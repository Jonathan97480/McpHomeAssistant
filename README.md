# 🏠 Home Assistant MCP Server

[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-orange)](https://www.home-assistant.io/)

A powerful Model Context Protocol (MCP) server for integrating Home Assistant with AI agents like Claude Desktop.

[🇫🇷 Version française](#version-française)

## ✨ Features

- 🏠 **Entity Management** : Read the state of all your Home Assistant devices
- 🎮 **Device Control** : Turn on/off lights, switches, and more
- 📊 **History Access** : Access sensor and entity history data
- 🔐 **Secure Authentication** : Uses Home Assistant access tokens
- 🚀 **High Performance** : Asynchronous connections for optimal responsiveness
- 🛠️ **Service Calls** : Call any Home Assistant service
- 🤖 **Smart Automations** : Generate intelligent YAML automations

## 📁 Project Structure

```
homeassistant-mcp-server/
├── src/                              # Main source code
│   └── homeassistant_mcp_server/
│       └── server.py                 # Main MCP server
├── tests/                            # Test and analysis scripts
│   ├── test_connection.py            # Basic connection test
│   ├── test_mcp_tools.py             # Complete tools test
│   ├── analyze_energy.py             # Energy analysis
│   └── analyze_smart_plugs.py        # Smart plugs analysis
├── examples/                         # Examples and configuration
│   ├── claude_desktop_config.json    # Claude Desktop configuration
│   └── smart_plug_automations.py     # Smart plug automations
├── docs/                             # Documentation
│   ├── QUICKSTART.md                 # Quick start guide
│   └── ARCHITECTURE.md               # Technical architecture
├── .env.example                      # Configuration example
└── README.md                         # This file
```

## 🚀 Installation

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

## 📚 Documentation

- **[Guide de démarrage rapide](docs/QUICKSTART.md)** - Installation et configuration rapide
- **[Architecture](docs/ARCHITECTURE.md)** - Documentation technique détaillée
- **[Tests](tests/README.md)** - Guide des scripts de test
- **[Exemples](examples/README.md)** - Exemples et configurations

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