#!/bin/bash
# ===============================================================================
# McP Bridge - Script d'Installation Unifié pour Raspberry Pi
# Version Phase 3.4 - Interface Web Complète
# ===============================================================================
#
# Ce script installe et configure McP Bridge avec l'interface web complète
# sur Raspberry Pi. Il combine toutes les fonctionnalités précédentes.
#
# Usage: 
#   curl -fsSL https://raw.githubusercontent.com/Jonathan97480/McpHomeAssistant/master/install_unified.sh | bash
#   ou
#   wget -O - https://raw.githubusercontent.com/Jonathan97480/McpHomeAssistant/master/install_unified.sh | bash
#
# ===============================================================================

set -e  # Exit on any error

# ===============================================================================
# CONFIGURATION
# ===============================================================================

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration par défaut
PROJECT_NAME="McpHomeAssistant"
PROJECT_DIR="$HOME/$PROJECT_NAME"
SERVICE_NAME="mcpbridge"
INSTALL_MODE="web"  # web ou mcp (legacy)
WEB_PORT=8080
MCP_PORT=3002
REPO_URL="https://github.com/Jonathan97480/McpHomeAssistant.git"
PYTHON_VERSION="python3"
MIN_PYTHON_VERSION="3.8"

# ===============================================================================
# FONCTIONS UTILITAIRES
# ===============================================================================

# Fonction de log avec horodatage
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✓ $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ✗ $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠ $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] ℹ $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] 🎉 $1${NC}"
}

# Affichage du banner
show_banner() {
    echo -e "${CYAN}"
    echo "==============================================================================="
    echo "                    McP Bridge - Installation Unified"
    echo "                          Phase 3.4 - Interface Web"
    echo "==============================================================================="
    echo -e "${NC}"
    echo "🚀 Installation automatique de McP Bridge avec interface web complète"
    echo "📋 Fonctionnalités:"
    echo "   • Interface web responsive avec dashboard"
    echo "   • API REST complète (25+ endpoints)"
    echo "   • Système d'authentification sécurisé"
    echo "   • Gestion des permissions granulaire"
    echo "   • Configuration multi-instances Home Assistant"
    echo "   • Service systemd intégré"
    echo "   • Tests automatisés"
    echo
}

# Demander confirmation à l'utilisateur
ask_confirmation() {
    local default_choice="Y"
    while true; do
        read -p "$(echo -e ${YELLOW}Continuer l\'installation ? [Y/n]: ${NC})" choice
        choice=${choice:-$default_choice}
        case $choice in
            [Yy]* ) return 0;;
            [Nn]* ) echo "Installation annulée."; exit 0;;
            * ) echo "Répondez par 'y' ou 'n'.";;
        esac
    done
}

# Menu de choix du mode d'installation
choose_installation_mode() {
    echo
    info "Choisissez le mode d'installation:"
    echo "  1) Interface Web (Recommandé) - Port $WEB_PORT"
    echo "  2) MCP Server Legacy - Port $MCP_PORT"
    echo "  3) Installation complète (Web + MCP)"
    echo
    
    while true; do
        read -p "$(echo -e ${YELLOW}Votre choix [1-3]: ${NC})" choice
        case $choice in
            1) INSTALL_MODE="web"; break;;
            2) INSTALL_MODE="mcp"; break;;
            3) INSTALL_MODE="both"; break;;
            *) echo "Choix invalide. Entrez 1, 2 ou 3.";;
        esac
    done
    
    info "Mode sélectionné: $INSTALL_MODE"
}

# ===============================================================================
# VÉRIFICATIONS SYSTÈME
# ===============================================================================

# Vérification des privilèges root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "Ne pas exécuter ce script en tant que root pour des raisons de sécurité."
        error "Utilisez un utilisateur normal. sudo sera utilisé quand nécessaire."
        exit 1
    fi
    
    if ! sudo -n true 2>/dev/null; then
        warn "Vous devrez peut-être entrer votre mot de passe pour sudo"
    fi
    
    log "Utilisateur: $USER"
}

# Vérification du système
check_system() {
    info "Vérification du système..."
    
    # OS
    if [[ -f /etc/debian_version ]]; then
        OS_VERSION=$(cat /etc/debian_version)
        log "Système Debian/Raspbian détecté: $OS_VERSION"
    elif [[ -f /etc/redhat-release ]]; then
        warn "Système RedHat détecté - peut nécessiter des adaptations"
    else
        warn "Système non reconnu - installation au risque de l'utilisateur"
    fi
    
    # Architecture
    ARCH=$(uname -m)
    case $ARCH in
        armv7l) log "Architecture: Raspberry Pi 32-bit (ARMv7)";;
        aarch64) log "Architecture: Raspberry Pi 64-bit (ARM64)";;
        x86_64) warn "Architecture: x86_64 - Non optimal pour Raspberry Pi";;
        *) warn "Architecture non reconnue: $ARCH";;
    esac
    
    # Mémoire
    MEM_TOTAL=$(free -m | awk 'NR==2{print $2}')
    MEM_AVAILABLE=$(free -m | awk 'NR==2{print $7}')
    log "Mémoire: ${MEM_TOTAL}MB total, ${MEM_AVAILABLE}MB disponible"
    
    if [ "$MEM_AVAILABLE" -lt 100 ]; then
        warn "Mémoire faible ($MEM_AVAILABLE MB) - Performance réduite possible"
        if [ "$MEM_TOTAL" -lt 512 ]; then
            error "Mémoire insuffisante pour l'installation"
            exit 1
        fi
    fi
    
    # Espace disque
    DISK_AVAILABLE=$(df -BM "$HOME" | awk 'NR==2 {print $4}' | sed 's/M//')
    log "Espace disque disponible: ${DISK_AVAILABLE}MB"
    
    if [ "$DISK_AVAILABLE" -lt 500 ]; then
        error "Espace disque insuffisant (${DISK_AVAILABLE}MB < 500MB requis)"
        exit 1
    fi
}

# Vérification de Python
check_python() {
    info "Vérification de Python..."
    
    if ! command -v python3 &> /dev/null; then
        error "Python 3 non installé"
        exit 1
    fi
    
    PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log "Version Python: $PYTHON_VER"
    
    # Vérification version minimale
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log "Version Python compatible (>= 3.8)"
    else
        error "Python 3.8+ requis. Version actuelle: $PYTHON_VER"
        exit 1
    fi
    
    # Vérification de pip
    if ! python3 -m pip --version &> /dev/null; then
        warn "pip non disponible - installation nécessaire"
        return 1
    fi
    
    log "pip disponible"
    return 0
}

# Vérification de Git
check_git() {
    if ! command -v git &> /dev/null; then
        warn "Git non installé - installation nécessaire"
        return 1
    fi
    
    log "Git disponible"
    return 0
}

# Vérification Home Assistant (optionnel)
check_homeassistant() {
    info "Vérification Home Assistant..."
    
    if systemctl is-active --quiet homeassistant 2>/dev/null; then
        log "Service Home Assistant actif"
        HA_STATUS="running"
    elif systemctl is-enabled --quiet homeassistant 2>/dev/null; then
        warn "Service Home Assistant installé mais arrêté"
        HA_STATUS="stopped"
    else
        warn "Home Assistant non détecté comme service systemd"
        warn "McP Bridge fonctionnera quand même"
        HA_STATUS="unknown"
    fi
    
    # Détection du port HA
    if netstat -tln 2>/dev/null | grep -q ":8123 "; then
        log "Home Assistant détecté sur le port 8123"
    fi
}

# ===============================================================================
# INSTALLATION DES DÉPENDANCES
# ===============================================================================

# Installation des paquets système
install_system_packages() {
    info "Installation des paquets système..."
    
    # Mise à jour de la liste des paquets
    sudo apt update
    
    # Paquets essentiels
    local packages=(
        "python3"
        "python3-pip"
        "python3-venv"
        "python3-dev"
        "git"
        "curl"
        "wget"
        "build-essential"
        "libffi-dev"
        "libssl-dev"
        "sqlite3"
        "lsof"
        "net-tools"
    )
    
    # Paquets optionnels pour optimisation
    local optional_packages=(
        "htop"
        "ufw"
        "fail2ban"
        "logrotate"
    )
    
    # Installation des paquets essentiels
    for package in "${packages[@]}"; do
        if dpkg -l | grep -q "^ii  $package "; then
            log "$package déjà installé"
        else
            info "Installation de $package..."
            sudo apt install -y "$package"
        fi
    done
    
    # Installation des paquets optionnels (sans échec)
    for package in "${optional_packages[@]}"; do
        if dpkg -l | grep -q "^ii  $package "; then
            log "$package déjà installé"
        else
            if sudo apt install -y "$package" 2>/dev/null; then
                log "$package installé"
            else
                warn "$package non installé (optionnel)"
            fi
        fi
    done
    
    log "Paquets système installés"
}

# ===============================================================================
# GESTION DES SERVICES EXISTANTS
# ===============================================================================

# Arrêt des services existants
stop_existing_services() {
    info "Vérification des services existants..."
    
    # Vérification du service mcpbridge
    if systemctl is-active --quiet $SERVICE_NAME 2>/dev/null; then
        warn "Service $SERVICE_NAME actif - arrêt en cours"
        sudo systemctl stop $SERVICE_NAME
        log "Service $SERVICE_NAME arrêté"
    fi
    
    # Vérification du service legacy
    if systemctl is-active --quiet homeassistant-mcp-server 2>/dev/null; then
        warn "Service legacy homeassistant-mcp-server détecté - arrêt"
        sudo systemctl stop homeassistant-mcp-server
        sudo systemctl disable homeassistant-mcp-server
        log "Service legacy arrêté et désactivé"
    fi
    
    # Arrêt des processus sur les ports
    local ports=("$WEB_PORT" "$MCP_PORT")
    for port in "${ports[@]}"; do
        if lsof -ti:$port &>/dev/null; then
            warn "Processus détecté sur le port $port - arrêt forcé"
            sudo kill -9 $(lsof -ti:$port) 2>/dev/null || true
            log "Port $port libéré"
        fi
    done
}

# ===============================================================================
# INSTALLATION DU PROJET
# ===============================================================================

# Sauvegarde de l'installation existante
backup_existing_installation() {
    if [ -d "$PROJECT_DIR" ]; then
        local backup_dir="${PROJECT_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
        warn "Installation existante détectée"
        info "Création de la sauvegarde: $backup_dir"
        
        mv "$PROJECT_DIR" "$backup_dir"
        log "Sauvegarde créée"
        
        # Sauvegarde de la base de données si elle existe
        if [ -f "$backup_dir/bridge_data.db" ]; then
            cp "$backup_dir/bridge_data.db" "$HOME/bridge_data.db.backup" 2>/dev/null || true
            log "Base de données sauvegardée"
        fi
    fi
}

# Clonage du projet
clone_project() {
    info "Clonage du projet depuis GitHub..."
    
    if ! git clone "$REPO_URL" "$PROJECT_DIR"; then
        error "Échec du clonage depuis $REPO_URL"
        exit 1
    fi
    
    cd "$PROJECT_DIR"
    log "Projet cloné dans $PROJECT_DIR"
    
    # Affichage des informations du commit
    local commit_hash=$(git rev-parse --short HEAD)
    local commit_date=$(git log -1 --format="%ci")
    info "Commit: $commit_hash ($commit_date)"
}

# ===============================================================================
# CONFIGURATION PYTHON
# ===============================================================================

# Configuration de l'environnement virtuel Python
setup_python_environment() {
    info "Configuration de l'environnement Python..."
    
    cd "$PROJECT_DIR"
    
    # Création de l'environnement virtuel
    if [ -d "venv" ]; then
        warn "Environnement virtuel existant - suppression"
        rm -rf venv
    fi
    
    python3 -m venv venv
    log "Environnement virtuel créé"
    
    # Activation et mise à jour
    source venv/bin/activate
    
    # Mise à jour de pip
    pip install --upgrade pip setuptools wheel
    log "pip mis à jour"
    
    # Installation des dépendances selon le mode
    local requirements=""
    case $INSTALL_MODE in
        "web"|"both")
            requirements="fastapi uvicorn pydantic httpx aiohttp cryptography bcrypt python-jose[cryptography] python-multipart passlib email-validator requests jinja2"
            ;;
        "mcp")
            requirements="fastapi uvicorn pydantic httpx aiohttp cryptography"
            ;;
    esac
    
    info "Installation des dépendances Python..."
    if pip install $requirements; then
        log "Dépendances Python installées"
    else
        error "Échec de l'installation des dépendances"
        exit 1
    fi
    
    # Vérification des imports critiques
    python3 -c "import fastapi, uvicorn, pydantic, httpx; print('Imports critiques OK')"
    log "Imports Python validés"
}

# ===============================================================================
# CONFIGURATION DE LA BASE DE DONNÉES
# ===============================================================================

# Initialisation de la base de données
setup_database() {
    info "Configuration de la base de données..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # Restauration de la sauvegarde si disponible
    if [ -f "$HOME/bridge_data.db.backup" ]; then
        warn "Restauration de la base de données sauvegardée"
        cp "$HOME/bridge_data.db.backup" "bridge_data.db"
        log "Base de données restaurée"
    else
        # Initialisation temporaire pour créer la structure
        info "Initialisation de la nouvelle base de données..."
        timeout 10 python3 bridge_server.py --init-db &>/dev/null &
        local server_pid=$!
        sleep 5
        kill $server_pid 2>/dev/null || true
        wait $server_pid 2>/dev/null || true
        
        if [ -f "bridge_data.db" ]; then
            log "Base de données initialisée"
        else
            warn "Base de données sera créée au premier démarrage"
        fi
    fi
    
    # Configuration des permissions
    chmod 644 bridge_data.db 2>/dev/null || true
}

# ===============================================================================
# CONFIGURATION DU SERVICE SYSTEMD
# ===============================================================================

# Création du service systemd
create_systemd_service() {
    info "Configuration du service systemd..."
    
    local service_file="/etc/systemd/system/$SERVICE_NAME.service"
    local exec_script="start_server.py"
    
    # Détermination du script selon le mode
    case $INSTALL_MODE in
        "web") exec_script="start_server.py";;
        "mcp") exec_script="bridge_server.py";;
        "both") exec_script="start_server.py";;
    esac
    
    # Création du fichier service
    sudo tee "$service_file" > /dev/null <<EOF
[Unit]
Description=McP Bridge Server - Home Assistant MCP Bridge
Documentation=https://github.com/Jonathan97480/McpHomeAssistant
After=network.target network-online.target
Wants=network-online.target
ConditionPathExists=$PROJECT_DIR

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
Environment=PYTHONPATH=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/python $exec_script
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
TimeoutStartSec=30
TimeoutStopSec=30

# Sécurité
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

    # Rechargement et activation
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
    
    log "Service systemd configuré et activé"
}

# ===============================================================================
# CONFIGURATION RÉSEAU ET SÉCURITÉ
# ===============================================================================

# Configuration du firewall
setup_firewall() {
    info "Configuration du firewall..."
    
    if command -v ufw &> /dev/null; then
        # Configuration UFW
        local ports=""
        case $INSTALL_MODE in
            "web") ports="$WEB_PORT";;
            "mcp") ports="$MCP_PORT";;
            "both") ports="$WEB_PORT $MCP_PORT";;
        esac
        
        for port in $ports; do
            if sudo ufw allow $port/tcp; then
                log "Port $port ouvert dans UFW"
            else
                warn "Impossible d'ouvrir le port $port dans UFW"
            fi
        done
        
        # Affichage du statut si UFW est actif
        if sudo ufw status | grep -q "Status: active"; then
            info "Firewall UFW actif avec les ports configurés"
        else
            warn "UFW installé mais inactif. Activez-le avec: sudo ufw enable"
        fi
    else
        warn "UFW non installé. Configurez manuellement votre firewall:"
        case $INSTALL_MODE in
            "web") warn "  - Autoriser le port $WEB_PORT/tcp";;
            "mcp") warn "  - Autoriser le port $MCP_PORT/tcp";;
            "both") warn "  - Autoriser les ports $WEB_PORT/tcp et $MCP_PORT/tcp";;
        esac
    fi
}

# Configuration de la sécurité supplémentaire
setup_security() {
    info "Configuration de la sécurité..."
    
    # Fail2ban pour SSH (si disponible)
    if command -v fail2ban-server &> /dev/null; then
        if systemctl is-active --quiet fail2ban; then
            log "Fail2ban actif pour la protection SSH"
        else
            warn "Fail2ban installé mais inactif"
        fi
    fi
    
    # Configuration des limites système
    local limits_file="/etc/security/limits.d/mcpbridge.conf"
    if [ ! -f "$limits_file" ]; then
        sudo tee "$limits_file" > /dev/null <<EOF
# Limites pour McP Bridge
$USER soft nofile 65536
$USER hard nofile 65536
$USER soft nproc 4096
$USER hard nproc 4096
EOF
        log "Limites système configurées"
    fi
}

# ===============================================================================
# TESTS ET VALIDATION
# ===============================================================================

# Démarrage du service pour tests
start_service_for_tests() {
    info "Démarrage du service pour les tests..."
    
    sudo systemctl start $SERVICE_NAME
    
    # Attente du démarrage
    local max_wait=30
    local wait_time=0
    
    while [ $wait_time -lt $max_wait ]; do
        if systemctl is-active --quiet $SERVICE_NAME; then
            log "Service démarré avec succès"
            sleep 5  # Attente supplémentaire pour l'initialisation
            return 0
        fi
        sleep 2
        wait_time=$((wait_time + 2))
    done
    
    error "Le service n'a pas démarré dans les temps"
    sudo journalctl -u $SERVICE_NAME --no-pager -n 20
    return 1
}

# Tests de connectivité
run_connectivity_tests() {
    info "Tests de connectivité..."
    
    local success=0
    local total=0
    
    # Test selon le mode d'installation
    case $INSTALL_MODE in
        "web"|"both")
            # Test de l'interface web
            total=$((total + 1))
            if curl -f http://localhost:$WEB_PORT/health &>/dev/null; then
                log "✓ Interface web accessible (port $WEB_PORT)"
                success=$((success + 1))
            else
                warn "✗ Interface web inaccessible (port $WEB_PORT)"
            fi
            
            # Test de la page d'accueil
            total=$((total + 1))
            if curl -f http://localhost:$WEB_PORT/ | grep -q "McP Bridge" &>/dev/null; then
                log "✓ Page d'accueil chargée"
                success=$((success + 1))
            else
                warn "✗ Page d'accueil non accessible"
            fi
            ;;
    esac
    
    if [ "$INSTALL_MODE" = "mcp" ] || [ "$INSTALL_MODE" = "both" ]; then
        # Test MCP server
        total=$((total + 1))
        if curl -f http://localhost:$MCP_PORT/health &>/dev/null; then
            log "✓ Serveur MCP accessible (port $MCP_PORT)"
            success=$((success + 1))
        else
            warn "✗ Serveur MCP inaccessible (port $MCP_PORT)"
        fi
    fi
    
    # Test de la base de données
    total=$((total + 1))
    if [ -f "$PROJECT_DIR/bridge_data.db" ]; then
        log "✓ Base de données présente"
        success=$((success + 1))
    else
        warn "✗ Base de données manquante"
    fi
    
    # Résultat des tests
    info "Tests de connectivité: $success/$total réussis"
    return $((total - success))
}

# Exécution des tests automatisés
run_automated_tests() {
    info "Exécution des tests automatisés..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # Test simple si disponible
    if [ -f "tests/test_simple.py" ]; then
        if python3 tests/test_simple.py; then
            log "✓ Tests simples réussis"
            return 0
        else
            warn "✗ Échec des tests simples"
            return 1
        fi
    else
        warn "Script de test simple non trouvé"
        return 0
    fi
}

# ===============================================================================
# FINALISATION
# ===============================================================================

# Affichage des informations finales
show_final_information() {
    local ip_address=$(hostname -I | awk '{print $1}')
    
    echo
    success "=== Installation Terminée avec Succès ==="
    echo
    
    case $INSTALL_MODE in
        "web")
            echo "🌐 Interface Web McP Bridge:"
            echo "   Local:  http://localhost:$WEB_PORT"
            echo "   Réseau: http://$ip_address:$WEB_PORT"
            echo
            echo "🔐 Connexion par défaut:"
            echo "   Utilisateur: admin"
            echo "   Mot de passe: Admin123!"
            echo
            echo "⚠️  IMPORTANT: Changez le mot de passe immédiatement après la première connexion"
            ;;
        "mcp")
            echo "🔧 Serveur MCP:"
            echo "   Local:  http://localhost:$MCP_PORT"
            echo "   Réseau: http://$ip_address:$MCP_PORT"
            ;;
        "both")
            echo "🌐 Interface Web:"
            echo "   Local:  http://localhost:$WEB_PORT"
            echo "   Réseau: http://$ip_address:$WEB_PORT"
            echo
            echo "🔧 Serveur MCP:"
            echo "   Local:  http://localhost:$MCP_PORT"
            echo "   Réseau: http://$ip_address:$MCP_PORT"
            echo
            echo "🔐 Connexion Web (admin/Admin123!)"
            ;;
    esac
    
    echo
    echo "🛠️  Commandes utiles:"
    echo "   sudo systemctl status $SERVICE_NAME     # Statut du service"
    echo "   sudo systemctl restart $SERVICE_NAME    # Redémarrer"
    echo "   sudo systemctl stop $SERVICE_NAME       # Arrêter"
    echo "   sudo journalctl -u $SERVICE_NAME -f     # Logs en temps réel"
    echo
    echo "📁 Répertoire d'installation: $PROJECT_DIR"
    echo "📊 Mode d'installation: $INSTALL_MODE"
    echo
    echo "📚 Documentation:"
    echo "   • Guide complet: cat $PROJECT_DIR/DEPLOYMENT_GUIDE.md"
    echo "   • Installation Raspberry Pi: cat $PROJECT_DIR/RASPBERRY_PI_INSTALL.md"
    echo "   • Guide rapide: cat $PROJECT_DIR/QUICK_INSTALL_RPI.md"
    echo
    
    if [ "$INSTALL_MODE" = "web" ] || [ "$INSTALL_MODE" = "both" ]; then
        echo "🏠 Configuration Home Assistant:"
        echo "   1. Générer un token Long-Term dans Home Assistant"
        echo "   2. Aller dans Configuration → Home Assistant"
        echo "   3. Ajouter votre instance avec l'URL et le token"
        echo "   4. Tester la connexion"
        echo "   5. Configurer les permissions dans le menu Permissions"
        echo
    fi
    
    echo "✅ Installation Phase 3.4 complète !"
}

# Nettoyage en cas d'erreur
cleanup_on_error() {
    error "Erreur pendant l'installation"
    
    # Arrêt du service si démarré
    if systemctl is-active --quiet $SERVICE_NAME 2>/dev/null; then
        sudo systemctl stop $SERVICE_NAME
    fi
    
    # Affichage des logs pour debugging
    if [ -f "/var/log/syslog" ]; then
        warn "Dernières lignes du syslog:"
        tail -20 /var/log/syslog | grep -i "$SERVICE_NAME" || true
    fi
    
    echo
    error "Consultez les logs pour plus de détails:"
    error "  sudo journalctl -u $SERVICE_NAME --no-pager"
    error "  cat $PROJECT_DIR/install.log"
    
    exit 1
}

# ===============================================================================
# FONCTION PRINCIPALE
# ===============================================================================

main() {
    # Gestion des erreurs
    trap cleanup_on_error ERR
    
    # Affichage du banner
    show_banner
    
    # Menu de sélection
    choose_installation_mode
    
    # Demande de confirmation
    ask_confirmation
    
    # Début de l'installation
    info "Début de l'installation..."
    local start_time=$(date +%s)
    
    # Étapes de vérification
    check_root
    check_system
    check_python
    check_git
    check_homeassistant
    
    # Installation des dépendances
    install_system_packages
    
    # Gestion des services existants
    stop_existing_services
    
    # Installation du projet
    backup_existing_installation
    clone_project
    
    # Configuration Python
    setup_python_environment
    
    # Configuration de la base de données
    setup_database
    
    # Configuration du service
    create_systemd_service
    
    # Configuration réseau et sécurité
    setup_firewall
    setup_security
    
    # Tests et validation
    start_service_for_tests
    run_connectivity_tests
    run_automated_tests
    
    # Finalisation
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    show_final_information
    
    success "Installation terminée en ${duration}s"
    
    return 0
}

# ===============================================================================
# POINT D'ENTRÉE
# ===============================================================================

# Vérification que le script est exécuté directement
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi