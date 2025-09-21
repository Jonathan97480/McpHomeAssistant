# 🍓 Installation sur Raspberry Pi - Guide Complet

## 📋 **Vue d'ensemble**
Ce guide vous permet d'installer et configurer le serveur MCP Bridge avec interface web sur votre Raspberry Pi.

## 🔧 **Prérequis Système**

### **Raspberry Pi recommandé**
- **Raspberry Pi 4** (2GB RAM minimum, 4GB recommandé)
- **Raspberry Pi OS Lite** ou Desktop (Debian 11/12)
- **Carte SD** 32GB minimum (Classe 10)
- **Connexion Internet** stable

### **Vérification système**
```bash
# Vérifier la version du système
cat /etc/os-release

# Vérifier l'espace disque (minimum 2GB libre)
df -h

# Vérifier la mémoire (minimum 1GB disponible)
free -h

# Vérifier Python (doit être 3.8+)
python3 --version
```

## 📦 **Installation des Dépendances**

### **1. Mise à jour du système**
```bash
sudo apt update && sudo apt upgrade -y
```

### **2. Installation Python et outils**
```bash
# Installation Python 3 et pip
sudo apt install python3 python3-pip python3-venv git -y

# Installation des dépendances système
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y

# Installation SQLite (normalement déjà présent)
sudo apt install sqlite3 -y
```

### **3. Installation Node.js (optionnel pour développement)**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
```

## 🚀 **Installation du Projet**

### **1. Clonage du repository**
```bash
# Aller dans le dossier home
cd ~

# Cloner le projet
git clone https://github.com/Jonathan97480/McpHomeAssistant.git

# Aller dans le dossier
cd McpHomeAssistant
```

### **2. Création environnement virtuel**
```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Mettre à jour pip
pip install --upgrade pip
```

### **3. Installation des dépendances Python**
```bash
# Installation des packages requis
pip install fastapi uvicorn pydantic httpx
pip install aiohttp cryptography
pip install bcrypt python-jose[cryptography] python-multipart passlib
pip install email-validator
pip install requests  # Pour les tests

# Vérifier l'installation
pip list
```

## ⚙️ **Configuration**

### **1. Vérification des fichiers**
```bash
# Vérifier que tous les fichiers sont présents
ls -la

# Vérifier la structure web
ls -la web/
ls -la web/static/
ls -la web/templates/
```

### **2. Test d'import Python**
```bash
# Tester l'import du serveur
python3 -c "import bridge_server; print('✅ Import réussi')"
```

### **3. Configuration des ports**
```bash
# Vérifier que le port 8080 est libre
sudo netstat -tulpn | grep :8080

# Si occupé, modifier dans bridge_server.py ou start_server.py
# Le port par défaut est 8080
```

## 🏃 **Démarrage du Serveur**

### **1. Premier démarrage (test)**
```bash
# Activer l'environnement virtuel si pas déjà fait
source venv/bin/activate

# Démarrer le serveur en mode test
python3 start_server.py
```

### **2. Vérification du fonctionnement**
Dans un autre terminal :
```bash
# Test simple
curl http://localhost:8080/health

# Test complet (si requests installé)
cd ~/McpHomeAssistant
source venv/bin/activate
python3 test_simple.py
```

### **3. Accès depuis un autre appareil**
```bash
# Trouver l'IP du Raspberry Pi
hostname -I

# Accéder depuis votre ordinateur/téléphone
# http://IP_DU_RPI:8080
# Exemple: http://192.168.1.100:8080
```

## 🔒 **Configuration Sécurisée**

### **1. Utilisateur dédié (recommandé)**
```bash
# Créer un utilisateur pour le service
sudo useradd -m -s /bin/bash mcpbridge
sudo usermod -aG sudo mcpbridge

# Copier le projet vers le nouvel utilisateur
sudo cp -r ~/McpHomeAssistant /home/mcpbridge/
sudo chown -R mcpbridge:mcpbridge /home/mcpbridge/McpHomeAssistant
```

### **2. Configuration firewall**
```bash
# Installer ufw si pas présent
sudo apt install ufw -y

# Configurer le firewall
sudo ufw allow ssh
sudo ufw allow 8080/tcp
sudo ufw enable

# Vérifier les règles
sudo ufw status
```

### **3. Configuration SSL (optionnel)**
```bash
# Installer certbot pour Let's Encrypt
sudo apt install certbot -y

# OU utiliser un reverse proxy Nginx
sudo apt install nginx -y
```

## 🚀 **Service Systemd (Démarrage Automatique)**

### **1. Créer le fichier service**
```bash
sudo nano /etc/systemd/system/mcpbridge.service
```

### **2. Contenu du fichier service**
```ini
[Unit]
Description=MCP Bridge Server with Web Interface
After=network.target

[Service]
Type=simple
User=mcpbridge
Group=mcpbridge
WorkingDirectory=/home/mcpbridge/McpHomeAssistant
Environment=PATH=/home/mcpbridge/McpHomeAssistant/venv/bin
ExecStart=/home/mcpbridge/McpHomeAssistant/venv/bin/python start_server.py
Restart=always
RestartSec=10

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mcpbridge

# Sécurité
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/home/mcpbridge/McpHomeAssistant

[Install]
WantedBy=multi-user.target
```

### **3. Activation du service**
```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer le service
sudo systemctl enable mcpbridge

# Démarrer le service
sudo systemctl start mcpbridge

# Vérifier le statut
sudo systemctl status mcpbridge

# Voir les logs
sudo journalctl -u mcpbridge -f
```

## 📊 **Monitoring et Logs**

### **1. Logs du système**
```bash
# Logs du service
sudo journalctl -u mcpbridge --since today

# Logs en temps réel
sudo journalctl -u mcpbridge -f

# Logs d'erreur uniquement
sudo journalctl -u mcpbridge -p err
```

### **2. Monitoring système**
```bash
# Utilisation CPU/Mémoire
top
htop  # Si installé: sudo apt install htop

# Espace disque
df -h

# Processus du serveur
ps aux | grep python
```

### **3. Scripts de maintenance**
```bash
# Créer un script de sauvegarde
cat > ~/backup_mcpbridge.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf ~/backups/mcpbridge_$DATE.tar.gz -C /home/mcpbridge McpHomeAssistant
echo "Backup créé: mcpbridge_$DATE.tar.gz"
EOF

chmod +x ~/backup_mcpbridge.sh
mkdir -p ~/backups
```

## 🌐 **Accès à l'Interface Web**

### **1. URL d'accès**
```
http://IP_DU_RPI:8080
```

### **2. Compte administrateur par défaut**
- **Utilisateur** : `admin`
- **Mot de passe** : `Admin123!`

⚠️ **Changez immédiatement ce mot de passe** après la première connexion !

### **3. Configuration Home Assistant**
1. Aller dans **Configuration**
2. Ajouter votre instance Home Assistant :
   - URL : `http://IP_HOME_ASSISTANT:8123`
   - Token : Générer un token Long-Term dans HA
3. Tester la connexion

## 🔧 **Résolution de Problèmes**

### **Problèmes courants**

#### **Port déjà utilisé**
```bash
# Changer le port dans start_server.py
nano start_server.py
# Modifier: port=8080 vers port=8081
```

#### **Erreur de permissions**
```bash
# Corriger les permissions
sudo chown -R mcpbridge:mcpbridge /home/mcpbridge/McpHomeAssistant
chmod +x start_server.py
```

#### **Erreur de mémoire**
```bash
# Augmenter le swap si RAM insuffisante
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### **Base de données corrompue**
```bash
# Supprimer et recréer la base
rm bridge_data.db
python3 -c "from database import create_tables; create_tables()"
```

### **Logs de debug**
```bash
# Démarrer en mode debug
source venv/bin/activate
python3 bridge_server.py --debug

# Ou avec logs détaillés
PYTHONPATH=. python3 -m uvicorn bridge_server:app --host 0.0.0.0 --port 8080 --log-level debug
```

## 📈 **Performance Raspberry Pi**

### **Optimisations recommandées**

#### **1. Configuration mémoire**
```bash
# Augmenter la split mémoire GPU/CPU
sudo nano /boot/config.txt
# Ajouter: gpu_mem=16
```

#### **2. Désactiver services inutiles**
```bash
# Désactiver Bluetooth si pas utilisé
sudo systemctl disable bluetooth
sudo systemctl disable hciuart

# Désactiver WiFi si Ethernet utilisé
sudo systemctl disable wpa_supplicant
```

#### **3. Configuration base de données**
```bash
# Optimiser SQLite pour Raspberry Pi
# (Déjà configuré dans database.py)
```

## 🎯 **Tests de Performance**

### **Test de charge simple**
```bash
# Installer Apache bench
sudo apt install apache2-utils -y

# Test de charge basic
ab -n 100 -c 10 http://localhost:8080/health

# Test avec authentification
# (Configurer avec token JWT)
```

### **Monitoring ressources**
```bash
# Script de monitoring
cat > ~/monitor.sh << 'EOF'
#!/bin/bash
while true; do
    echo "=== $(date) ==="
    echo "CPU: $(vcgencmd measure_temp)"
    echo "RAM: $(free -m | grep Mem | awk '{print $3"/"$2" MB"}')"
    echo "Disk: $(df -h / | tail -1 | awk '{print $3"/"$2" ("$5")"}')"
    echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
    echo "---"
    sleep 60
done
EOF

chmod +x ~/monitor.sh
```

## ✅ **Checklist Final**

- [ ] Raspberry Pi mis à jour
- [ ] Python 3.8+ installé
- [ ] Dépendances système installées
- [ ] Repository cloné
- [ ] Environnement virtuel créé
- [ ] Dépendances Python installées
- [ ] Import du serveur testé
- [ ] Serveur démarre sans erreur
- [ ] Interface web accessible
- [ ] Tests automatiques passent
- [ ] Service systemd configuré (optionnel)
- [ ] Firewall configuré
- [ ] Compte admin sécurisé
- [ ] Home Assistant connecté
- [ ] Backup configuré

## 🎊 **Installation Terminée !**

Votre serveur MCP Bridge est maintenant installé et fonctionnel sur Raspberry Pi !

**Accès** : http://IP_DU_RPI:8080  
**Admin** : admin / Admin123! (à changer)

N'oubliez pas de :
1. Changer le mot de passe admin
2. Configurer votre Home Assistant
3. Tester toutes les fonctionnalités
4. Configurer des sauvegardes régulières

Pour tout problème, consultez les logs avec : `sudo journalctl -u mcpbridge -f`