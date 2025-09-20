# Exemples et Configuration

Ce dossier contient des exemples d'utilisation et de configuration pour le serveur MCP Home Assistant.

## 📁 Fichiers

### Configuration
- **`claude_desktop_config.json`** - Configuration pour Claude Desktop
  - Copiez ce fichier dans votre configuration Claude Desktop
  - Ajustez le chemin vers votre installation

### Exemples d'Automatisations
- **`smart_plug_automations.py`** - Automatisations personnalisées pour prises connectées
  - Sécurité imprimante 3D (extinction après 3h)
  - Économie d'énergie nocturne
  - Surveillance appareils critiques
  - Mode travail bureau
  - Sécurité plaque électrique

## 🔧 Configuration Claude Desktop

1. Localisez votre fichier de configuration Claude Desktop
2. Copiez le contenu de `claude_desktop_config.json`
3. Ajustez le chemin `command` vers votre installation Python
4. Redémarrez Claude Desktop

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