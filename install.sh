#!/bin/bash

# ===============================================================================
# Home Assistant MCP Server - Installation Script for Raspberry Pi
# ===============================================================================
#
# This script installs the Home Assistant MCP Server directly on a Raspberry Pi
# running Home Assistant, making it available as a system service.
#
# Usage: curl -sSL https://raw.githubusercontent.com/Jonathan97480/McpHomeAssistant/master/install.sh | bash
#
# ===============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/homeassistant-mcp-server"
SERVICE_NAME="homeassistant-mcp-server"
USER="homeassistant"
PYTHON_VERSION="3.11"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons."
        error "Please run it as the homeassistant user or with sudo for specific commands."
        exit 1
    fi
}

# Check system requirements
check_system() {
    log "Checking system requirements..."
    
    # Check OS
    if [[ ! -f /etc/debian_version ]]; then
        error "This script is designed for Debian/Raspbian systems only."
        exit 1
    fi
    
    # Check architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" != "armv7l" && "$ARCH" != "aarch64" ]]; then
        warn "This script is optimized for Raspberry Pi (ARM). Your architecture: $ARCH"
    fi
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log "Python version detected: $PYTHON_VER"
    
    # Check if Home Assistant is running
    if systemctl is-active --quiet homeassistant; then
        log "Home Assistant service is running ✓"
    else
        warn "Home Assistant service not detected. Please ensure it's installed and running."
    fi
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    sudo apt update
    sudo apt install -y \
        python3-pip \
        python3-venv \
        python3-dev \
        git \
        curl \
        build-essential \
        libffi-dev \
        libssl-dev
    
    log "System dependencies installed ✓"
}

# Create installation directory
create_install_dir() {
    log "Creating installation directory..."
    
    if [[ -d "$INSTALL_DIR" ]]; then
        warn "Installation directory already exists. Backing up..."
        sudo mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%s)"
    fi
    
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown -R $USER:$USER "$INSTALL_DIR"
    
    log "Installation directory created: $INSTALL_DIR"
}

# Download and install the MCP server
install_mcp_server() {
    log "Downloading Home Assistant MCP Server..."
    
    cd "$INSTALL_DIR"
    git clone https://github.com/Jonathan97480/McpHomeAssistant.git .
    
    log "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    log "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -e .
    
    log "MCP Server installed ✓"
}

# Create configuration file
create_config() {
    log "Creating configuration file..."
    
    CONFIG_FILE="$INSTALL_DIR/.env"
    
    cat > "$CONFIG_FILE" << EOF
# Home Assistant MCP Server Configuration
HASS_URL=http://localhost:8123
HASS_TOKEN=your_token_here

# Server Settings
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=3000

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/homeassistant-mcp-server.log
EOF
    
    chmod 600 "$CONFIG_FILE"
    
    warn "Please edit $CONFIG_FILE and set your Home Assistant token!"
    info "You can get a token from: Home Assistant > Profile > Long-lived access tokens"
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
    
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Home Assistant MCP Server
After=network.target homeassistant.service
Wants=homeassistant.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python -m homeassistant_mcp_server.server
EnvironmentFile=$INSTALL_DIR/.env
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$INSTALL_DIR /var/log
CapabilityBoundingSet=
LockPersonality=true
MemoryDenyWriteExecute=true
RestrictNamespaces=true
RestrictRealtime=true
SystemCallArchitectures=native

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    
    log "Systemd service created and enabled ✓"
}

# Create log directory
create_log_dir() {
    log "Setting up logging..."
    
    sudo mkdir -p /var/log
    sudo touch /var/log/homeassistant-mcp-server.log
    sudo chown $USER:$USER /var/log/homeassistant-mcp-server.log
    
    log "Logging configured ✓"
}

# Test installation
test_installation() {
    log "Testing installation..."
    
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    # Test import
    if python -c "import homeassistant_mcp_server.server" 2>/dev/null; then
        log "Python module import successful ✓"
    else
        error "Python module import failed ✗"
        return 1
    fi
    
    # Test connection script
    if [[ -f "tests/test_connection.py" ]]; then
        info "You can test the Home Assistant connection with:"
        info "cd $INSTALL_DIR && source venv/bin/activate && python tests/test_connection.py"
    fi
}

# Main installation function
main() {
    echo -e "${BLUE}"
    echo "============================================================"
    echo "   Home Assistant MCP Server - Raspberry Pi Installation"
    echo "============================================================"
    echo -e "${NC}"
    
    check_root
    check_system
    install_dependencies
    create_install_dir
    install_mcp_server
    create_config
    create_systemd_service
    create_log_dir
    test_installation
    
    echo -e "${GREEN}"
    echo "============================================================"
    echo "                 Installation Complete!"
    echo "============================================================"
    echo -e "${NC}"
    
    info "Next steps:"
    echo "1. Edit the configuration file: sudo nano $INSTALL_DIR/.env"
    echo "2. Add your Home Assistant token"
    echo "3. Start the service: sudo systemctl start $SERVICE_NAME"
    echo "4. Check status: sudo systemctl status $SERVICE_NAME"
    echo "5. View logs: journalctl -u $SERVICE_NAME -f"
    echo ""
    info "The MCP server will be available on port 3000"
    info "Access it from other machines using: http://YOUR_PI_IP:3000"
    echo ""
    warn "Don't forget to configure your AI client to connect to this server!"
}

# Run main function
main "$@"