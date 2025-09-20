# Tests et Scripts d'Analyse

Ce dossier contient tous les scripts de test et d'analyse pour le serveur MCP Home Assistant.

## 📋 Scripts de Test

### Tests de Base
- **`test_connection.py`** - Test de connexion à Home Assistant
- **`test_mcp_tools.py`** - Test complet de tous les outils MCP
- **`test_automations.py`** - Test des fonctionnalités d'automatisation

### Scripts d'Analyse
- **`analyze_energy.py`** - Analyse détaillée du capteur de consommation énergétique
- **`analyze_smart_plugs.py`** - Analyse des prises connectées
- **`show_sensors.py`** - Affichage de tous les capteurs disponibles
- **`explore_automation_api.py`** - Exploration des endpoints d'automatisation

### Démonstrations
- **`demo_automations.py`** - Démonstration de génération d'automatisations YAML

## 🚀 Utilisation

Pour exécuter les tests depuis la racine du projet :

```bash
# Test de connexion basique
python tests/test_connection.py

# Test complet des outils MCP
python tests/test_mcp_tools.py

# Analyse des capteurs d'énergie
python tests/analyze_energy.py

# Analyse des prises connectées
python tests/analyze_smart_plugs.py

# Démonstration des automatisations
python tests/demo_automations.py
```

## ⚙️ Configuration

Assurez-vous que le fichier `.env` est configuré dans la racine du projet :

```env
HASS_URL=http://votre_ip:8123
HASS_TOKEN=votre_token_home_assistant
```

## 📊 Résultats Attendus

Les scripts d'analyse vous donneront des informations sur :
- État de vos 23 entités Home Assistant
- Consommation énergétique (capteur KWS-306WF)
- 9 prises connectées et leur état
- Automatisations YAML prêtes à utiliser