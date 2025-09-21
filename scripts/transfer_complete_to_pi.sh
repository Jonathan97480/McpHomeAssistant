#!/bin/bash
# =============================================================================
# Script de Transfert Complet - Phase 3.4 vers Raspberry Pi
# =============================================================================
# Transfère TOUS les fichiers du projet local vers le Raspberry Pi
# UTILISATION: ./transfer_complete_to_pi.sh [IP_RASPBERRY] [USER]
# EXEMPLE: ./transfer_complete_to_pi.sh 192.168.1.22 beroute
# =============================================================================

set -e

# Configuration par défaut
DEFAULT_PI_IP="192.168.1.22"
DEFAULT_PI_USER="beroute"
LOCAL_PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE_PROJECT_DIR="/home/\$PI_USER/homeassistant-mcp-server-v3.4"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Arguments
PI_IP="${1:-$DEFAULT_PI_IP}"
PI_USER="${2:-$DEFAULT_PI_USER}"

echo -e "${BLUE}=== Transfert Complet Phase 3.4 vers Raspberry Pi ===${NC}"
echo "🔗 Destination: ${PI_USER}@${PI_IP}"
echo "📁 Projet local: ${LOCAL_PROJECT_DIR}"
echo "📁 Destination: /home/${PI_USER}/homeassistant-mcp-server-v3.4"
echo

# =============================================================================
# 1. VÉRIFICATIONS PRÉALABLES
# =============================================================================
echo -e "${YELLOW}🔍 1. VÉRIFICATIONS PRÉALABLES${NC}"

# Vérifier le projet local
if [ ! -f "$LOCAL_PROJECT_DIR/bridge_server.py" ]; then
    echo -e "${RED}❌ Ce script doit être exécuté depuis le répertoire du projet${NC}"
    exit 1
fi

# Vérifier la complétude du projet local
echo "✅ Vérification de la complétude du projet local..."
python3 "$LOCAL_PROJECT_DIR/scripts/check_project_completeness.py"
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Le projet local n'est pas complet${NC}"
    echo "Corrigez les problèmes avant le transfert"
    exit 1
fi

# Test de connectivité
echo "🔗 Test de connectivité vers ${PI_USER}@${PI_IP}..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes ${PI_USER}@${PI_IP} exit 2>/dev/null; then
    echo -e "${RED}❌ Impossible de se connecter au Raspberry Pi${NC}"
    echo "Vérifiez l'IP, l'utilisateur et les clés SSH"
    exit 1
fi
echo "✅ Connectivité OK"

# =============================================================================
# 2. PRÉPARATION DU TRANSFERT
# =============================================================================
echo -e "\n${YELLOW}📦 2. PRÉPARATION DU TRANSFERT${NC}"

# Créer le répertoire de destination
echo "📁 Création du répertoire de destination..."
ssh ${PI_USER}@${PI_IP} "mkdir -p /home/${PI_USER}/homeassistant-mcp-server-v3.4"

# =============================================================================
# 3. TRANSFERT DES FICHIERS
# =============================================================================
echo -e "\n${YELLOW}🚀 3. TRANSFERT DES FICHIERS${NC}"

# Fichiers et dossiers à exclure du transfert
EXCLUDE_LIST=(
    "__pycache__"
    ".git"
    "*.pyc"
    ".pytest_cache"
    "*.log"
    "logs/*"
    ".env"
    "bridge_data.db"
    "*.tmp"
    ".vscode"
    ".idea"
)

# Construire les options d'exclusion pour rsync
EXCLUDE_OPTS=""
for item in "${EXCLUDE_LIST[@]}"; do
    EXCLUDE_OPTS="$EXCLUDE_OPTS --exclude=$item"
done

echo "📂 Transfert du projet complet (avec exclusions intelligentes)..."
echo "   Exclusions: ${EXCLUDE_LIST[*]}"

# Transfert avec rsync pour une synchronisation efficace
rsync -avz --progress \
    --delete \
    $EXCLUDE_OPTS \
    "$LOCAL_PROJECT_DIR/" \
    ${PI_USER}@${PI_IP}:/home/${PI_USER}/homeassistant-mcp-server-v3.4/

echo -e "${GREEN}✅ Transfert terminé${NC}"

# =============================================================================
# 4. VÉRIFICATION POST-TRANSFERT
# =============================================================================
echo -e "\n${YELLOW}🔍 4. VÉRIFICATION POST-TRANSFERT${NC}"

# Vérifier les fichiers critiques
CRITICAL_FILES=(
    "bridge_server.py"
    "auth_manager.py"
    "database.py"
    "requirements.txt"
    "web/templates/login.html"
    "web/static/css/main.css"
    "web/static/js/dashboard.js"
    "scripts/deploy_pi.sh"
)

echo "📋 Vérification des fichiers critiques sur le Pi..."
MISSING_FILES=()
for file in "${CRITICAL_FILES[@]}"; do
    if ssh ${PI_USER}@${PI_IP} "[ ! -f /home/${PI_USER}/homeassistant-mcp-server-v3.4/$file ]"; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ Tous les fichiers critiques sont présents${NC}"
else
    echo -e "${RED}❌ Fichiers manquants:${NC}"
    for file in "${MISSING_FILES[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

# Vérifier la structure web
echo "🌐 Vérification de la structure web..."
WEB_CHECK=$(ssh ${PI_USER}@${PI_IP} "cd /home/${PI_USER}/homeassistant-mcp-server-v3.4 && find web/ -name '*.html' | wc -l" 2>/dev/null || echo "0")
if [ "$WEB_CHECK" -ge 8 ]; then
    echo -e "${GREEN}✅ Structure web complète ($WEB_CHECK templates trouvés)${NC}"
else
    echo -e "${RED}❌ Structure web incomplète (seulement $WEB_CHECK templates)${NC}"
    exit 1
fi

# =============================================================================
# 5. STATISTIQUES DE TRANSFERT
# =============================================================================
echo -e "\n${YELLOW}📊 5. STATISTIQUES DE TRANSFERT${NC}"

# Taille du projet transféré
REMOTE_SIZE=$(ssh ${PI_USER}@${PI_IP} "du -sh /home/${PI_USER}/homeassistant-mcp-server-v3.4" | cut -f1)
REMOTE_FILES=$(ssh ${PI_USER}@${PI_IP} "find /home/${PI_USER}/homeassistant-mcp-server-v3.4 -type f | wc -l")

echo "📁 Taille transférée: $REMOTE_SIZE"
echo "📄 Nombre de fichiers: $REMOTE_FILES"

# =============================================================================
# 6. INSTRUCTIONS SUIVANTES
# =============================================================================
echo -e "\n${GREEN}🎉 TRANSFERT RÉUSSI !${NC}"
echo
echo -e "${BLUE}📋 ÉTAPES SUIVANTES:${NC}"
echo "1. Se connecter au Pi:"
echo "   ssh ${PI_USER}@${PI_IP}"
echo
echo "2. Exécuter le déploiement:"
echo "   cd /home/${PI_USER}/homeassistant-mcp-server-v3.4"
echo "   chmod +x scripts/deploy_pi.sh"
echo "   ./scripts/deploy_pi.sh"
echo
echo "3. Ou utiliser le script de migration complet:"
echo "   chmod +x scripts/migrate_pi.sh"
echo "   ./scripts/migrate_pi.sh"
echo
echo -e "${YELLOW}💡 CONSEIL:${NC} Le projet est maintenant complet sur le Pi avec TOUS les fichiers"
echo "   incluant la structure web/, les templates et les fichiers statiques."