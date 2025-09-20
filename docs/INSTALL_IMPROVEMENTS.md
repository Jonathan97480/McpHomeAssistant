# Améliorations du Script d'Installation

## 🔧 Mises à Jour Apportées

### ✅ Configuration du Serveur HTTP
- **Port 3002**: Le script installe maintenant le serveur HTTP sur le port 3002 (au lieu du MCP basique sur le port 3000)
- **Dependencies HTTP**: Installation automatique d'`aiohttp`, `python-dotenv`, `aiofiles`
- **Fichier http_server.py**: Copie et configuration du serveur HTTP standalone

### ✅ Configuration Interactive .env
- **Prompt pour le Token**: Le script demande maintenant le token Home Assistant de manière interactive
- **URL personnalisée**: Possibilité de configurer l'URL Home Assistant pendant l'installation
- **Validation**: Vérification que le fichier .env est correctement créé avec les bonnes valeurs

### ✅ Service Systemd Amélioré
- **ExecStart mis à jour**: Le service lance maintenant `http_server.py` au lieu du serveur MCP basique
- **Variables d'environnement**: Chargement correct du fichier .env
- **Sécurité renforcée**: Permissions et isolation du service améliorées

### ✅ Tests et Vérification
- **Tests HTTP**: Vérification que les modules HTTP sont bien installés
- **Endpoints de test**: Instructions pour tester les endpoints REST API
- **Sanity checks**: Validation de l'installation complète

## 🚀 Nouveaux Scripts Utilitaires

### `quick_start.sh`
- Démarrage rapide pour développement local
- Configuration automatique de l'environnement
- Installation des dépendances si manquantes

### `check_installation.sh`
- Vérification complète de l'installation Raspberry Pi
- Tests de connectivité des endpoints
- Diagnostic du service systemd
- Conseils de dépannage

## 📋 Flux d'Installation Mis à Jour

1. **Téléchargement**: `curl -sSL https://raw.githubusercontent.com/Jonathan97480/McpHomeAssistant/master/install.sh | bash`
2. **Configuration interactive**: Le script demande le token HA et l'URL
3. **Installation HTTP**: Installation du serveur HTTP avec toutes les dépendances
4. **Service systemd**: Configuration du service pour `http_server.py`
5. **Vérification**: Tests automatiques des endpoints et du service

## 🌐 Endpoints Disponibles Après Installation

- **Health Check**: `http://PI_IP:3002/health`
- **Entities**: `http://PI_IP:3002/api/entities`
- **Services**: `http://PI_IP:3002/api/services/call`
- **History**: `http://PI_IP:3002/api/history`

## 🔐 Sécurité

- **Permissions**: Fichier .env avec permissions 600 (lecture seule par le propriétaire)
- **Isolation**: Service systemd avec restrictions de sécurité
- **Token sécurisé**: Saisie du token en mode masqué (password prompt)

## 🛠️ Dépannage

### Vérifier l'Installation
```bash
./scripts/check_installation.sh
```

### Logs du Service
```bash
journalctl -u homeassistant-mcp-server -f
```

### Test Manuel
```bash
cd /opt/homeassistant-mcp-server
source venv/bin/activate
python http_server.py
```

### Configuration
```bash
sudo nano /opt/homeassistant-mcp-server/.env
```

Ces améliorations rendent l'installation beaucoup plus robuste et user-friendly, avec une configuration HTTP complète prête pour l'intégration avec les services IA !