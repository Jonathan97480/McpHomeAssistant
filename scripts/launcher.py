#!/usr/bin/env python3
"""
Home Assistant MCP Server Launcher
This script starts the MCP server with proper configuration and error handling.
"""

import os
import sys
import asyncio
import signal
import logging
from pathlib import Path
from typing import Optional

# Add the src directory to the Python path
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from homeassistant_mcp_server.server import main as mcp_main

# Configuration
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 3000
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class MCPServerLauncher:
    def __init__(self):
        self.server_task: Optional[asyncio.Task] = None
        self.setup_logging()
        self.setup_signal_handlers()
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_file = os.getenv("LOG_FILE")
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format=LOG_FORMAT,
            handlers=[
                logging.StreamHandler(sys.stdout),
                *([] if not log_file else [logging.FileHandler(log_file)])
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("MCP Server Launcher starting...")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down gracefully...")
            if self.server_task:
                self.server_task.cancel()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def validate_environment(self):
        """Validate required environment variables"""
        required_vars = ["HASS_URL", "HASS_TOKEN"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            self.logger.error("Please check your .env file or environment configuration")
            return False
        
        # Validate URLs
        hass_url = os.getenv("HASS_URL")
        if not (hass_url.startswith("http://") or hass_url.startswith("https://")):
            self.logger.error(f"Invalid HASS_URL format: {hass_url}")
            return False
        
        self.logger.info(f"Environment validation passed")
        self.logger.info(f"Home Assistant URL: {hass_url}")
        
        return True
    
    def get_server_config(self):
        """Get server configuration from environment"""
        return {
            "host": os.getenv("MCP_SERVER_HOST", DEFAULT_HOST),
            "port": int(os.getenv("MCP_SERVER_PORT", DEFAULT_PORT)),
        }
    
    async def run_server(self):
        """Run the MCP server"""
        try:
            if not self.validate_environment():
                return 1
            
            config = self.get_server_config()
            self.logger.info(f"Starting MCP server on {config['host']}:{config['port']}")
            
            # Start the MCP server
            self.server_task = asyncio.create_task(mcp_main())
            await self.server_task
            
        except asyncio.CancelledError:
            self.logger.info("Server shutdown requested")
            return 0
        except Exception as e:
            self.logger.error(f"Server error: {e}", exc_info=True)
            return 1
    
    def run(self):
        """Main entry point"""
        try:
            return asyncio.run(self.run_server())
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
            return 0
        except Exception as e:
            self.logger.error(f"Launcher error: {e}", exc_info=True)
            return 1

def main():
    """Main function"""
    launcher = MCPServerLauncher()
    exit_code = launcher.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()