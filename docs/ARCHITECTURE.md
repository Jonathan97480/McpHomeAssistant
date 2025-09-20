# Architecture du Projet

## 📁 Structure du Projet

```
homeassistant-mcp-server/
├── src/                              # Code source principal
│   └── homeassistant_mcp_server/
│       └── server.py                 # Serveur MCP principal
├── tests/                            # Scripts de test et analyse
│   ├── test_connection.py            # Test connexion Home Assistant
│   ├── test_mcp_tools.py             # Test outils MCP
│   ├── analyze_energy.py             # Analyse énergétique
│   ├── analyze_smart_plugs.py        # Analyse prises connectées
│   └── README.md
├── examples/                         # Exemples et configuration
│   ├── claude_desktop_config.json    # Config Claude Desktop
│   ├── smart_plug_automations.py     # Exemples automatisations
│   └── README.md
├── docs/                             # Documentation
│   ├── QUICKSTART.md                 # Guide démarrage rapide
│   └── ARCHITECTURE.md               # Ce fichier
├── .env.example                      # Exemple configuration
├── .gitignore                        # Exclusions Git
├── LICENSE                           # Licence MIT
├── pyproject.toml                    # Configuration Python
└── README.md                         # Documentation principale
```

## 🏗️ Architecture Technique

### Serveur MCP (`src/homeassistant_mcp_server/server.py`)

**HomeAssistantClient**
- Client asynchrone pour Home Assistant API
- Gestion des sessions HTTP avec aiohttp
- Authentification JWT token
- Méthodes pour entités, services, historique, automatisations

**Outils MCP Disponibles**
1. `get_entities` - Liste des entités avec filtrage
2. `get_entity_state` - État détaillé d'une entité
3. `call_service` - Appel de services Home Assistant
4. `get_history` - Historique temporel des entités
5. `get_services` - Liste des services disponibles
6. `create_automation` - Génération automatisations YAML
7. `list_automations` - Liste des automatisations actives
8. `toggle_automation` - Activation/désactivation automatisations

### Gestion des Automatisations

Le système génère du YAML Home Assistant compatible :
- **Déclencheurs** : temps, état, numérique, soleil
- **Conditions** : temps, état, présence
- **Actions** : services, notifications, contrôles

### Configuration

**Variables d'environnement** (`.env`)
```env
HASS_URL=http://192.168.1.22:8123
HASS_TOKEN=eyJhbGciOiJIUzI1NiIs...
```

**Configuration Claude Desktop**
```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "python",
      "args": ["-m", "homeassistant_mcp_server.server"],
      "cwd": "/chemin/vers/homeassistant-mcp-server"
    }
  }
}
```

## 🔄 Flux de Données

1. **Claude Desktop** → Requête utilisateur
2. **Serveur MCP** → Traduction en appels Home Assistant API
3. **Home Assistant** → Exécution/Récupération données
4. **Serveur MCP** → Formatage réponse
5. **Claude Desktop** → Présentation utilisateur

## 🛡️ Sécurité

- Authentification par token JWT Home Assistant
- Communication locale (réseau privé)
- Pas de stockage de données sensibles
- Validation des paramètres d'entrée

## 📊 Entités Supportées

**Votre Installation** (23 entités détectées)
- 9 prises connectées (switches)
- 7 capteurs (dont énergie KWS-306WF)
- 6 capteurs solaires (timestamps)
- 1 entité personne

## 🔧 Extension du Système

Pour ajouter de nouveaux outils MCP :

1. Ajouter méthode dans `HomeAssistantClient`
2. Définir schéma JSON dans `handle_list_tools()`
3. Implémenter logique dans `handle_call_tool()`
4. Ajouter tests dans `tests/`