#!/usr/bin/env python3
"""
HTTP Server wrapper for Home Assistant MCP Server
Exposes MCP functionality via REST API endpoints
"""

import asyncio
import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from aiohttp import web
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from homeassistant_mcp_server.server import HomeAssistantClient

class MCPHTTPServer:
    def __init__(self):
        """Initialize the HTTP server"""
        self.hass_url = os.getenv("HASS_URL", "http://localhost:8123")
        self.hass_token = os.getenv("HASS_TOKEN")
        self.port = int(os.getenv("MCP_SERVER_PORT", "3002"))
        self.host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
        
        # Setup logging
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)
        
        if not self.hass_token:
            raise ValueError("HASS_TOKEN environment variable required")
        
        self.logger.info("HTTP Server initialized")
        self.logger.info(f"Home Assistant URL: {self.hass_url}")
        self.logger.info(f"Server will bind to: {self.host}:{self.port}")

    @web.middleware
    async def cors_handler(self, request, handler):
        """CORS middleware for cross-origin requests"""
        if request.method == "OPTIONS":
            response = web.Response()
        else:
            response = await handler(request)
        
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response

    async def health_handler(self, request):
        """Health check endpoint"""
        try:
            # Test connection to Home Assistant
            async with HomeAssistantClient(self.hass_url, self.hass_token) as client:
                entities = await client.get_entities()
                entity_count = len(entities) if entities else 0
            
            return web.json_response({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "home_assistant": {
                    "url": self.hass_url,
                    "connected": True,
                    "entity_count": entity_count
                },
                "server": {
                    "host": self.host,
                    "port": self.port,
                    "version": "1.0.0"
                }
            })
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return web.json_response({
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "home_assistant": {
                    "url": self.hass_url,
                    "connected": False
                }
            }, status=500)

    async def get_entities_handler(self, request):
        """Get all entities or filter by domain"""
        try:
            domain = request.query.get("domain")
            async with HomeAssistantClient(self.hass_url, self.hass_token) as client:
                entities = await client.get_entities()
            
            if domain:
                entities = [e for e in entities if e.get("entity_id", "").startswith(f"{domain}.")]
            
            return web.json_response({
                "success": True,
                "count": len(entities),
                "entities": entities
            })
        except Exception as e:
            self.logger.error(f"Error getting entities: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def get_entity_handler(self, request):
        """Get specific entity state"""
        try:
            entity_id = request.match_info['entity_id']
            async with HomeAssistantClient(self.hass_url, self.hass_token) as client:
                entity = await client.get_entity_state(entity_id)
            
            if entity:
                return web.json_response({
                    "success": True,
                    "entity": entity
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": f"Entity {entity_id} not found"
                }, status=404)
                
        except Exception as e:
            self.logger.error(f"Error getting entity {entity_id}: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def call_service_handler(self, request):
        """Call a Home Assistant service"""
        try:
            data = await request.json()
            domain = data.get("domain")
            service = data.get("service")
            service_data = data.get("service_data", {})
            target = data.get("target")
            
            if not domain or not service:
                return web.json_response({
                    "success": False,
                    "error": "domain and service are required"
                }, status=400)
            
            async with HomeAssistantClient(self.hass_url, self.hass_token) as client:
                result = await client.call_service(domain, service, service_data, target)
            
            return web.json_response({
                "success": True,
                "result": result
            })
            
        except Exception as e:
            self.logger.error(f"Error calling service: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def get_history_handler(self, request):
        """Get entity history"""
        try:
            # Parse query parameters
            start_time = request.query.get("start_time")
            end_time = request.query.get("end_time")
            entity_id = request.query.get("entity_id")
            hours = request.query.get("hours", "24")
            
            async with HomeAssistantClient(self.hass_url, self.hass_token) as client:
                if entity_id:
                    # Get history for specific entity
                    history = await client.get_history(entity_id, int(hours))
                else:
                    # Get general history data (simplified)
                    entities = await client.get_entities()
                    history = [{"entity_id": e.get("entity_id"), "state": e.get("state")} for e in entities[:10]]
            
            return web.json_response({
                "success": True,
                "history": history
            })
            
        except Exception as e:
            self.logger.error(f"Error getting history: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    def create_app(self):
        """Create the aiohttp application"""
        app = web.Application(middlewares=[self.cors_handler])
        
        # Add routes
        app.router.add_get("/", self.health_handler)
        app.router.add_get("/health", self.health_handler)
        app.router.add_get("/api/entities", self.get_entities_handler)
        app.router.add_get("/api/entities/{entity_id}", self.get_entity_handler)
        app.router.add_post("/api/services/call", self.call_service_handler)
        app.router.add_get("/api/history", self.get_history_handler)
        
        return app

    async def start(self):
        """Start the HTTP server"""
        app = self.create_app()
        
        self.logger.info("🚀 Starting Home Assistant MCP HTTP Server")
        self.logger.info(f"📡 Server URL: http://{self.host}:{self.port}")
        self.logger.info(f"🏠 Home Assistant: {self.hass_url}")
        self.logger.info(f"🔗 Health check: http://{self.host}:{self.port}/health")
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        self.logger.info("✅ Server started successfully!")
        
        try:
            # Keep running
            while True:
                await asyncio.sleep(3600)  # Sleep for 1 hour
        except KeyboardInterrupt:
            self.logger.info("⏹️  Keyboard interrupt received")
        except Exception as e:
            self.logger.error(f"❌ Server error: {e}")
        finally:
            self.logger.info("🛑 Shutting down server...")
            await runner.cleanup()

def main():
    """Main entry point"""
    try:
        server = MCPHTTPServer()
        asyncio.run(server.start())
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file and ensure HASS_TOKEN is set")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()