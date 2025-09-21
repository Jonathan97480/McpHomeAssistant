# 🚀 Installation Rapide sur Raspberry Pi

## Installation Automatique (Recommandée)

### 1. Connexion SSH au Raspberry Pi
```bash
ssh pi@IP_DU_RPI
# ou ssh votre_utilisateur@IP_DU_RPI
```

### 2. Installation en une commande
```bash
curl -fsSL https://raw.githubusercontent.com/Jonathan97480/McpHomeAssistant/master/install.sh | bash
```

### 3. Accès à l'interface
- **URL** : http://IP_DU_RPI:8080
- **Login** : admin
- **Password** : Admin123!

⚠️ **Changez immédiatement le mot de passe !**

---

## Installation Manuelle

### 1. Cloner le projet
```bash
cd ~
git clone https://github.com/Jonathan97480/McpHomeAssistant.git
cd McpHomeAssistant
chmod +x install.sh
./install.sh
```

Ou installation complète automatique :

```bash
sudo apt update && sudo apt install python3-pip python3-venv git -y
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pydantic httpx aiohttp cryptography bcrypt python-jose[cryptography] python-multipart passlib email-validator requests
```

### 2. Démarrer le serveur
```bash
python3 start_server.py
```

### 3. Tester l'installation
```bash
python3 test_simple.py
```

---

## 🔧 Configuration Home Assistant

1. **Générer un token Long-Term** dans Home Assistant :
   - Profil → Tokens d'accès de longue durée → Créer un token

2. **Configurer dans l'interface web** :
   - Aller sur http://IP_DU_RPI:8080
   - Se connecter avec admin/Admin123!
   - Menu **Configuration** → Ajouter Home Assistant
   - URL : `http://IP_HOME_ASSISTANT:8123`
   - Token : Coller le token généré
   - Tester la connexion

---

## 🛠️ Commandes Utiles

### Service (si installé)
```bash
sudo systemctl status mcpbridge    # Voir le statut
sudo systemctl restart mcpbridge   # Redémarrer
sudo systemctl stop mcpbridge      # Arrêter
sudo journalctl -u mcpbridge -f    # Logs en temps réel
```

### Manuel
```bash
cd ~/McpHomeAssistant
source venv/bin/activate
python3 start_server.py           # Démarrer manuellement
python3 test_complete.py          # Tests complets
```

### Debugging
```bash
# Logs détaillés
python3 bridge_server.py --log-level debug

# Test de connexion
curl http://localhost:8080/health

# Vérifier les ports
sudo netstat -tulpn | grep :8080
```

---

## ⚠️ Résolution de Problèmes

### Port déjà utilisé
```bash
# Changer le port dans start_server.py
nano start_server.py
# Modifier port=8080 vers port=8081
```

### Erreurs de permissions
```bash
sudo chown -R $USER:$USER ~/McpHomeAssistant
chmod +x start_server.py
```

### Mémoire insuffisante
```bash
# Ajouter du swap
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Base de données corrompue
```bash
rm bridge_data.db
# Redémarrer le serveur pour recréer la DB
```

---

## 📊 Fonctionnalités Disponibles

### ✅ Interface Web Complète
- **Dashboard** avec métriques temps réel
- **Gestion des permissions** par outil MCP
- **Configuration Home Assistant** multi-instance
- **Visualisation des logs** avec filtrage
- **Panel d'administration** utilisateurs
- **Tests des outils MCP** en direct

### ✅ API REST Complète
- **15+ endpoints** pour toutes les fonctionnalités
- **Authentification JWT** sécurisée
- **Export de données** CSV/JSON
- **Monitoring système** intégré

### ✅ Sécurité Intégrée
- **Authentification** utilisateur obligatoire
- **Permissions granulaires** READ/WRITE/EXECUTE
- **Chiffrement des tokens** Home Assistant
- **Firewall** configuré automatiquement

---

## 🎯 Prêt pour Production

Cette version est stable et prête pour utilisation avec votre Home Assistant !

**Support** : Consultez `RASPBERRY_PI_INSTALL.md` pour le guide complet

**GitHub** : https://github.com/Jonathan97480/McpHomeAssistant