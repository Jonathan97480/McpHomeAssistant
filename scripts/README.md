# Scripts et Utilitaires

Ce dossier contient les scripts utilitaires pour le serveur MCP Home Assistant.

## Scripts Disponibles

### 🚀 `quick_start.sh`
**Objectif**: Configuration rapide pour développement et test  
**Usage**: `./scripts/quick_start.sh`  
**Description**: 
- Crée le fichier `.env` si manquant
- Installe les dépendances automatiquement
- Démarre le serveur HTTP pour les tests
- Configuration interactive

### 🛠️ `launcher.py`
**Objectif**: Wrapper pour service systemd  
**Usage**: Utilisé en interne par le service systemd  
**Description**: 
- Démarrage robuste avec chargement de l'environnement
- Gestion d'arrêt propre
- Récupération d'erreur et logging
- Gestion de processus pour la production

### 🔍 `check_installation.sh`
**Objectif**: Vérification d'installation Raspberry Pi  
**Usage**: `./scripts/check_installation.sh`  
**Description**: 
- Vérifie la complétude de l'installation
- Teste l'état du service et la connectivité
- Affiche les logs récents et l'état du service
- Fournit des conseils de dépannage

## Exemples d'Utilisation

### Flux de Développement
```bash
# Cloner le repository
git clone https://github.com/Jonathan97480/McpHomeAssistant.git
cd homeassistant-mcp-server

# Démarrage rapide pour test
./scripts/quick_start.sh
```

### Déploiement Production (Raspberry Pi)
```bash
# Exécuter le script d'installation
curl -sSL https://raw.githubusercontent.com/Jonathan97480/McpHomeAssistant/master/install.sh | bash

# Vérifier l'installation
./scripts/check_installation.sh

# Vérifier l'état du service
sudo systemctl status homeassistant-mcp-server
```

### Dépannage
```bash
# Vérifier la complétude de l'installation
./scripts/check_installation.sh

# Voir les logs en temps réel
journalctl -u homeassistant-mcp-server -f

# Redémarrer le service
sudo systemctl restart homeassistant-mcp-server

# Test manuel
cd /opt/homeassistant-mcp-server
source venv/bin/activate
python http_server.py
```

## Permissions des Scripts

Rendre les scripts exécutables:
```bash
chmod +x scripts/*.sh
```

## Fichiers de Configuration

Les scripts créent/utilisent ces fichiers de configuration:
- `.env` - Variables d'environnement (créé par quick_start.sh)
- `/etc/systemd/system/homeassistant-mcp-server.service` - Service systemd (créé par install.sh)

## Configuration

### Variables d'Environnement (.env)
```env
# Home Assistant Configuration
HASS_URL=http://localhost:8123
HASS_TOKEN=your_token_here

# HTTP Server Settings  
HTTP_SERVER_HOST=0.0.0.0
HTTP_SERVER_PORT=3002

# Logging
LOG_LEVEL=INFO
```

### Service Systemd
Le service utilise `launcher.py` pour:
- Charger automatiquement les variables d'environnement
- Gérer les redémarrages en cas d'erreur
- Fournir des logs structurés via journald
- Assurer un arrêt propre du serveur