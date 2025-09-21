#!/bin/bash
# =============================================================================
# Script de Déploiement Phase 3.4 - Raspberry Pi
# =============================================================================
# Ce script installe la nouvelle version Phase 3.4 sur Raspberry Pi
# PRÉREQUIS: Exécuter migrate_pi.sh d'abord
# UTILISATION: ./deploy_pi.sh
# =============================================================================

set -e

# Configuration
PROJECT_DIR="/home/pi/homeassistant-mcp-server-v3.4"
BACKUP_DIR=$(ls -td /home/pi/backup-* 2>/dev/null | head -n1)
SERVICE_NAME="homeassistant-mcp-v3.4"
LOG_FILE="/home/pi/deployment.log"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Déploiement Phase 3.4 - Raspberry Pi ===${NC}"
echo "Début: $(date)" | tee -a $LOG_FILE

# =============================================================================
# 1. VÉRIFICATIONS PRÉALABLES
# =============================================================================
echo -e "\n${YELLOW}✅ 1. VÉRIFICATIONS PRÉALABLES${NC}"

# Vérifier que le répertoire existe
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Répertoire $PROJECT_DIR non trouvé${NC}"
    echo "Exécutez d'abord migrate_pi.sh"
    exit 1
fi

# Vérifier les fichiers Phase 3.4
REQUIRED_FILES=("bridge_server.py" "auth_manager.py" "requirements.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$PROJECT_DIR/$file" ]; then
        echo -e "${RED}❌ Fichier manquant: $file${NC}"
        echo "Transférez tous les fichiers Phase 3.4 d'abord"
        exit 1
    fi
done

echo "✅ Tous les fichiers requis sont présents"

# =============================================================================
# 2. INSTALLATION DES DÉPENDANCES
# =============================================================================
echo -e "\n${YELLOW}📦 2. INSTALLATION DES DÉPENDANCES${NC}"

cd "$PROJECT_DIR"

# Créer un environnement virtuel
echo "🐍 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Mettre à jour pip dans le venv
pip install --upgrade pip

# Installer les dépendances
echo "📦 Installation des dépendances Python..."
pip install -r requirements.txt

echo "✅ Dépendances installées"

# =============================================================================
# 3. RESTAURATION DES CONFIGURATIONS
# =============================================================================
echo -e "\n${YELLOW}⚙️  3. RESTAURATION DES CONFIGURATIONS${NC}"

if [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ]; then
    echo "📁 Restauration depuis: $BACKUP_DIR"
    
    # Restaurer la base de données si elle existe
    if [ -f "$BACKUP_DIR/bridge_data.db" ]; then
        echo "💾 Restauration de la base de données..."
        cp "$BACKUP_DIR/bridge_data.db" "$PROJECT_DIR/"
        echo "   ✓ bridge_data.db restauré"
    fi
    
    # Restaurer les configurations
    if [ -f "$BACKUP_DIR/config.json" ]; then
        echo "⚙️  Restauration des configurations..."
        cp "$BACKUP_DIR/config.json" "$PROJECT_DIR/"
        echo "   ✓ config.json restauré"
    fi
    
    # Restaurer les variables d'environnement
    if [ -f "$BACKUP_DIR/.env" ]; then
        echo "🔐 Restauration des variables d'environnement..."
        cp "$BACKUP_DIR/.env" "$PROJECT_DIR/"
        echo "   ✓ .env restauré"
    fi
    
    echo "✅ Configurations restaurées"
else
    echo "⚠️  Aucune sauvegarde trouvée, configuration par défaut"
fi

# =============================================================================
# 4. CONFIGURATION DU SERVICE SYSTEMD
# =============================================================================
echo -e "\n${YELLOW}🔧 4. CONFIGURATION DU SERVICE SYSTEMD${NC}"

# Créer le fichier de service
cat > /tmp/$SERVICE_NAME.service << EOF
[Unit]
Description=Home Assistant MCP Server Phase 3.4
After=network.target
StartLimitBurst=5
StartLimitIntervalSec=10

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python bridge_server.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Installer le service
echo "📋 Installation du service systemd..."
sudo mv /tmp/$SERVICE_NAME.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

echo "✅ Service systemd configuré"

# =============================================================================
# 5. TESTS ET DÉMARRAGE
# =============================================================================
echo -e "\n${YELLOW}🚀 5. TESTS ET DÉMARRAGE${NC}"

# Test de syntaxe Python
echo "🔍 Vérification de la syntaxe..."
python -m py_compile bridge_server.py
python -m py_compile auth_manager.py
echo "✅ Syntaxe Python valide"

# Démarrer le service
echo "🚀 Démarrage du service..."
sudo systemctl start $SERVICE_NAME

# Attendre le démarrage
sleep 5

# Vérifier le statut
echo "📊 Vérification du statut..."
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service démarré avec succès"
    
    # Tester la connectivité
    echo "🌐 Test de connectivité..."
    sleep 3
    
    if curl -f http://localhost:3003/health >/dev/null 2>&1; then
        echo "✅ API accessible sur le port 3003"
    else
        echo "⚠️  API non accessible, vérifiez les logs"
    fi
    
else
    echo "❌ Échec du démarrage du service"
    echo "Logs:"
    sudo journalctl -u $SERVICE_NAME --no-pager -n 20
fi

# =============================================================================
# 6. INFORMATIONS FINALES
# =============================================================================
echo -e "\n${GREEN}🎉 DÉPLOIEMENT PHASE 3.4 TERMINÉ${NC}"

echo -e "\n${BLUE}📋 INFORMATIONS DE SERVICE:${NC}"
echo "• Nom du service: $SERVICE_NAME"
echo "• Répertoire: $PROJECT_DIR"
echo "• Log de déploiement: $LOG_FILE"

echo -e "\n${BLUE}🔧 COMMANDES UTILES:${NC}"
echo "• Statut: sudo systemctl status $SERVICE_NAME"
echo "• Logs: sudo journalctl -u $SERVICE_NAME -f"
echo "• Redémarrer: sudo systemctl restart $SERVICE_NAME"
echo "• Arrêter: sudo systemctl stop $SERVICE_NAME"

echo -e "\n${BLUE}🌐 ACCÈS WEB:${NC}"
echo "• Dashboard: http://[IP_RASPBERRY]:3003"
echo "• API Health: http://[IP_RASPBERRY]:3003/health"
echo "• Login par défaut: admin / Admin123!"

echo -e "\n${GREEN}✅ Phase 3.4 déployée avec succès sur Raspberry Pi!${NC}"
echo "Fin: $(date)" | tee -a $LOG_FILE