# 🏠 Home Assistant MCP Server

[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-orange)](https://www.home-assistant.io/)
[![Phase](https://img.shields.io/badge/Phase%203.4-Complete-brightgreen)](docs/PHASE_3_4_SUMMARY.md)

Un serveur Model Context Protocol (MCP) puissant avec **interface web complète** pour intégrer Home Assistant avec les agents IA.

> **� Interface Web Complète !** Phase 3.4 inclut une interface web responsive avec dashboard, authentification, gestion des permissions et configuration multi-instances Home Assistant. Installation automatisée pour Raspberry Pi.

> **🍓 Raspberry Pi Ready!** Installation optimisée pour Raspberry Pi 3B+ avec script automatisé `install.sh`.

[🇫🇷 Version française](#version-française) | [📚 Documentation](docs/) | [🧪 Tests](tests/)

## ✨ Features

- 🏠 **Entity Management** : Read the state of all your Home Assistant devices
- 🎮 **Device Control** : Turn on/off lights, switches, and more
- 📊 **History Access** : Access sensor and entity history data
- 🔐 **Secure Authentication** : Uses Home Assistant access tokens
- 🚀 **High Performance** : Asynchronous connections for optimal responsiveness
- 🛠️ **Service Calls** : Call any Home Assistant service
- 🤖 **Smart Automations** : Generate intelligent YAML automations

## 🌐 HTTP Server Mode

In addition to MCP protocol, this server can run as a standalone HTTP REST API server, perfect for:

- 🍓 **Raspberry Pi deployment** alongside Home Assistant
- 🔗 **Web applications** and custom integrations  
- 🚀 **Microservices** architecture
- 📱 **Mobile apps** and third-party tools
- 🤖 **AI agents** that don't support MCP protocol directly

**Why use HTTP Server mode?**
- **Universal compatibility**: Any programming language or tool can connect via HTTP
- **Direct deployment**: Install directly on your Raspberry Pi running Home Assistant
- **No MCP client required**: Works with any HTTP client (curl, Postman, web browsers)
- **REST API standard**: Easy integration with existing systems and workflows
- **Standalone operation**: Independent service that doesn't require MCP infrastructure

### HTTP Endpoints

The HTTP server provides a complete REST API interface to Home Assistant:

- `GET /health` - Server health check and Home Assistant connectivity status
- `GET /api/entities` - List all entities (with optional domain filtering like `?domain=light`)
- `GET /api/entities/{entity_id}` - Get specific entity state and attributes
- `POST /api/services/call` - Call Home Assistant services (turn on/off devices, etc.)
- `GET /api/history` - Get entity history data with time range filtering

**Use Cases:**
- **Web dashboards**: Build custom web interfaces for Home Assistant
- **Mobile apps**: Create native mobile applications with HTTP API
- **Automation scripts**: Use any programming language to automate your home
- **Third-party integrations**: Connect non-MCP services to Home Assistant
- **Development testing**: Quick API testing with curl or Postman

### Quick Installation

**Automatic Installation:**
```bash
curl -fsSL https://raw.githubusercontent.com/Jonathan97480/McpHomeAssistant/master/install.sh | bash
```

**Manual Installation:**
```bash
git clone https://github.com/Jonathan97480/McpHomeAssistant.git
cd McpHomeAssistant
chmod +x install.sh
./install.sh
```

### Quick HTTP Server Start

```bash
# Install dependencies
pip install aiohttp python-dotenv

# Configure environment
cp .env.example .env
# Edit .env with your Home Assistant URL and token

# Start HTTP server
python http_server.py
```

Server runs on `http://localhost:3002` by default and provides a complete REST API interface.

**Example API calls:**
```bash
# Check server health
curl http://localhost:3002/health

# List all lights
curl http://localhost:3002/api/entities?domain=light

# Turn on a light
curl -X POST http://localhost:3002/api/services/call \
  -H "Content-Type: application/json" \
  -d '{"domain": "light", "service": "turn_on", "target": {"entity_id": "light.living_room"}}'
```

📖 **[Complete HTTP Server Guide](docs/HTTP_SERVER_README.md)**

### 🎯 HTTP vs MCP: When to use which?

**Use HTTP Server when:**
- 🍓 Installing directly on Raspberry Pi 3B+
- 🌐 Building web applications or mobile apps
- 🔧 Integrating with non-MCP tools and services
- 🚀 Need universal compatibility across programming languages
- 📊 Creating custom dashboards or monitoring systems

**Use MCP Server when:**
- 💻 Working with AI agents that support MCP (Claude Desktop, etc.)
- 🤖 Need structured tool-based interactions
- 🔄 Want automatic tool discovery and schema validation
- 📝 Prefer conversation-based device control

## 📁 Project Structure

```
homeassistant-mcp-server/
├── src/                              # Main source code
│   └── homeassistant_mcp_server/
│       └── server.py                 # Main MCP server
├── tests/                            # Test and analysis scripts
│   ├── test_connection.py            # Basic connection test
│   ├── test_mcp_tools.py             # Complete tools test
│   ├── test_http_server.py           # HTTP server tests
│   ├── analyze_energy.py             # Energy analysis
│   └── analyze_smart_plugs.py        # Smart plugs analysis
├── examples/                         # Examples and configuration
│   ├── claude_desktop_config.json    # Claude Desktop configuration
│   └── smart_plug_automations.py     # Smart plug automations
├── docs/                             # Documentation
│   ├── QUICKSTART.md                 # Quick start guide
│   ├── HTTP_SERVER_README.md         # HTTP server documentation
│   ├── RASPBERRY_PI_INSTALL.md       # Raspberry Pi installation
│   └── ARCHITECTURE.md               # Technical architecture
├── scripts/                          # Utility scripts
│   ├── launcher.py                   # Service launcher wrapper
│   └── README.md                     # Scripts documentation
├── http_server.py                    # Standalone HTTP server
├── install.sh                        # Raspberry Pi installation script
├── .env.example                      # Configuration example
└── README.md                         # This file
```

## 🚀 Installation

### Quick Start Options

#### 🍓 **Raspberry Pi Installation (Recommended)**
Install directly on your Raspberry Pi 3B+ alongside Home Assistant:

```bash
# Download and run the installation script
curl -sSL https://raw.githubusercontent.com/Jonathan97480/McpHomeAssistant/master/install.sh | bash

# Or download and customize before running
wget https://raw.githubusercontent.com/Jonathan97480/McpHomeAssistant/master/install.sh
chmod +x install.sh
./install.sh
```

**🎯 Optimized for Raspberry Pi 3B+:**
- ✅ **HTTP Server Setup**: Installs the standalone HTTP server for easy AI integration
- ✅ **Interactive Configuration**: Prompts for Home Assistant token and URL during installation
- ✅ **Systemd Service**: Auto-configures system service for automatic startup
- ✅ **Security**: Proper file permissions and service isolation
- ✅ **Port 3002**: HTTP REST API accessible from external machines
- ✅ **Resource Optimized**: Lightweight deployment suitable for Pi 3B+ hardware
- ✅ **Debian Compatible**: Tested on Raspberry Pi OS (Debian-based)

**System Requirements:**
- Raspberry Pi 3B+ or newer
- Raspberry Pi OS (Debian 11+ recommended)
- Home Assistant running on the same Pi or network
- Python 3.9+ (automatically installed if needed)
- At least 512MB available RAM

📖 **[Complete Raspberry Pi Guide](docs/RASPBERRY_PI_INSTALL.md)**

#### 💻 **Desktop Installation**
For development or remote installation:

### Prerequisites

- Python 3.8+
- Home Assistant with API enabled
- Home Assistant access token

### Server Installation

```bash
cd homeassistant-mcp-server
pip install -e .
```

### Configuration

1. Create a `.env` file:

```env
HASS_URL=http://192.168.1.22:8123
HASS_TOKEN=your_token_here
```

2. Get your Home Assistant token:
   - Go to Home Assistant > Profile > Long-lived access tokens
   - Create a new token
   - Copy it to the `.env` file

## Claude Desktop Configuration

Add this to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "homeassistant-mcp-server",
      "env": {
        "HASS_URL": "http://192.168.1.22:8123",
        "HASS_TOKEN": "your_token_here"
      }
    }
  }
}
```

**📄 Complete configuration file available in `examples/claude_desktop_config.json`**

## 🤖 AI Service Configurations

### Claude Desktop
Add this to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "homeassistant-mcp-server",
      "env": {
        "HASS_URL": "http://192.168.1.22:8123",
        "HASS_TOKEN": "your_token_here"
      }
    }
  }
}
```

### LM Studio
Configure MCP in LM Studio:

1. Open LM Studio
2. Go to Settings > MCP Servers
3. Add a new server:
   - **Name**: `homeassistant`
   - **Command**: `homeassistant-mcp-server`
   - **Environment Variables**:
     ```
     HASS_URL=http://192.168.1.22:8123
     HASS_TOKEN=your_token_here
     ```

### Continue.dev (VS Code Extension)
Add to your Continue configuration (`.continue/config.json`):

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "homeassistant-mcp-server",
      "env": {
        "HASS_URL": "http://192.168.1.22:8123",
        "HASS_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Cursor IDE
Add to Cursor's AI configuration:

1. Open Cursor IDE
2. Go to Settings > AI > MCP Servers
3. Add server configuration:
   ```json
   {
     "name": "homeassistant",
     "command": "homeassistant-mcp-server",
     "env": {
       "HASS_URL": "http://192.168.1.22:8123",
       "HASS_TOKEN": "your_token_here"
     }
   }
   ```

### Cline (VS Code Extension)
Configure in Cline settings:

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "homeassistant-mcp-server",
      "args": [],
      "env": {
        "HASS_URL": "http://192.168.1.22:8123",
        "HASS_TOKEN": "your_token_here"
      }
    }
  }
}
```

### LM Studio
LM Studio peut utiliser le serveur via des fonctions HTTP personnalisées:

**Option 1: HTTP Functions (Recommandé)**
1. Importez le fichier [`configs/lm-studio-functions.json`](configs/lm-studio-functions.json)
2. Utilisez le prompt système [`configs/lm-studio-system-prompt.md`](configs/lm-studio-system-prompt.md)
3. Assurez-vous que le serveur HTTP fonctionne: `http://192.168.1.22:3002/health`

**Configuration rapide:**
```json
{
  "name": "control_light",
  "endpoint": {
    "method": "POST",
    "url": "http://192.168.1.22:3002/api/services/call",
    "body": {
      "domain": "light",
      "service": "{{action}}",
      "service_data": {"entity_id": "{{entity_id}}"}
    }
  }
}
```

📖 **[Guide complet LM Studio](docs/LM_STUDIO_CONFIG.md)**
}
```

### OpenWebUI
For OpenWebUI MCP integration:

1. Install the MCP plugin
2. Configure server in settings:
   ```yaml
   servers:
     homeassistant:
       command: homeassistant-mcp-server
       env:
         HASS_URL: "http://192.168.1.22:8123"
         HASS_TOKEN: "your_token_here"
   ```

### Custom Integration
For other MCP-compatible services, use this standard format:

```json
{
  "servers": {
    "homeassistant": {
      "command": "homeassistant-mcp-server",
      "env": {
        "HASS_URL": "http://192.168.1.22:8123",
        "HASS_TOKEN": "your_token_here"
      }
    }
  }
}
```

**🔧 Configuration Notes:**
- Replace `your_token_here` with your actual Home Assistant token
- Update the URL if your Home Assistant runs on a different address
- Some services may require the full path to the executable
- Restart your AI service after adding the configuration

## 🧪 Testing and Validation

Test your installation with the provided scripts:

```bash
# Test Home Assistant connection
python tests/test_connection.py

# Complete test of all MCP tools
python tests/test_mcp_tools.py

# Analyze your energy consumption
python tests/analyze_energy.py

# Analyze your smart plugs
python tests/analyze_smart_plugs.py

# Generate example automations
python examples/smart_plug_automations.py
```

## 💬 Usage

Once configured, you can ask Claude:

- "What lights are currently on?"
- "Turn off all the living room lights"
- "Show me the temperature from my sensors"
- "What's the temperature history for today?"
- "Create an automation to turn on lights at sunset"
- "Generate an alert when energy consumption exceeds 700 kWh"

## 🛠️ Available Tools

The MCP server exposes **8 tools** to interact with Home Assistant:

### 📋 **Entity Management**
- **`get_entities`** : List all entities with domain filtering
- **`get_entity_state`** : Get detailed state of an entity
- **`get_history`** : Entity history over a given period

### 🎮 **Device Control**
- **`call_service`** : Call a service to control devices
- **`get_services`** : List all available services

### 🤖 **Automations** *(New!)*
- **`create_automation`** : Generate ready-to-use YAML automations
- **`list_automations`** : List all active automations
- **`toggle_automation`** : Enable/disable an automation

## 💡 Automation Examples

### ⚡ **Energy Monitoring**
```yaml
- alias: "High consumption alert"
  trigger:
    - platform: numeric_state
      entity_id: sensor.kws_306wf_energie_totale
      above: 700
  action:
    - service: persistent_notification.create
      data:
        title: "⚡ High Consumption"
        message: "More than 700 kWh consumed!"
```

### 🌅 **Automatic Lighting**
```yaml
- alias: "Lights at sunset"
  trigger:
    - platform: sun
      event: sunset
      offset: "-00:30:00"
  action:
    - service: light.turn_on
      target:
        area_id: living_room
```

### 📅 **Scheduled Notifications**
```yaml
- alias: "Morning notification"
  trigger:
    - platform: time
      at: "08:00:00"
  action:
    - service: persistent_notification.create
      data:
        title: "🌅 Good Morning!"
        message: "Have a great day!"
```

## 📚 Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Fast installation and configuration
- **[Architecture](docs/ARCHITECTURE.md)** - Detailed technical documentation
- **[Tests](tests/README.md)** - Test scripts guide
- **[Examples](examples/README.md)** - Examples and configurations

## 🔧 Development

```bash
# Development installation
pip install -e ".[dev]"

# Run tests
python tests/test_mcp_tools.py

# Analyze your installation
python tests/analyze_smart_plugs.py
python -m pytest

# Start the server
homeassistant-mcp-server
```

## License

MIT

---

# Version française

Un serveur Model Context Protocol (MCP) puissant pour intégrer Home Assistant avec des agents IA comme Claude Desktop.

[🇬🇧 English version](#-home-assistant-mcp-server)

## ✨ Fonctionnalités

- 🏠 **Lecture d'entités** : Consultez l'état de tous vos appareils Home Assistant
- 🎮 **Contrôle d'appareils** : Allumer/éteindre lumières, commutateurs, etc.
- 📊 **Historique** : Accédez à l'historique des capteurs et entités
- 🔐 **Authentification sécurisée** : Utilise les tokens d'accès Home Assistant
- 🚀 **Performance** : Connexions asynchrones pour une réactivité optimale
- 🛠️ **Services** : Appelez n'importe quel service Home Assistant
- 🤖 **Automatisations** : Générez des automatisations YAML intelligentes

## 🌐 Mode Serveur HTTP

En plus du protocole MCP, ce serveur peut fonctionner comme un serveur HTTP REST API autonome, parfait pour :

- 🍓 **Déploiement Raspberry Pi** aux côtés de Home Assistant
- 🔗 **Applications web** et intégrations personnalisées
- 🚀 **Architecture microservices** 
- 📱 **Applications mobiles** et outils tiers
- 🤖 **Agents IA** qui ne supportent pas directement le protocole MCP

**Pourquoi utiliser le mode Serveur HTTP ?**
- **Compatibilité universelle** : N'importe quel langage ou outil peut se connecter via HTTP
- **Déploiement direct** : Installation directe sur votre Raspberry Pi 3B+ avec Home Assistant
- **Pas de client MCP requis** : Fonctionne avec n'importe quel client HTTP (curl, Postman, navigateurs)
- **Standard REST API** : Intégration facile avec systèmes et workflows existants
- **Fonctionnement autonome** : Service indépendant ne nécessitant pas d'infrastructure MCP

## 📁 Structure du Projet

```
homeassistant-mcp-server/
├── src/                              # Code source principal
│   └── homeassistant_mcp_server/
│       └── server.py                 # Serveur MCP principal
├── tests/                            # Scripts de test et analyse
│   ├── test_connection.py            # Test connexion de base
│   ├── test_mcp_tools.py             # Test complet des outils
│   ├── analyze_energy.py             # Analyse énergétique
│   └── analyze_smart_plugs.py        # Analyse prises connectées
├── examples/                         # Exemples et configuration
│   ├── claude_desktop_config.json    # Configuration Claude Desktop
│   └── smart_plug_automations.py     # Automatisations des prises
├── docs/                             # Documentation
│   ├── QUICKSTART.md                 # Guide de démarrage rapide
│   └── ARCHITECTURE.md               # Architecture technique
├── .env.example                      # Exemple de configuration
└── README.md                         # Ce fichier
```

## 🚀 Installation

### Options de Démarrage Rapide

#### 🍓 **Installation Raspberry Pi (Recommandée)**
Installez directement sur votre Raspberry Pi 3B+ avec Home Assistant :

```bash
curl -sSL https://raw.githubusercontent.com/Jonathan97480/McpHomeAssistant/master/install.sh | bash
```

**🎯 Optimisé pour Raspberry Pi 3B+ :**
- ✅ **Configuration Serveur HTTP** : Installe le serveur HTTP autonome pour intégration IA facile
- ✅ **Configuration Interactive** : Demande le token et URL Home Assistant pendant l'installation
- ✅ **Service Systemd** : Configure automatiquement le service système pour démarrage automatique
- ✅ **Sécurité** : Permissions de fichiers appropriées et isolation du service
- ✅ **Port 3002** : API REST HTTP accessible depuis des machines externes
- ✅ **Optimisé Ressources** : Déploiement léger adapté au matériel Pi 3B+
- ✅ **Compatible Debian** : Testé sur Raspberry Pi OS (basé Debian)

**Configuration Système Requise :**
- Raspberry Pi 3B+ ou plus récent
- Raspberry Pi OS (Debian 11+ recommandé)
- Home Assistant fonctionnant sur le même Pi ou réseau
- Python 3.9+ (installé automatiquement si nécessaire)
- Au moins 512MB de RAM disponible

📖 **[Guide Complet Raspberry Pi](docs/RASPBERRY_PI_INSTALL.md)**

#### 💻 **Installation Bureau**
Pour le développement ou l'installation à distance :

### Prérequis

- Python 3.8+
- Home Assistant avec API activée
- Token d'accès Home Assistant

### Installation du serveur

```bash
cd homeassistant-mcp-server
pip install -e .
```

### Configuration

1. Créez un fichier `.env` :

```env
HASS_URL=http://192.168.1.22:8123
HASS_TOKEN=votre_token_ici
```

2. Obtenez votre token Home Assistant :
   - Allez dans Home Assistant > Profil > Tokens d'accès à long terme
   - Créez un nouveau token
   - Copiez-le dans le fichier `.env`

## Configuration Claude Desktop

Ajoutez ceci à votre configuration Claude Desktop (`claude_desktop_config.json`) :

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "homeassistant-mcp-server",
      "env": {
        "HASS_URL": "http://192.168.1.22:8123",
        "HASS_TOKEN": "votre_token_ici"
      }
    }
  }
}
```

**📄 Fichier de configuration complet disponible dans `examples/claude_desktop_config.json`**

## 🤖 Configurations des Services d'IA

### Claude Desktop
Ajoutez ceci à votre configuration Claude Desktop (`claude_desktop_config.json`) :

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "homeassistant-mcp-server",
      "env": {
        "HASS_URL": "http://192.168.1.22:8123",
        "HASS_TOKEN": "votre_token_ici"
      }
    }
  }
}
```

### LM Studio
Configurez MCP dans LM Studio :

1. Ouvrez LM Studio
2. Allez dans Paramètres > Serveurs MCP
3. Ajoutez un nouveau serveur :
   - **Nom** : `homeassistant`
   - **Commande** : `homeassistant-mcp-server`
   - **Variables d'environnement** :
     ```
     HASS_URL=http://192.168.1.22:8123
     HASS_TOKEN=votre_token_ici
     ```

### Continue.dev (Extension VS Code)
Ajoutez à votre configuration Continue (`.continue/config.json`) :

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "homeassistant-mcp-server",
      "env": {
        "HASS_URL": "http://192.168.1.22:8123",
        "HASS_TOKEN": "votre_token_ici"
      }
    }
  }
}
```

### Cursor IDE
Ajoutez à la configuration AI de Cursor :

1. Ouvrez Cursor IDE
2. Allez dans Paramètres > IA > Serveurs MCP
3. Ajoutez la configuration du serveur :
   ```json
   {
     "name": "homeassistant",
     "command": "homeassistant-mcp-server",
     "env": {
       "HASS_URL": "http://192.168.1.22:8123",
       "HASS_TOKEN": "votre_token_ici"
     }
   }
   ```

### Cline (Extension VS Code)
Configurez dans les paramètres Cline :

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "homeassistant-mcp-server",
      "args": [],
      "env": {
        "HASS_URL": "http://192.168.1.22:8123",
        "HASS_TOKEN": "votre_token_ici"
      }
    }
  }
}
```

### OpenWebUI
Pour l'intégration MCP OpenWebUI :

1. Installez le plugin MCP
2. Configurez le serveur dans les paramètres :
   ```yaml
   servers:
     homeassistant:
       command: homeassistant-mcp-server
       env:
         HASS_URL: "http://192.168.1.22:8123"
         HASS_TOKEN: "votre_token_ici"
   ```

### Intégration Personnalisée
Pour d'autres services compatibles MCP, utilisez ce format standard :

```json
{
  "servers": {
    "homeassistant": {
      "command": "homeassistant-mcp-server",
      "env": {
        "HASS_URL": "http://192.168.1.22:8123",
        "HASS_TOKEN": "votre_token_ici"
      }
    }
  }
}
```

**🔧 Notes de Configuration :**
- Remplacez `votre_token_ici` par votre vrai token Home Assistant
- Mettez à jour l'URL si votre Home Assistant fonctionne sur une autre adresse
- Certains services peuvent nécessiter le chemin complet vers l'exécutable
- Redémarrez votre service IA après avoir ajouté la configuration

## 🧪 Tests et Validation

Testez votre installation avec les scripts fournis :

```bash
# Test de connexion Home Assistant
python tests/test_connection.py

# Test complet de tous les outils MCP
python tests/test_mcp_tools.py

# Analyse de votre consommation énergétique
python tests/analyze_energy.py

# Analyse de vos prises connectées
python tests/analyze_smart_plugs.py

# Génération d'automatisations d'exemple
python examples/smart_plug_automations.py
```

## 💬 Utilisation

Une fois configuré, vous pouvez demander à Claude :

- "Quelles sont mes lumières allumées ?"
- "Éteins toutes les lumières du salon"
- "Montre-moi la température de mes capteurs"
- "Quel est l'historique de mon capteur de température aujourd'hui ?"
- "Crée une automatisation pour allumer les lumières au coucher du soleil"
- "Génère une alerte quand ma consommation énergétique dépasse 700 kWh"

## 🛠️ Outils disponibles

Le serveur MCP expose **8 outils** pour interagir avec Home Assistant :

### 📋 **Gestion des entités**
- **`get_entities`** : Liste toutes les entités avec filtrage par domaine
- **`get_entity_state`** : Récupère l'état détaillé d'une entité
- **`get_history`** : Historique d'une entité sur une période donnée

### 🎮 **Contrôle des appareils**
- **`call_service`** : Appelle un service pour contrôler des appareils
- **`get_services`** : Liste tous les services disponibles

### 🤖 **Automatisations** *(Nouveau !)*
- **`create_automation`** : Génère des automatisations YAML prêtes à utiliser
- **`list_automations`** : Liste toutes les automatisations actives
- **`toggle_automation`** : Active/désactive une automatisation

## 💡 Exemples d'automatisations

### ⚡ **Surveillance énergétique**
```yaml
- alias: "Alerte consommation élevée"
  trigger:
    - platform: numeric_state
      entity_id: sensor.kws_306wf_energie_totale
      above: 700
  action:
    - service: persistent_notification.create
      data:
        title: "⚡ Consommation Élevée"
        message: "Plus de 700 kWh consommés !"
```

### 🌅 **Éclairage automatique**
```yaml
- alias: "Lumières au coucher du soleil"
  trigger:
    - platform: sun
      event: sunset
      offset: "-00:30:00"
  action:
    - service: light.turn_on
      target:
        area_id: salon
```

### 📅 **Notifications programmées**
```yaml
- alias: "Notification matinale"
  trigger:
    - platform: time
      at: "08:00:00"
  action:
    - service: persistent_notification.create
      data:
        title: "🌅 Bonjour !"
        message: "Bonne journée !"
```

## � Structure du Projet

```
McpHomeAssistant/
├── 📂 docs/                    # 📚 Documentation complète
│   ├── DEPLOYMENT_GUIDE.md     # Guide de déploiement
│   ├── PHASE_3_4_README.md     # Documentation Phase 3.4
│   ├── QUICK_INSTALL_RPI.md    # Installation rapide
│   └── ...                     # Autres guides
├── 📂 tests/                   # 🧪 Suite de tests
│   ├── test_simple.py          # Tests rapides
│   ├── test_complete.py        # Tests complets
│   ├── test_web_interface.py   # Tests interface web
│   └── ...                     # Autres tests
├── 📂 web/                     # 🌐 Interface Web Phase 3.4
│   ├── static/css/main.css     # Framework CSS responsive
│   ├── static/js/dashboard.js  # SPA JavaScript
│   └── templates/              # Templates HTML
├── 📂 src/                     # 📦 Code source principal
├── 📂 configs/                 # ⚙️ Configurations
├── 📂 examples/                # 💡 Exemples d'usage
├── 🚀 install.sh               # Script installation unifié
├── 🏠 bridge_server.py         # Serveur principal
├── 🖥️ start_server.py          # Script de démarrage
└── 📋 README.md                # Ce fichier
```

## �📚 Documentation

### 🚀 Installation et Déploiement
- **[Guide de déploiement complet](docs/DEPLOYMENT_GUIDE.md)** - Installation production
- **[Installation rapide Raspberry Pi](docs/QUICK_INSTALL_RPI.md)** - Guide express
- **[Installation détaillée Pi](docs/RASPBERRY_PI_INSTALL.md)** - Guide complet Pi

### 🏗️ Architecture et Développement
- **[Architecture système](docs/ARCHITECTURE.md)** - Documentation technique
- **[API REST](docs/API_DOCUMENTATION.md)** - Documentation API complète
- **[Phase 3.4](docs/PHASE_3_4_README.md)** - Interface web complète

### 🧪 Tests et Validation
- **[Guide des tests](tests/README.md)** - Suite de tests complète
- **[Examples d'usage](examples/README.md)** - Exemples pratiques

## 🔧 Développement

```bash
# Installation en mode développement
pip install -e ".[dev]"

# Exécuter les tests
python tests/test_mcp_tools.py

# Analyser votre installation
python tests/analyze_smart_plugs.py
python -m pytest

# Lancement du serveur
homeassistant-mcp-server
```

## Licence

MIT