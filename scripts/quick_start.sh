#!/bin/bash

# Quick Start Script for Home Assistant MCP HTTP Server
# ====================================================
# This script helps you quickly start the HTTP server for testing

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if .env file exists
check_env() {
    if [[ ! -f ".env" ]]; then
        warn "No .env file found. Creating from example..."
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
        else
            cat > .env << EOF
# Home Assistant Configuration
HASS_URL=http://localhost:8123
HASS_TOKEN=

# HTTP Server Settings  
HTTP_SERVER_HOST=0.0.0.0
HTTP_SERVER_PORT=3002

# Logging
LOG_LEVEL=INFO
EOF
        fi
        
        warn "Please edit .env and add your Home Assistant token!"
        info "Get a token from: Home Assistant > Profile > Long-lived access tokens"
        echo
        read -p "Press Enter to continue with .env configuration..."
        
        if command -v nano >/dev/null 2>&1; then
            nano .env
        elif command -v vim >/dev/null 2>&1; then
            vim .env
        else
            echo "Please edit .env manually with your preferred text editor"
        fi
    fi
}

# Check Python dependencies
check_dependencies() {
    log "Checking Python dependencies..."
    
    if ! python -c "import aiohttp" 2>/dev/null; then
        log "Installing required dependencies..."
        pip install aiohttp python-dotenv aiofiles
    fi
    
    if ! python -c "import homeassistant_mcp_server" 2>/dev/null; then
        log "Installing MCP server..."
        pip install -e .
    fi
}

# Start the HTTP server
start_server() {
    log "Starting HTTP server..."
    info "Server will be available at: http://localhost:3002"
    info "Health check: http://localhost:3002/health"
    echo
    info "Press Ctrl+C to stop the server"
    echo
    
    python http_server.py
}

# Main function
main() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "  Home Assistant MCP HTTP Server"
    echo "       Quick Start Script"
    echo "=========================================="
    echo -e "${NC}"
    
    # Check if http_server.py exists
    if [[ ! -f "http_server.py" ]]; then
        error "http_server.py not found in current directory"
        error "Please run this script from the project root directory"
        exit 1
    fi
    
    check_env
    check_dependencies
    start_server
}

# Run main function
main "$@"