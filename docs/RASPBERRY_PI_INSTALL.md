# 🍓 Raspberry Pi Installation Guide

This guide explains how to install the Home Assistant MCP Server directly on your Raspberry Pi, making it run as a local service alongside Home Assistant.

## 📋 Prerequisites

- Raspberry Pi running Debian/Raspbian
- Home Assistant already installed and running
- SSH access to your Raspberry Pi
- Internet connection

## 🚀 Quick Installation

### Option 1: Automated Installation (Recommended)

Run this single command on your Raspberry Pi:

```bash
curl -sSL https://raw.githubusercontent.com/Jonathan97480/McpHomeAssistant/master/install.sh | bash
```

### Option 2: Manual Installation

If you prefer to install manually, follow these steps:

#### 1. Connect to your Raspberry Pi

```bash
ssh homeassistant@192.168.1.22
# Replace with your Pi's IP address
```

#### 2. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

#### 3. Install Dependencies

```bash
sudo apt install -y python3-pip python3-venv python3-dev git curl build-essential libffi-dev libssl-dev
```

#### 4. Create Installation Directory

```bash
sudo mkdir -p /opt/homeassistant-mcp-server
sudo chown -R $USER:$USER /opt/homeassistant-mcp-server
cd /opt/homeassistant-mcp-server
```

#### 5. Clone Repository

```bash
git clone https://github.com/Jonathan97480/McpHomeAssistant.git .
```

#### 6. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -e .
```

#### 7. Create Configuration File

```bash
cat > .env << EOF
HASS_URL=http://localhost:8123
HASS_TOKEN=your_token_here
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=3000
LOG_LEVEL=INFO
EOF
```

## 🔑 Configuration

### 1. Get Home Assistant Token

1. Open Home Assistant web interface
2. Go to **Profile** → **Long-lived access tokens**
3. Click **Create Token**
4. Copy the generated token

### 2. Update Configuration

```bash
nano /opt/homeassistant-mcp-server/.env
```

Replace `your_token_here` with your actual token:

```env
HASS_URL=http://localhost:8123
HASS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=3000
LOG_LEVEL=INFO
```

## 🛠️ Service Configuration

### Create Systemd Service

```bash
sudo tee /etc/systemd/system/homeassistant-mcp-server.service > /dev/null << EOF
[Unit]
Description=Home Assistant MCP Server
After=network.target homeassistant.service
Wants=homeassistant.service

[Service]
Type=simple
User=homeassistant
Group=homeassistant
WorkingDirectory=/opt/homeassistant-mcp-server
Environment=PATH=/opt/homeassistant-mcp-server/venv/bin
ExecStart=/opt/homeassistant-mcp-server/venv/bin/python -m homeassistant_mcp_server.server
EnvironmentFile=/opt/homeassistant-mcp-server/.env
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable homeassistant-mcp-server
sudo systemctl start homeassistant-mcp-server
```

## 🧪 Testing

### 1. Check Service Status

```bash
sudo systemctl status homeassistant-mcp-server
```

Expected output:
```
● homeassistant-mcp-server.service - Home Assistant MCP Server
   Loaded: loaded (/etc/systemd/system/homeassistant-mcp-server.service; enabled; vendor preset: enabled)
   Active: active (running) since...
```

### 2. View Logs

```bash
# Real-time logs
journalctl -u homeassistant-mcp-server -f

# Recent logs
journalctl -u homeassistant-mcp-server --since "1 hour ago"
```

### 3. Test Connection

```bash
cd /opt/homeassistant-mcp-server
source venv/bin/activate
python tests/test_connection.py
```

### 4. Test MCP Tools

```bash
python tests/test_mcp_tools.py
```

## 🌐 Network Access

The MCP server will be available on:
- **Local**: `http://localhost:3000`
- **Network**: `http://192.168.1.22:3000` (replace with your Pi's IP)

### Configure Firewall (if needed)

```bash
sudo ufw allow 3000/tcp
```

## 🔧 AI Client Configuration

### For Claude Desktop (on another machine)

Update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "stdio-proxy",
      "args": ["http://192.168.1.22:3000"],
      "env": {}
    }
  }
}
```

### For LM Studio (on another machine)

1. Open LM Studio
2. Go to Settings → MCP Servers
3. Add server:
   - **Name**: `homeassistant`
   - **URL**: `http://192.168.1.22:3000`

## 📊 Monitoring

### Check Resource Usage

```bash
# CPU and Memory usage
top -p $(pgrep -f homeassistant-mcp-server)

# Disk usage
df -h /opt/homeassistant-mcp-server
```

### Log Rotation

Create log rotation configuration:

```bash
sudo tee /etc/logrotate.d/homeassistant-mcp-server << EOF
/var/log/homeassistant-mcp-server.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        systemctl reload homeassistant-mcp-server
    endscript
}
EOF
```

## 🔄 Updates

### Update the Server

```bash
cd /opt/homeassistant-mcp-server
git pull
source venv/bin/activate
pip install -e .
sudo systemctl restart homeassistant-mcp-server
```

### Auto-Update Script

Create an update script:

```bash
cat > /opt/homeassistant-mcp-server/update.sh << 'EOF'
#!/bin/bash
cd /opt/homeassistant-mcp-server
git pull
source venv/bin/activate
pip install -e .
sudo systemctl restart homeassistant-mcp-server
echo "Update completed!"
EOF

chmod +x /opt/homeassistant-mcp-server/update.sh
```

## 🛡️ Security

### Firewall Configuration

```bash
# Allow only local network access
sudo ufw allow from 192.168.1.0/24 to any port 3000

# Or allow specific IP only
sudo ufw allow from 192.168.1.100 to any port 3000
```

### SSL/HTTPS (Optional)

For secure connections, consider setting up a reverse proxy with nginx:

```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/mcp-server
```

## 🆘 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   journalctl -u homeassistant-mcp-server -n 50
   ```

2. **Permission errors**
   ```bash
   sudo chown -R homeassistant:homeassistant /opt/homeassistant-mcp-server
   ```

3. **Port already in use**
   ```bash
   sudo netstat -tulpn | grep 3000
   ```

4. **Home Assistant connection fails**
   - Check if Home Assistant is running: `sudo systemctl status homeassistant`
   - Verify token in `/opt/homeassistant-mcp-server/.env`
   - Test manually: `curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8123/api/`

### Performance Tuning

For better performance on Raspberry Pi:

```bash
# Increase swap (if needed)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 📚 Additional Resources

- [Main Documentation](../README.md)
- [Architecture Guide](../docs/ARCHITECTURE.md)
- [Configuration Examples](../examples/README.md)
- [GitHub Repository](https://github.com/Jonathan97480/McpHomeAssistant)

---

🎉 **Your Home Assistant MCP Server is now running locally on your Raspberry Pi!**