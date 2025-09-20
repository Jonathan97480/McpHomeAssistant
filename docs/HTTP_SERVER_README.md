# Home Assistant MCP HTTP Server

Ce serveur HTTP expose les fonctionnalités du serveur MCP Home Assistant via une API REST, permettant son utilisation standalone ou comme service sur Raspberry Pi.

## 🚀 Démarrage rapide

### Prérequis

- Python 3.11+
- Home Assistant avec un token d'accès long terme
- Dépendances Python : `aiohttp`, `python-dotenv`

### Configuration

1. Créez un fichier `.env` avec votre configuration Home Assistant :
```env
HASS_URL=http://your-homeassistant-ip:8123
HASS_TOKEN=your-long-lived-access-token
```

2. Installez les dépendances :
```bash
pip install aiohttp python-dotenv
```

### Lancement en mode développement

```bash
python start_dev_server.py
```

Le serveur sera accessible sur `http://localhost:3000`

### Test du serveur

```bash
python test_http_server.py
```

## 📚 API Endpoints

### Health Check
- **GET** `/health`
- Vérifie que le serveur et la connexion Home Assistant sont fonctionnels

### Entités
- **GET** `/api/entities` - Liste toutes les entités
- **GET** `/api/entities/{entity_id}` - Détails d'une entité spécifique

### Services
- **POST** `/api/services/call` - Appelle un service Home Assistant
  ```json
  {
    "domain": "light",
    "service": "turn_on",
    "service_data": {
      "entity_id": "light.living_room"
    }
  }
  ```

### Historique
- **GET** `/api/history?start_time={timestamp}&end_time={timestamp}` - Récupère l'historique

## 🔧 Installation sur Raspberry Pi

### Installation automatique

```bash
curl -sSL https://raw.githubusercontent.com/your-repo/homeassistant-mcp-server/main/install.sh | bash
```

### Installation manuelle

1. Clonez le repository :
```bash
git clone https://github.com/your-repo/homeassistant-mcp-server.git
cd homeassistant-mcp-server
```

2. Créez un environnement virtuel :
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurez les variables d'environnement :
```bash
cp .env.raspberry_pi .env
# Éditez .env avec vos paramètres
```

5. Créez et démarrez le service :
```bash
sudo cp homeassistant-mcp.service /etc/systemd/system/
sudo systemctl enable homeassistant-mcp
sudo systemctl start homeassistant-mcp
```

## 🔍 Monitoring

### Vérifier le statut du service
```bash
sudo systemctl status homeassistant-mcp
```

### Voir les logs
```bash
sudo journalctl -u homeassistant-mcp -f
```

### Tester la connectivité
```bash
curl http://localhost:3000/health
```

## 🛠️ Développement

### Structure du projet
```
homeassistant-mcp-server/
├── http_server.py          # Serveur HTTP principal
├── start_dev_server.py     # Launcher pour développement
├── test_http_server.py     # Tests automatisés
├── install.sh              # Script d'installation Raspberry Pi
├── launcher.py             # Wrapper pour le service systemd
├── homeassistant-mcp.service # Configuration systemd
└── requirements.txt        # Dépendances Python
```

### Fonctionnalités

- **API REST complète** pour toutes les fonctionnalités Home Assistant
- **Support CORS** pour intégration web
- **Gestion d'erreurs robuste** avec logging détaillé
- **Health checks** pour monitoring
- **Service systemd** pour auto-démarrage
- **Tests automatisés** pour validation

### Architecture

Le serveur HTTP agit comme un wrapper autour du client Home Assistant MCP :
1. Reçoit les requêtes HTTP REST
2. Traduit en appels vers l'API Home Assistant
3. Retourne les réponses au format JSON
4. Gère l'authentification et les erreurs

## 🔐 Sécurité

- Utilisez HTTPS en production
- Configurez un reverse proxy (nginx) si nécessaire
- Limitez l'accès réseau au serveur
- Gardez votre token Home Assistant sécurisé

## 🐛 Dépannage

### Le serveur ne démarre pas
1. Vérifiez la configuration `.env`
2. Testez la connectivité Home Assistant : `curl -H "Authorization: Bearer YOUR_TOKEN" http://YOUR_HASS_URL/api/`
3. Vérifiez les logs : `python start_dev_server.py`

### Erreurs de connexion
1. Vérifiez l'URL et le port Home Assistant
2. Validez le token d'accès
3. Vérifiez les paramètres réseau/firewall

### Performance
1. Le serveur utilise des connexions async pour de meilleures performances
2. Configurez des timeouts appropriés selon votre réseau
3. Utilisez un reverse proxy pour la mise en cache si nécessaire