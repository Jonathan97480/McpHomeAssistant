# 🤖 Configuration Examples / Exemples de Configuration

This directory contains configuration examples for various AI services that support MCP (Model Context Protocol).

Ce répertoire contient des exemples de configuration pour différents services d'IA qui supportent MCP (Model Context Protocol).

## 📁 Files / Fichiers

### English

- **`claude_desktop_config.json`** - Configuration for Claude Desktop application
- **`lm_studio_config.json`** - Configuration for LM Studio local AI models
- **`continue_config.json`** - Configuration for Continue.dev VS Code extension
- **`cursor_config.json`** - Configuration for Cursor IDE
- **`cline_config.json`** - Configuration for Cline VS Code extension
- **`openwebui_config.yaml`** - Configuration for OpenWebUI interface
- **`smart_plug_automations.py`** - Example smart plug automation scripts

### Français

- **`claude_desktop_config.json`** - Configuration pour l'application Claude Desktop
- **`lm_studio_config.json`** - Configuration pour LM Studio (modèles IA locaux)
- **`continue_config.json`** - Configuration pour l'extension VS Code Continue.dev
- **`cursor_config.json`** - Configuration pour l'IDE Cursor
- **`cline_config.json`** - Configuration pour l'extension VS Code Cline
- **`openwebui_config.yaml`** - Configuration pour l'interface OpenWebUI
- **`smart_plug_automations.py`** - Scripts d'exemple pour automatisations de prises connectées

## 🔧 Setup Instructions / Instructions d'Installation

### For All Services / Pour Tous les Services

1. **Replace placeholders / Remplacez les placeholders :**
   - `your_token_here` → Your Home Assistant long-lived token
   - `http://192.168.1.22:8123` → Your Home Assistant URL

2. **Copy the appropriate config file / Copiez le fichier de config approprié :**
   - Check your AI service documentation for the correct config location
   - Restart your AI service after adding the configuration

### Claude Desktop

**Location / Emplacement :**
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

### LM Studio

1. Open LM Studio
2. Go to Settings → Developer → MCP Servers
3. Add server using the configuration from `lm_studio_config.json`

### Continue.dev

**Location / Emplacement :** `.continue/config.json` in your workspace root

### Cursor IDE

1. Open Cursor
2. Go to Settings → AI → MCP Servers
3. Add the configuration from `cursor_config.json`

### Cline

1. Install Cline extension in VS Code
2. Go to Cline settings
3. Add MCP server configuration from `cline_config.json`

### OpenWebUI

1. Install OpenWebUI MCP plugin
2. Go to Admin Settings → MCP Servers
3. Upload or paste the configuration from `openwebui_config.yaml`

## 🚀 Testing / Tests

After configuring any service, test the connection:

```bash
# Test basic connection
python ../tests/test_connection.py

# Test all MCP tools
python ../tests/test_mcp_tools.py
```

## 🔐 Security Notes / Notes de Sécurité

- Never commit your actual tokens to version control
- Use environment variables for sensitive information
- Regularly rotate your Home Assistant tokens
- Limit token permissions if possible

---

- Ne commitez jamais vos vrais tokens dans le contrôle de version
- Utilisez des variables d'environnement pour les informations sensibles
- Renouvelez régulièrement vos tokens Home Assistant
- Limitez les permissions des tokens si possible

## 🆘 Troubleshooting / Dépannage

### Common Issues / Problèmes Courants

1. **Connection refused / Connexion refusée**
   - Check Home Assistant URL and port
   - Verify firewall settings

2. **Authentication failed / Échec d'authentification**
   - Verify your token is correct and not expired
   - Check token permissions

3. **Service not found / Service non trouvé**
   - Ensure `homeassistant-mcp-server` is installed
   - Check PATH environment variable

### Getting Help / Obtenir de l'Aide

- Check the main [README.md](../README.md) for full documentation
- Run test scripts in the `../tests/` directory
- Open an issue on GitHub for bugs or feature requests

---

- Consultez le [README.md](../README.md) principal pour la documentation complète
- Lancez les scripts de test dans le répertoire `../tests/`
- Ouvrez une issue sur GitHub pour les bugs ou demandes de fonctionnalités

## 🎯 Utilisation des Automatisations

```bash
# Générer des automatisations pour vos prises
python examples/smart_plug_automations.py
```

Le script génère du YAML prêt à copier dans votre fichier `automations.yaml` Home Assistant.

## 💡 Exemples de Commandes Claude

Une fois configuré, vous pourrez utiliser des commandes comme :

```
• "Quel est l'état de toutes mes prises ?"
• "Allume la prise du vidéo projecteur"
• "Crée une automatisation pour éteindre la TV à 22h"
• "Montre-moi ma consommation énergétique"
• "Éteins tous les appareils de divertissement"
```