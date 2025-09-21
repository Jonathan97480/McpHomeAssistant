#!/usr/bin/env python3
"""
🌉 HTTP-MCP Bridge Server
FastAPI server that exposes MCP protocol via REST endpoints with queue management
"""

import asyncio
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import MCP components
import sys
import os

# Ajouter le chemin pour importer notre serveur MCP
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import du système de base de données
from database import db_manager, log_manager, setup_database, cleanup_old_data_task, LogEntry, RequestEntry, ErrorEntry

# Variables globales pour le serveur MCP
mcp_server = None
ha_client = None

async def initialize_mcp_server():
    """Initialise le serveur MCP et le client Home Assistant"""
    global mcp_server, ha_client
    
    try:
        # Importer les modules MCP
        from src.homeassistant_mcp_server.server import HomeAssistantClient
        from mcp.server import Server
        from dotenv import load_dotenv
        
        # Charger l'environnement
        load_dotenv()
        
        # Configuration
        HASS_URL = os.getenv("HASS_URL", "http://192.168.1.22:8123")
        HASS_TOKEN = os.getenv("HASS_TOKEN")
        
        if not HASS_TOKEN:
            raise ValueError("HASS_TOKEN environment variable required")
        
        # Créer le client Home Assistant
        ha_client = HomeAssistantClient(HASS_URL, HASS_TOKEN)
        
        # Créer le serveur MCP (pour l'instant une version simplifiée)
        mcp_server = Server("homeassistant-mcp-server")
        
        logging.info("✅ MCP Server initialized successfully")
        return True
        
    except Exception as e:
        logging.error(f"❌ Failed to initialize MCP server: {e}")
        return False


class MockMCPServer:
    """Serveur MCP de test pour le développement"""
    
    async def list_tools(self):
        """Retourne une liste d'outils simulés"""
        return {
            "tools": [
                {
                    "name": "get_entities",
                    "description": "Récupère la liste de toutes les entités Home Assistant",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Filtrer par domaine (optionnel)"
                            }
                        }
                    }
                },
                {
                    "name": "call_service", 
                    "description": "Appelle un service Home Assistant",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "domain": {"type": "string"},
                            "service": {"type": "string"},
                            "entity_id": {"type": "string"},
                            "data": {"type": "object"}
                        },
                        "required": ["domain", "service"]
                    }
                }
            ]
        }
    
    async def call_tool(self, name: str, args: Dict[str, Any]):
        """Exécute un outil simulé"""
        if name == "get_entities":
            domain = args.get("domain", "all")
            return {
                "content": [{
                    "type": "text", 
                    "text": f"🔧 Mock: Récupération des entités pour le domaine '{domain}'\n\nEntités simulées:\n- light.salon_lamp (état: off)\n- sensor.temperature (état: 22.5°C)\n- switch.tv (état: on)"
                }],
                "isError": False
            }
        elif name == "call_service":
            domain = args.get("domain")
            service = args.get("service") 
            entity_id = args.get("entity_id")
            return {
                "content": [{
                    "type": "text",
                    "text": f"🔧 Mock: Service {domain}.{service} appelé sur {entity_id}"
                }],
                "isError": False
            }
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"❌ Outil inconnu: {name}"
                }],
                "isError": True
            }


# 📊 Models et Types
class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM" 
    LOW = "LOW"
    BULK = "BULK"


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


@dataclass
class QueuedRequest:
    """Représente une requête en file d'attente"""
    id: str
    session_id: str
    method: str
    params: Dict[str, Any]
    priority: Priority
    created_at: datetime
    timeout_seconds: int = 30
    status: RequestStatus = RequestStatus.PENDING
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.created_at + timedelta(seconds=self.timeout_seconds)


@dataclass 
class MCPSession:
    """Représente une session MCP active"""
    id: str
    server: Any  # MCP Server instance
    created_at: datetime
    last_used: datetime
    is_healthy: bool = True
    request_count: int = 0
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.last_used + timedelta(minutes=30)


# 🎯 Pydantic Models pour API
class InitializeRequest(BaseModel):
    protocolVersion: str = "2024-11-05"
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    clientInfo: Dict[str, str] = Field(default_factory=lambda: {"name": "http-client", "version": "1.0"})
    session_id: Optional[str] = None


class ToolCallRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int] = 1
    method: str = "tools/call"
    params: Dict[str, Any]


class ToolListRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int] = 2
    method: str = "tools/list"
    params: Dict[str, Any] = Field(default_factory=dict)


# 🔄 AsyncRequestQueue - Gestion des files d'attente
class AsyncRequestQueue:
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.queues = {
            Priority.HIGH: asyncio.Queue(),
            Priority.MEDIUM: asyncio.Queue(), 
            Priority.LOW: asyncio.Queue(),
            Priority.BULK: asyncio.Queue()
        }
        self.processing: Dict[str, QueuedRequest] = {}
        self.completed: Dict[str, QueuedRequest] = {}
        self.stats = {
            "total_requests": 0,
            "completed_requests": 0,
            "failed_requests": 0,
            "avg_processing_time": 0.0
        }
        self._processor_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Démarre le processeur de queue"""
        if self._processor_task is None:
            self._processor_task = asyncio.create_task(self._process_queue())
            logging.info("🔄 AsyncRequestQueue started")
    
    async def stop(self):
        """Arrête le processeur de queue"""
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
            self._processor_task = None
            logging.info("🛑 AsyncRequestQueue stopped")
    
    async def enqueue(self, request: QueuedRequest) -> str:
        """Ajoute une requête à la queue"""
        await self.queues[request.priority].put(request)
        self.stats["total_requests"] += 1
        logging.info(f"📥 Request {request.id} queued with priority {request.priority}")
        return request.id
    
    async def get_result(self, request_id: str, timeout: float = 30.0) -> QueuedRequest:
        """Attend et retourne le résultat d'une requête"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Vérifier si completed
            if request_id in self.completed:
                return self.completed[request_id]
            
            # Vérifier si en cours
            if request_id in self.processing:
                await asyncio.sleep(0.1)
                continue
                
            # Vérifier dans les queues
            await asyncio.sleep(0.1)
        
        raise HTTPException(status_code=408, detail=f"Request {request_id} timeout")
    
    async def _process_queue(self):
        """Processeur principal de la queue"""
        while True:
            try:
                # Traiter par priorité: HIGH > MEDIUM > LOW > BULK
                for priority in [Priority.HIGH, Priority.MEDIUM, Priority.LOW, Priority.BULK]:
                    if len(self.processing) >= self.max_concurrent:
                        break
                        
                    try:
                        request = self.queues[priority].get_nowait()
                        if not request.is_expired:
                            asyncio.create_task(self._execute_request(request))
                        else:
                            logging.warning(f"⏰ Request {request.id} expired before processing")
                    except asyncio.QueueEmpty:
                        continue
                
                await asyncio.sleep(0.01)  # Éviter CPU spinning
                
            except Exception as e:
                logging.error(f"❌ Queue processor error: {e}")
                await asyncio.sleep(1)
    
    async def _execute_request(self, request: QueuedRequest):
        """Exécute une requête MCP"""
        start_time = time.time()
        request.status = RequestStatus.PROCESSING
        self.processing[request.id] = request
        
        try:
            # Récupérer la session MCP
            session = session_pool.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Exécuter la méthode MCP
            if request.method == "tools/list":
                result = await session.server.list_tools()
            elif request.method == "tools/call":
                tool_name = request.params.get("name")
                tool_args = request.params.get("arguments", {})
                result = await session.server.call_tool(tool_name, tool_args)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")
            
            # Stocker le résultat
            request.result = result
            request.status = RequestStatus.COMPLETED
            session.last_used = datetime.now()
            session.request_count += 1
            
            # Statistiques
            processing_time = time.time() - start_time
            self.stats["completed_requests"] += 1
            self.stats["avg_processing_time"] = (
                (self.stats["avg_processing_time"] * (self.stats["completed_requests"] - 1) + processing_time) 
                / self.stats["completed_requests"]
            )
            
            logging.info(f"✅ Request {request.id} completed in {processing_time:.3f}s")
            
        except Exception as e:
            request.error = {
                "code": -32603,
                "message": str(e),
                "data": {"request_id": request.id}
            }
            request.status = RequestStatus.FAILED
            self.stats["failed_requests"] += 1
            logging.error(f"❌ Request {request.id} failed: {e}")
        
        finally:
            # Déplacer vers completed et nettoyer processing
            self.completed[request.id] = request
            if request.id in self.processing:
                del self.processing[request.id]
            
            # Cleanup ancien completed (garder dernières 1000)
            if len(self.completed) > 1000:
                old_ids = sorted(self.completed.keys())[:500]
                for old_id in old_ids:
                    del self.completed[old_id]
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de la queue"""
        total_queued = sum(q.qsize() for q in self.queues.values())
        return {
            "pending": total_queued,
            "processing": len(self.processing),
            "by_priority": {p.value: self.queues[p].qsize() for p in Priority},
            "stats": self.stats,
            "max_concurrent": self.max_concurrent
        }


# 🏊 MCPSessionPool - Gestion du pool de sessions
class MCPSessionPool:
    def __init__(self, max_sessions: int = 10):
        self.max_sessions = max_sessions
        self.sessions: Dict[str, MCPSession] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Démarre le nettoyage automatique des sessions"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_sessions())
            logging.info("🏊 MCPSessionPool started")
    
    async def stop(self):
        """Arrête le pool de sessions"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
        
        # Fermer toutes les sessions
        for session in self.sessions.values():
            try:
                await session.server.close()
            except:
                pass
        self.sessions.clear()
        logging.info("🛑 MCPSessionPool stopped")
    
    async def create_session(self, session_id: Optional[str] = None) -> MCPSession:
        """Crée une nouvelle session MCP"""
        if len(self.sessions) >= self.max_sessions:
            # Nettoyer les sessions expirées ou inactives
            await self._cleanup_expired()
            if len(self.sessions) >= self.max_sessions:
                raise HTTPException(status_code=503, detail="No MCP sessions available")
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Créer le serveur MCP
        if mcp_server is None:
            await initialize_mcp_server()
        
        # Utiliser le mock server pour les tests
        mock_server = MockMCPServer()
        
        session = MCPSession(
            id=session_id,
            server=mock_server,  # Utiliser le mock pour les tests
            created_at=datetime.now(),
            last_used=datetime.now()
        )
        
        self.sessions[session_id] = session
        logging.info(f"🆕 Created MCP session {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[MCPSession]:
        """Récupère une session existante"""
        return self.sessions.get(session_id)
    
    async def _cleanup_sessions(self):
        """Nettoyage périodique des sessions expirées"""
        while True:
            try:
                await self._cleanup_expired()
                await asyncio.sleep(60)  # Cleanup toutes les minutes
            except Exception as e:
                logging.error(f"❌ Session cleanup error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired(self):
        """Supprime les sessions expirées"""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired
        ]
        
        for session_id in expired_sessions:
            session = self.sessions[session_id]
            try:
                await session.server.close()
            except:
                pass
            del self.sessions[session_id]
            logging.info(f"🗑️ Cleaned up expired session {session_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du pool"""
        healthy_count = sum(1 for s in self.sessions.values() if s.is_healthy)
        return {
            "total": len(self.sessions),
            "healthy": healthy_count,
            "max_sessions": self.max_sessions,
            "by_status": {
                "healthy": healthy_count,
                "unhealthy": len(self.sessions) - healthy_count
            }
        }


# 🌐 Instances globales
request_queue = AsyncRequestQueue(max_concurrent=5)
session_pool = MCPSessionPool(max_sessions=10)


# 🚀 Lifecycle Management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("🚀 Starting HTTP-MCP Bridge Server...")
    
    # Initialiser la base de données
    await setup_database()
    
    # Démarrer les composants
    await request_queue.start()
    await session_pool.start()
    
    # Démarrer la tâche de nettoyage automatique
    cleanup_task = asyncio.create_task(cleanup_old_data_task())
    
    yield
    
    # Shutdown
    logging.info("🛑 Shutting down HTTP-MCP Bridge Server...")
    
    # Arrêter la tâche de nettoyage
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    
    # Arrêter les composants
    await request_queue.stop()
    await session_pool.stop()
    
    # Fermer la base de données
    await db_manager.close()


# 🌐 FastAPI App
app = FastAPI(
    title="HTTP-MCP Bridge",
    description="Bridge HTTP REST API to MCP Protocol with queue management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📝 Logging setup avec rotation journalière
class DatabaseLogHandler(logging.Handler):
    """Handler personnalisé pour envoyer les logs vers la base de données"""
    
    def emit(self, record):
        try:
            # Créer l'entrée de log
            log_entry = LogEntry(
                timestamp=datetime.fromtimestamp(record.created).isoformat(),
                level=record.levelname,
                message=record.getMessage(),
                module=record.name,
                extra_data=json.dumps({
                    "filename": record.filename,
                    "lineno": record.lineno,
                    "funcName": record.funcName
                }) if hasattr(record, 'filename') else None
            )
            
            # Insérer de manière asynchrone (dans un thread séparé pour éviter les blocages)
            asyncio.create_task(db_manager.insert_log(log_entry))
            
        except Exception:
            # Éviter les boucles infinies en cas d'erreur du logger
            pass

# Configuration du logging
def setup_logging():
    """Configure le système de logging avec rotation et base de données"""
    
    # Logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Formateur
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler pour fichier journalier
    file_handler = logging.FileHandler(
        log_manager.get_current_log_file(),
        mode='a',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Handler pour console  
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Handler pour base de données
    db_handler = DatabaseLogHandler()
    db_handler.setLevel(logging.WARNING)  # Seulement les warnings et erreurs en BDD
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(db_handler)
    
    return logger

# Initialiser le logging
logger = setup_logging()


# 🛠️ Dependencies
async def get_session_id(x_session_id: Optional[str] = Header(None)) -> Optional[str]:
    return x_session_id

async def get_priority(x_priority: Optional[str] = Header("MEDIUM")) -> Priority:
    try:
        return Priority(x_priority.upper())
    except (ValueError, AttributeError):
        return Priority.MEDIUM

async def get_timeout(x_timeout: Optional[int] = Header(30)) -> int:
    return max(1, min(x_timeout or 30, 300))  # Limite entre 1 et 300 secondes

async def log_request(request: Request, response_time_ms: int, status_code: int, session_id: Optional[str] = None):
    """Log une requête utilisateur dans la base de données"""
    try:
        request_entry = RequestEntry(
            timestamp=datetime.now().isoformat(),
            session_id=session_id or "anonymous",
            method=request.method,
            endpoint=str(request.url.path),
            params=json.dumps(dict(request.query_params)) if request.query_params else "{}",
            response_time_ms=response_time_ms,
            status_code=status_code,
            user_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        await db_manager.insert_request(request_entry)
        
    except Exception as e:
        logger.warning(f"⚠️ Erreur log requête: {e}")

async def log_error(error_type: str, error_message: str, stack_trace: str = None, session_id: str = None, context: Dict = None):
    """Log une erreur dans la base de données"""
    try:
        error_entry = ErrorEntry(
            timestamp=datetime.now().isoformat(),
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            session_id=session_id,
            context=json.dumps(context) if context else None
        )
        
        await db_manager.insert_error(error_entry)
        
    except Exception as e:
        logger.warning(f"⚠️ Erreur log erreur: {e}")


# 🌐 Routes API
@app.post("/mcp/initialize")
async def initialize_session(request_data: InitializeRequest, request: Request):
    """Initialise une nouvelle session MCP"""
    start_time = time.time()
    status_code = 200
    
    try:
        session = await session_pool.create_session(request_data.session_id)
        
        response_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": request_data.protocolVersion,
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": "homeassistant-mcp-server",
                    "version": "1.0.0"
                },
                "session_id": session.id,
                "expires_at": (session.created_at + timedelta(hours=1)).isoformat()
            },
            "bridge_info": {
                "queue_position": 0,
                "estimated_wait_ms": 0
            }
        }
        
        # Log de la requête
        response_time_ms = int((time.time() - start_time) * 1000)
        await log_request(request, response_time_ms, status_code, session.id)
        
        return JSONResponse(response_data)
    
    except HTTPException as e:
        status_code = e.status_code
        await log_error("HTTPException", str(e.detail), session_id=None, context={"endpoint": "/mcp/initialize"})
        raise
    except Exception as e:
        status_code = 500
        logger.error(f"Initialize error: {e}")
        await log_error("InternalError", str(e), session_id=None, context={"endpoint": "/mcp/initialize"})
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if status_code != 200:
            response_time_ms = int((time.time() - start_time) * 1000)
            await log_request(request, response_time_ms, status_code)


@app.post("/mcp/tools/list")
async def list_tools(
    request: ToolListRequest,
    session_id: str = Depends(get_session_id),
    priority: Priority = Depends(get_priority),
    timeout: int = Depends(get_timeout)
):
    """Liste tous les outils MCP disponibles"""
    if not session_id:
        raise HTTPException(status_code=400, detail="X-Session-ID header required")
    
    # Créer la requête en queue
    queued_request = QueuedRequest(
        id=str(uuid.uuid4()),
        session_id=session_id,
        method="tools/list",
        params=request.params,
        priority=priority,
        created_at=datetime.now(),
        timeout_seconds=timeout
    )
    
    # Ajouter à la queue
    await request_queue.enqueue(queued_request)
    
    # Attendre le résultat
    result = await request_queue.get_result(queued_request.id, timeout)
    
    if result.status == RequestStatus.FAILED:
        raise HTTPException(status_code=500, detail=result.error)
    
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": request.id,
        "result": result.result,
        "bridge_info": {
            "cached": False,
            "execution_time_ms": int((datetime.now() - result.created_at).total_seconds() * 1000)
        }
    })


@app.post("/mcp/tools/call")
async def call_tool(
    request_data: ToolCallRequest,
    request: Request,
    session_id: str = Depends(get_session_id),
    priority: Priority = Depends(get_priority),
    timeout: int = Depends(get_timeout)
):
    """Exécute un outil MCP spécifique"""
    start_time = time.time()
    status_code = 200
    
    try:
        if not session_id:
            raise HTTPException(status_code=400, detail="X-Session-ID header required")
        
        # Créer la requête en queue
        queued_request = QueuedRequest(
            id=str(uuid.uuid4()),
            session_id=session_id,
            method="tools/call",
            params=request_data.params,
            priority=priority,
            created_at=datetime.now(),
            timeout_seconds=timeout
        )
        
        # Ajouter à la queue
        await request_queue.enqueue(queued_request)
        
        # Attendre le résultat
        result = await request_queue.get_result(queued_request.id, timeout)
        
        if result.status == RequestStatus.FAILED:
            status_code = 500
            await log_error("ToolExecutionError", str(result.error), session_id=session_id, context={"tool": request_data.params.get("name"), "params": request_data.params})
            raise HTTPException(status_code=500, detail=result.error)
        
        response_data = {
            "jsonrpc": "2.0",
            "id": request_data.id,
            "result": result.result,
            "bridge_info": {
                "execution_time_ms": int((datetime.now() - result.created_at).total_seconds() * 1000),
                "session_id": session_id,
                "cached": False
            }
        }
        
        # Log de la requête
        response_time_ms = int((time.time() - start_time) * 1000)
        await log_request(request, response_time_ms, status_code, session_id)
        
        return JSONResponse(response_data)
        
    except HTTPException as e:
        status_code = e.status_code
        await log_error("HTTPException", str(e.detail), session_id=session_id, context={"endpoint": "/mcp/tools/call"})
        raise
    except Exception as e:
        status_code = 500
        await log_error("InternalError", str(e), session_id=session_id, context={"endpoint": "/mcp/tools/call"})
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if status_code != 200:
            response_time_ms = int((time.time() - start_time) * 1000)
            await log_request(request, response_time_ms, status_code, session_id)


@app.get("/mcp/status")
async def bridge_status():
    """Statut complet du bridge"""
    return JSONResponse({
        "bridge": {
            "status": "healthy",
            "version": "1.0.0",
            "started_at": datetime.now().isoformat()
        },
        "sessions": session_pool.get_status(),
        "queue": request_queue.get_status(),
        "home_assistant": {
            "url": "http://192.168.1.22:8123",
            "status": "connected"
        }
    })


@app.get("/health")
async def health_check():
    """Health check simple"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


@app.get("/admin/stats")
async def get_statistics(days: int = 7):
    """Récupère les statistiques détaillées du bridge"""
    try:
        stats = await db_manager.get_stats(days=days)
        return JSONResponse({
            "status": "success",
            "data": stats
        })
    except Exception as e:
        logger.error(f"Erreur récupération stats: {e}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


@app.post("/admin/cleanup")
async def manual_cleanup(days_to_keep: int = 30):
    """Lance un nettoyage manuel des données anciennes"""
    try:
        result = await db_manager.cleanup_old_data(days_to_keep=days_to_keep)
        return JSONResponse({
            "status": "success",
            "data": result
        })
    except Exception as e:
        logger.error(f"Erreur nettoyage manuel: {e}")
        return JSONResponse({
            "status": "error", 
            "message": str(e)
        }, status_code=500)


@app.get("/admin/logs/rotate")
async def manual_log_rotation():
    """Force la rotation des logs manuellement"""
    try:
        await log_manager.rotate_logs_if_needed()
        return JSONResponse({
            "status": "success",
            "message": "Log rotation completed",
            "current_log_file": str(log_manager.get_current_log_file())
        })
    except Exception as e:
        logger.error(f"Erreur rotation logs: {e}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)


if __name__ == "__main__":
    uvicorn.run(
        "bridge_server:app",
        host="0.0.0.0",
        port=3003,
        reload=False,  # Désactiver reload pour éviter les conflits
        log_level="info"
    )