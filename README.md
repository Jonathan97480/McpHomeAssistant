# 🏠 Home Assistant MCP Server

[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-orange)](https://www.home-assistant.io/)

Un serveur Model Context Protocol (MCP) puissant pour intégrer Home Assistant avec des agents IA comme Claude Desktop.

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