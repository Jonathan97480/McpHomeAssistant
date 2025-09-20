"""
Home Assistant MCP Server

Serveur Model Context Protocol pour intégrer Home Assistant avec des agents IA.
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import aiohttp
from dotenv import load_dotenv

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# Chargement des variables d'environnement
load_dotenv()

class HomeAssistantClient:
    """Client pour l'API Home Assistant"""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_entities(self) -> List[Dict[str, Any]]:
        """Récupère toutes les entités"""
        if not self.session:
            raise RuntimeError("Client non initialisé")
        
        async with self.session.get(f"{self.base_url}/api/states") as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_entity_state(self, entity_id: str) -> Dict[str, Any]:
        """Récupère l'état d'une entité spécifique"""
        if not self.session:
            raise RuntimeError("Client non initialisé")
        
        async with self.session.get(f"{self.base_url}/api/states/{entity_id}") as response:
            response.raise_for_status()
            return await response.json()
    
    async def call_service(self, domain: str, service: str, entity_id: Optional[str] = None, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Appelle un service Home Assistant"""
        if not self.session:
            raise RuntimeError("Client non initialisé")
        
        service_data = data or {}
        if entity_id:
            service_data["entity_id"] = entity_id
        
        async with self.session.post(
            f"{self.base_url}/api/services/{domain}/{service}",
            json=service_data
        ) as response:
            response.raise_for_status()
            return await response.json() if response.content_type == 'application/json' else {}
    
    async def get_history(self, entity_id: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Récupère l'historique d'une entité"""
        if not self.session:
            raise RuntimeError("Client non initialisé")
        
        if not start_time:
            start_time = datetime.now() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.now()
        
        params = {
            "filter_entity_id": entity_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
        async with self.session.get(f"{self.base_url}/api/history/period", params=params) as response:
            response.raise_for_status()
            history_data = await response.json()
            return history_data[0] if history_data else []
    
    async def get_services(self) -> Dict[str, Any]:
        """Récupère la liste des services disponibles"""
        if not self.session:
            raise RuntimeError("Client non initialisé")
        
        async with self.session.get(f"{self.base_url}/api/services") as response:
            response.raise_for_status()
            return await response.json()
    
    async def create_automation(self, automation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une nouvelle automatisation via le service automation"""
        if not self.session:
            raise RuntimeError("Client non initialisé")
        
        # Validation basique des données d'automatisation
        if "trigger" not in automation_data:
            raise ValueError("L'automatisation doit contenir un déclencheur (trigger)")
        if "action" not in automation_data:
            raise ValueError("L'automatisation doit contenir une action")
        
        # Utiliser le service automation.create au lieu de l'API config
        # Note: Cela nécessite que l'automatisation soit ajoutée au fichier YAML
        try:
            # Essayer d'abord de créer via l'API config (si disponible)
            async with self.session.post(
                f"{self.base_url}/api/config/automation/config",
                json=automation_data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    # Fallback: retourner les données comme si elles étaient créées
                    # L'utilisateur devra ajouter manuellement au fichier automations.yaml
                    raise Exception(f"API config non disponible (Status: {response.status})")
                    
        except Exception as e:
            # Alternative: retourner les données YAML que l'utilisateur peut copier
            import yaml
            yaml_content = yaml.dump([automation_data], default_flow_style=False, allow_unicode=True)
            
            return {
                "status": "yaml_generated",
                "message": "L'automatisation ne peut pas être créée directement via l'API. Ajoutez ce contenu à votre fichier automations.yaml:",
                "yaml_content": yaml_content,
                "automation_data": automation_data
            }
    
    async def list_automations(self) -> List[Dict[str, Any]]:
        """Liste toutes les automatisations"""
        if not self.session:
            raise RuntimeError("Client non initialisé")
        
        # Récupérer les entités automation depuis /api/states
        async with self.session.get(f"{self.base_url}/api/states") as response:
            response.raise_for_status()
            states = await response.json()
            
            # Filtrer les entités automation
            automations = [
                entity for entity in states 
                if entity.get("entity_id", "").startswith("automation.")
            ]
            
            return automations
    
    async def delete_automation(self, automation_id: str) -> bool:
        """Supprime une automatisation (ou la désactive)"""
        if not self.session:
            raise RuntimeError("Client non initialisé")
        
        try:
            # Essayer de désactiver l'automatisation au lieu de la supprimer
            entity_id = automation_id if automation_id.startswith("automation.") else f"automation.{automation_id}"
            
            await self.call_service("automation", "turn_off", entity_id)
            return True
            
        except Exception as e:
            raise Exception(f"Impossible de désactiver l'automatisation {automation_id}: {e}")
            
    async def toggle_automation(self, automation_id: str, enable: bool = True) -> Dict[str, Any]:
        """Active ou désactive une automatisation"""
        if not self.session:
            raise RuntimeError("Client non initialisé")
        
        entity_id = automation_id if automation_id.startswith("automation.") else f"automation.{automation_id}"
        service = "turn_on" if enable else "turn_off"
        
        result = await self.call_service("automation", service, entity_id)
        
        return {
            "entity_id": entity_id,
            "action": "enabled" if enable else "disabled",
            "result": result
        }

# Configuration
HASS_URL = os.getenv("HASS_URL", "http://localhost:8123")
HASS_TOKEN = os.getenv("HASS_TOKEN", "")

if not HASS_TOKEN:
    print("Erreur: HASS_TOKEN requis dans les variables d'environnement")
    sys.exit(1)

# Initialisation du serveur MCP
server = Server("homeassistant-mcp-server")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """Liste des outils disponibles"""
    return [
        Tool(
            name="get_entities",
            description="Récupère la liste de toutes les entités Home Assistant avec leurs états",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Filtrer par domaine (optionnel): light, switch, sensor, etc."
                    }
                }
            }
        ),
        Tool(
            name="get_entity_state", 
            description="Récupère l'état détaillé d'une entité spécifique",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "ID de l'entité (ex: light.salon_lamp)"
                    }
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="call_service",
            description="Appelle un service Home Assistant pour contrôler des appareils",
            inputSchema={
                "type": "object", 
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domaine du service (ex: light, switch)"
                    },
                    "service": {
                        "type": "string", 
                        "description": "Service à appeler (ex: turn_on, turn_off)"
                    },
                    "entity_id": {
                        "type": "string",
                        "description": "ID de l'entité cible (optionnel)"
                    },
                    "data": {
                        "type": "object",
                        "description": "Données additionnelles pour le service (optionnel)"
                    }
                },
                "required": ["domain", "service"]
            }
        ),
        Tool(
            name="get_history",
            description="Récupère l'historique d'une entité",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "ID de l'entité"
                    },
                    "hours": {
                        "type": "number",
                        "description": "Nombre d'heures d'historique (défaut: 24)",
                        "default": 24
                    }
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="get_services",
            description="Récupère la liste de tous les services disponibles dans Home Assistant",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="create_automation",
            description="Génère une automatisation Home Assistant (YAML) prête à être ajoutée",
            inputSchema={
                "type": "object",
                "properties": {
                    "alias": {
                        "type": "string",
                        "description": "Nom de l'automatisation"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description de l'automatisation (optionnel)"
                    },
                    "trigger": {
                        "type": "array",
                        "description": "Liste des déclencheurs",
                        "items": {
                            "type": "object",
                            "properties": {
                                "platform": {
                                    "type": "string",
                                    "description": "Type de déclencheur (time, state, sun, numeric_state, etc.)"
                                }
                            }
                        }
                    },
                    "condition": {
                        "type": "array",
                        "description": "Liste des conditions (optionnel)",
                        "items": {
                            "type": "object"
                        }
                    },
                    "action": {
                        "type": "array",
                        "description": "Liste des actions à exécuter",
                        "items": {
                            "type": "object",
                            "properties": {
                                "service": {
                                    "type": "string",
                                    "description": "Service à appeler"
                                },
                                "entity_id": {
                                    "type": "string",
                                    "description": "Entité cible"
                                }
                            }
                        }
                    }
                },
                "required": ["alias", "trigger", "action"]
            }
        ),
        Tool(
            name="list_automations",
            description="Liste toutes les automatisations Home Assistant actives",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="toggle_automation",
            description="Active ou désactive une automatisation Home Assistant",
            inputSchema={
                "type": "object",
                "properties": {
                    "automation_id": {
                        "type": "string",
                        "description": "ID de l'automatisation (ex: automation.my_automation)"
                    },
                    "enable": {
                        "type": "boolean",
                        "description": "true pour activer, false pour désactiver"
                    }
                },
                "required": ["automation_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Gestionnaire des appels d'outils"""
    
    async with HomeAssistantClient(HASS_URL, HASS_TOKEN) as client:
        try:
            if name == "get_entities":
                entities = await client.get_entities()
                domain_filter = arguments.get("domain")
                
                if domain_filter:
                    entities = [e for e in entities if e["entity_id"].startswith(f"{domain_filter}.")]
                
                result = {
                    "total": len(entities),
                    "entities": [
                        {
                            "entity_id": e["entity_id"],
                            "state": e["state"],
                            "friendly_name": e["attributes"].get("friendly_name", e["entity_id"]),
                            "last_updated": e["last_updated"]
                        }
                        for e in entities[:50]  # Limite pour éviter les réponses trop longues
                    ]
                }
                
                return [types.TextContent(
                    type="text",
                    text=f"Trouvé {result['total']} entités:\n\n" +
                         json.dumps(result, indent=2, ensure_ascii=False)
                )]
            
            elif name == "get_entity_state":
                entity_id = arguments["entity_id"]
                entity = await client.get_entity_state(entity_id)
                
                return [types.TextContent(
                    type="text", 
                    text=json.dumps(entity, indent=2, ensure_ascii=False)
                )]
            
            elif name == "call_service":
                domain = arguments["domain"]
                service = arguments["service"]
                entity_id = arguments.get("entity_id")
                data = arguments.get("data", {})
                
                result = await client.call_service(domain, service, entity_id, data)
                
                return [types.TextContent(
                    type="text",
                    text=f"Service {domain}.{service} appelé avec succès.\n" +
                         f"Réponse: {json.dumps(result, indent=2, ensure_ascii=False)}"
                )]
            
            elif name == "get_history":
                entity_id = arguments["entity_id"]
                hours = arguments.get("hours", 24)
                
                start_time = datetime.now() - timedelta(hours=hours)
                history = await client.get_history(entity_id, start_time)
                
                return [types.TextContent(
                    type="text",
                    text=f"Historique de {entity_id} ({hours}h):\n\n" +
                         json.dumps(history, indent=2, ensure_ascii=False)
                )]
            
            elif name == "get_services":
                services = await client.get_services()
                
                # Simplifier la sortie pour la lisibilité
                simplified = {}
                for domain, domain_services in services.items():
                    simplified[domain] = list(domain_services.keys())
                
                return [types.TextContent(
                    type="text",
                    text=f"Services disponibles:\n\n" +
                         json.dumps(simplified, indent=2, ensure_ascii=False)
                )]
            
            elif name == "create_automation":
                automation_data = {
                    "alias": arguments["alias"],
                    "trigger": arguments["trigger"],
                    "action": arguments["action"]
                }
                
                # Ajouter description si fournie
                if "description" in arguments:
                    automation_data["description"] = arguments["description"]
                
                # Ajouter conditions si fournies
                if "condition" in arguments:
                    automation_data["condition"] = arguments["condition"]
                
                result = await client.create_automation(automation_data)
                
                if result.get("status") == "yaml_generated":
                    return [types.TextContent(
                        type="text",
                        text=f"Automatisation '{arguments['alias']}' générée!\n\n" +
                             f"⚠️ {result['message']}\n\n" +
                             f"```yaml\n{result['yaml_content']}```\n\n" +
                             "Copiez ce contenu dans votre fichier automations.yaml et redémarrez Home Assistant."
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Automatisation '{arguments['alias']}' créée avec succès!\n\n" +
                             json.dumps(result, indent=2, ensure_ascii=False)
                    )]
            
            elif name == "list_automations":
                automations = await client.list_automations()
                
                if not automations:
                    return [types.TextContent(
                        type="text",
                        text="Aucune automatisation trouvée.\n\n" +
                             "💡 Pour créer des automatisations:\n" +
                             "1. Utilisez l'outil 'create_automation' pour générer le YAML\n" +
                             "2. Ajoutez le contenu à votre fichier automations.yaml\n" +
                             "3. Redémarrez Home Assistant ou appelez automation.reload"
                    )]
                
                # Simplifier l'affichage
                simplified = []
                for auto in automations:
                    attributes = auto.get("attributes", {})
                    simplified.append({
                        "entity_id": auto.get("entity_id"),
                        "state": auto.get("state"),
                        "friendly_name": attributes.get("friendly_name", auto.get("entity_id")),
                        "last_triggered": attributes.get("last_triggered"),
                        "mode": attributes.get("mode", "single")
                    })
                
                return [types.TextContent(
                    type="text",
                    text=f"Trouvé {len(automations)} automatisations:\n\n" +
                         json.dumps(simplified, indent=2, ensure_ascii=False)
                )]
            
            elif name == "toggle_automation":
                automation_id = arguments["automation_id"]
                enable = arguments.get("enable", True)
                
                result = await client.toggle_automation(automation_id, enable)
                action = "activée" if enable else "désactivée"
                
                return [types.TextContent(
                    type="text",
                    text=f"Automatisation {result['entity_id']} {action} avec succès!\n\n" +
                         json.dumps(result, indent=2, ensure_ascii=False)
                )]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Outil inconnu: {name}"
                )]
                
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Erreur lors de l'exécution de {name}: {str(e)}"
            )]

async def main():
    """Point d'entrée principal"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="homeassistant-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())