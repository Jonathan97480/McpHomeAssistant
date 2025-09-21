#!/bin/bash
# Script de déploiement des corrections d'authentification sur Pi avec utilisateur beroute

echo "🚀 Déploiement des corrections d'authentification sur Pi..."

PI_USER="beroute"
PI_HOST="192.168.1.22"
PI_PATH="/home/beroute/phase3"

# 1. Transfert du fichier bridge_server.py corrigé
echo "📤 Transfert de bridge_server.py..."
scp bridge_server.py ${PI_USER}@${PI_HOST}:${PI_PATH}/

# 2. Transfert du script de test
echo "📤 Transfert du script de test..."
scp test_fix_auth.py ${PI_USER}@${PI_HOST}:${PI_PATH}/

# 3. Redémarrage du service
echo "🔄 Redémarrage du service..."
ssh ${PI_USER}@${PI_HOST} "sudo systemctl restart bridge-server"

# 4. Attendre que le service démarre
echo "⏳ Attente du démarrage du service..."
sleep 5

# 5. Vérification du statut
echo "🔍 Vérification du statut..."
ssh ${PI_USER}@${PI_HOST} "sudo systemctl status bridge-server --no-pager -l"

echo "✅ Déploiement terminé!"