#!/bin/bash

# Raspberry Pi Installation Verification Script
# =============================================
# This script checks if the MCP HTTP server is properly installed and running

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[✓] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[!] $1${NC}"
}

error() {
    echo -e "${RED}[✗] $1${NC}"
}

info() {
    echo -e "${BLUE}[i] $1${NC}"
}

# Configuration
INSTALL_DIR="/opt/homeassistant-mcp-server"
SERVICE_NAME="homeassistant-mcp-server"
HTTP_PORT=3002

echo -e "${BLUE}"
echo "================================================"
echo "  Home Assistant MCP Server - System Check"
echo "================================================"
echo -e "${NC}"

# Check if installation directory exists
if [[ -d "$INSTALL_DIR" ]]; then
    log "Installation directory found: $INSTALL_DIR"
else
    error "Installation directory not found: $INSTALL_DIR"
    exit 1
fi

# Check if files exist
cd "$INSTALL_DIR"

if [[ -f "http_server.py" ]]; then
    log "HTTP server file found"
else
    error "HTTP server file missing"
fi

if [[ -f ".env" ]]; then
    log "Configuration file found"
    
    # Check if token is configured
    if grep -q "HASS_TOKEN=$" .env; then
        warn "Home Assistant token not configured in .env"
        info "Edit $INSTALL_DIR/.env and add your token"
    else
        log "Home Assistant token configured"
    fi
else
    error "Configuration file missing"
fi

if [[ -d "venv" ]]; then
    log "Python virtual environment found"
else
    error "Python virtual environment missing"
fi

# Check systemd service
if systemctl is-enabled "$SERVICE_NAME" >/dev/null 2>&1; then
    log "Systemd service is enabled"
else
    warn "Systemd service is not enabled"
fi

if systemctl is-active "$SERVICE_NAME" >/dev/null 2>&1; then
    log "Service is running"
else
    warn "Service is not running"
    info "Start with: sudo systemctl start $SERVICE_NAME"
fi

# Check if port is listening
if netstat -tuln 2>/dev/null | grep -q ":$HTTP_PORT "; then
    log "HTTP server is listening on port $HTTP_PORT"
else
    warn "HTTP server is not listening on port $HTTP_PORT"
fi

# Test HTTP endpoints
info "Testing HTTP endpoints..."

# Test health endpoint
if curl -s -f "http://localhost:$HTTP_PORT/health" >/dev/null 2>&1; then
    log "Health endpoint is responding"
else
    warn "Health endpoint is not responding"
fi

# Show service status
echo
info "Service status:"
systemctl status "$SERVICE_NAME" --no-pager -l || true

echo
info "Recent logs:"
journalctl -u "$SERVICE_NAME" --no-pager -n 10 || true

echo
echo -e "${BLUE}"
echo "================================================"
echo "  System Check Complete"
echo "================================================"
echo -e "${NC}"

echo
info "Next steps if issues found:"
echo "1. Check configuration: sudo nano $INSTALL_DIR/.env"
echo "2. Restart service: sudo systemctl restart $SERVICE_NAME"
echo "3. View logs: journalctl -u $SERVICE_NAME -f"
echo "4. Test manually: cd $INSTALL_DIR && source venv/bin/activate && python http_server.py"