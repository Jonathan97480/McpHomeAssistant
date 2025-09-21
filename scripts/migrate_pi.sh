#!/bin/bash
# =============================================================================
# Script de Migration Raspberry Pi - Phase 3.4
# =============================================================================
# Ce script gère la transition de l'ancienne version vers Phase 3.4
# UTILISATION: ./migrate_pi.sh
# =============================================================================

set -e  # Arrêt en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
OLD_PROJECT_DIR="/home/pi/homeassistant-mcp-server"
NEW_PROJECT_DIR="/home/pi/homeassistant-mcp-server-v3.4"
BACKUP_DIR="/home/pi/backup-$(date +%Y%m%d-%H%M%S)"
LOG_FILE="/home/pi/migration.log"

echo -e "${BLUE}=== Migration vers Phase 3.4 - Raspberry Pi ===${NC}"
echo "Début: $(date)" | tee -a $LOG_FILE

# =============================================================================
# 1. AUDIT DE L'INSTALLATION ACTUELLE
# =============================================================================
echo -e "\n${YELLOW}📋 1. AUDIT DE L'INSTALLATION ACTUELLE${NC}"

# Vérifier les processus en cours
echo "🔍 Processus Python en cours:"
ps aux | grep -i python | grep -v grep || echo "Aucun processus Python trouvé"

# Vérifier les ports utilisés
echo -e "\n🔍 Ports en écoute:"
sudo netstat -tlnp | grep -E ':(3002|3003|8080|8000)' || echo "Aucun port MCP détecté"

# Vérifier l'ancienne installation
if [ -d "$OLD_PROJECT_DIR" ]; then
    echo -e "\n📂 Ancienne installation trouvée: $OLD_PROJECT_DIR"
    echo "   Taille: $(du -sh $OLD_PROJECT_DIR | cut -f1)"
    echo "   Fichiers: $(find $OLD_PROJECT_DIR -type f | wc -l)"
    
    # Vérifier les fichiers critiques
    echo -e "\n📋 Fichiers critiques détectés:"
    [ -f "$OLD_PROJECT_DIR/config.json" ] && echo "   ✓ config.json"
    [ -f "$OLD_PROJECT_DIR/bridge_data.db" ] && echo "   ✓ bridge_data.db"
    [ -f "$OLD_PROJECT_DIR/.env" ] && echo "   ✓ .env"
    [ -f "$OLD_PROJECT_DIR/requirements.txt" ] && echo "   ✓ requirements.txt"
else
    echo -e "\n❌ Aucune installation précédente trouvée dans $OLD_PROJECT_DIR"
fi

# =============================================================================
# 2. ARRÊT DES SERVICES EXISTANTS
# =============================================================================
echo -e "\n${YELLOW}⏹️  2. ARRÊT DES SERVICES EXISTANTS${NC}"

# Arrêter les processus Python liés au projet
echo "🛑 Arrêt des processus Python MCP..."
pkill -f "python.*bridge_server" || echo "Aucun bridge_server à arrêter"
pkill -f "python.*mcp" || echo "Aucun processus MCP à arrêter"
pkill -f "uvicorn" || echo "Aucun uvicorn à arrêter"

# Attendre que les processus se terminent
sleep 3

# Vérifier que tout est arrêté
REMAINING=$(ps aux | grep -E "(bridge_server|mcp|uvicorn)" | grep -v grep | wc -l)
if [ $REMAINING -eq 0 ]; then
    echo "✅ Tous les services sont arrêtés"
else
    echo "⚠️  $REMAINING processus encore actifs"
    ps aux | grep -E "(bridge_server|mcp|uvicorn)" | grep -v grep
fi

# =============================================================================
# 3. SAUVEGARDE DES DONNÉES IMPORTANTES
# =============================================================================
echo -e "\n${YELLOW}💾 3. SAUVEGARDE DES DONNÉES${NC}"

if [ -d "$OLD_PROJECT_DIR" ]; then
    echo "📁 Création du répertoire de sauvegarde: $BACKUP_DIR"
    mkdir -p $BACKUP_DIR
    
    # Sauvegarder les fichiers critiques
    echo "💾 Sauvegarde en cours..."
    
    [ -f "$OLD_PROJECT_DIR/config.json" ] && cp "$OLD_PROJECT_DIR/config.json" "$BACKUP_DIR/" && echo "   ✓ config.json sauvegardé"
    [ -f "$OLD_PROJECT_DIR/bridge_data.db" ] && cp "$OLD_PROJECT_DIR/bridge_data.db" "$BACKUP_DIR/" && echo "   ✓ bridge_data.db sauvegardé"
    [ -f "$OLD_PROJECT_DIR/.env" ] && cp "$OLD_PROJECT_DIR/.env" "$BACKUP_DIR/" && echo "   ✓ .env sauvegardé"
    [ -d "$OLD_PROJECT_DIR/logs" ] && cp -r "$OLD_PROJECT_DIR/logs" "$BACKUP_DIR/" && echo "   ✓ logs sauvegardés"
    
    # Backup complet de l'ancienne version
    echo "📦 Archivage complet de l'ancienne version..."
    tar -czf "$BACKUP_DIR/old_installation.tar.gz" -C $(dirname $OLD_PROJECT_DIR) $(basename $OLD_PROJECT_DIR)
    echo "   ✓ Archive créée: $BACKUP_DIR/old_installation.tar.gz"
    
    echo "✅ Sauvegarde terminée dans: $BACKUP_DIR"
else
    echo "⚠️  Aucune installation à sauvegarder"
fi

# =============================================================================
# 4. NETTOYAGE DE L'ANCIENNE INSTALLATION
# =============================================================================
echo -e "\n${YELLOW}🧹 4. NETTOYAGE DE L'ANCIENNE INSTALLATION${NC}"

read -p "❓ Voulez-vous supprimer l'ancienne installation? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "$OLD_PROJECT_DIR" ]; then
        echo "🗑️  Suppression de $OLD_PROJECT_DIR..."
        rm -rf "$OLD_PROJECT_DIR"
        echo "✅ Ancienne installation supprimée"
    fi
    
    # Nettoyer les services systemd éventuels
    if systemctl list-unit-files | grep -q "homeassistant-mcp"; then
        echo "🛑 Désactivation du service systemd..."
        sudo systemctl stop homeassistant-mcp || true
        sudo systemctl disable homeassistant-mcp || true
        echo "✅ Service systemd désactivé"
    fi
else
    echo "⏭️  Conservation de l'ancienne installation"
fi

# =============================================================================
# 5. PRÉPARATION POUR LA NOUVELLE VERSION
# =============================================================================
echo -e "\n${YELLOW}🔧 5. PRÉPARATION POUR PHASE 3.4${NC}"

# Créer le répertoire pour la nouvelle version
echo "📁 Création du répertoire: $NEW_PROJECT_DIR"
mkdir -p "$NEW_PROJECT_DIR"

# Vérifier Python et pip
echo "🐍 Vérification de Python..."
python3 --version
pip3 --version

# Mettre à jour pip
echo "⬆️  Mise à jour de pip..."
pip3 install --upgrade pip

# =============================================================================
# 6. INFORMATIONS POUR LA SUITE
# =============================================================================
echo -e "\n${GREEN}✅ MIGRATION PRÉPARÉE AVEC SUCCÈS${NC}"
echo -e "\n${BLUE}📋 ÉTAPES SUIVANTES:${NC}"
echo "1. Transférer les fichiers Phase 3.4 vers: $NEW_PROJECT_DIR"
echo "2. Installer les dépendances: pip3 install -r requirements.txt"
echo "3. Restaurer les configurations depuis: $BACKUP_DIR"
echo "4. Configurer et démarrer la nouvelle version"
echo "5. Valider le fonctionnement"

echo -e "\n${BLUE}📂 RÉPERTOIRES:${NC}"
echo "• Nouvelle installation: $NEW_PROJECT_DIR"
echo "• Sauvegarde: $BACKUP_DIR"
echo "• Log de migration: $LOG_FILE"

echo -e "\n${GREEN}🎯 Prêt pour le déploiement Phase 3.4!${NC}"
echo "Fin: $(date)" | tee -a $LOG_FILE