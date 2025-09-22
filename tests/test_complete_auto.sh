#!/bin/bash

# 🧪 Script de Test Automatique Complet - MCP Bridge (Linux/Mac)
# Lance le serveur dans un nouveau terminal et exécute tous les tests

set -e

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVER_PORT=8080
SERVER_URL="http://localhost:$SERVER_PORT"

echo "🧪 LANCEMENT DE LA SUITE DE TESTS AUTOMATIQUE"
echo "============================================================"

# Fonction pour arrêter les serveurs existants
stop_existing_servers() {
    echo "🔄 Arrêt des serveurs existants..."
    
    # Tuer les processus Python qui pourraient être des serveurs
    if pgrep -f "start_server.py\|bridge_server" > /dev/null; then
        echo "🔪 Arrêt des processus Python serveurs..."
        pkill -f "start_server.py\|bridge_server" || true
    fi
    
    # Vérifier les processus sur le port 8080
    if netstat -tulpn 2>/dev/null | grep ":$SERVER_PORT " > /dev/null; then
        echo "🔪 Arrêt des processus sur port $SERVER_PORT..."
        lsof -ti:$SERVER_PORT | xargs -r kill -9 || true
    fi
    
    sleep 2
    echo "✅ Serveurs existants arrêtés"
}

# Fonction pour démarrer le serveur
start_server() {
    echo "🚀 Démarrage du serveur dans un nouveau terminal..."
    
    cd "$PROJECT_ROOT"
    
    # Vérifier si l'environnement virtuel existe
    if [ -f "venv/bin/activate" ]; then
        echo "🐍 Utilisation de l'environnement virtuel..."
        SERVER_CMD="cd '$PROJECT_ROOT' && source venv/bin/activate && python src/start_server.py"
    else
        SERVER_CMD="cd '$PROJECT_ROOT' && python src/start_server.py"
    fi
    
    # Démarrer le serveur dans un nouveau terminal selon l'environnement
    if command -v gnome-terminal > /dev/null; then
        gnome-terminal -- bash -c "$SERVER_CMD; echo 'Appuyez sur Entrée pour fermer...'; read" &
        SERVER_PID=$!
    elif command -v konsole > /dev/null; then
        konsole -e bash -c "$SERVER_CMD; echo 'Appuyez sur Entrée pour fermer...'; read" &
        SERVER_PID=$!
    elif command -v xterm > /dev/null; then
        xterm -e bash -c "$SERVER_CMD; echo 'Appuyez sur Entrée pour fermer...'; read" &
        SERVER_PID=$!
    else
        echo "⚠️ Aucun terminal graphique trouvé, démarrage en arrière-plan..."
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        fi
        python src/start_server.py &
        SERVER_PID=$!
    fi
    
    echo "🖥️ Serveur lancé avec PID: $SERVER_PID"
    
    # Attendre que le serveur démarre
    local max_wait=25
    for ((i=1; i<=max_wait; i++)); do
        if curl -s "$SERVER_URL/health" > /dev/null 2>&1; then
            echo "✅ Serveur démarré et accessible sur $SERVER_URL"
            return 0
        fi
        
        # Vérifier si le processus existe encore
        if ! kill -0 $SERVER_PID 2>/dev/null; then
            echo "❌ Le processus serveur s'est arrêté prématurément"
            return 1
        fi
        
        echo "⏳ Attente du serveur... ($i/$max_wait)"
        sleep 1
    done
    
    echo "❌ Timeout: Le serveur n'a pas démarré dans les temps"
    echo "💡 Le serveur continue de démarrer dans le terminal séparé"
    return 0  # On continue quand même
}

# Fonction pour exécuter un test
run_test() {
    local test_file="$1"
    local test_name="$2"
    
    echo ""
    echo "🧪 Exécution du test: $test_name"
    echo "=================================================="
    
    if [ ! -f "tests/$test_file" ]; then
        echo "⚠️ Test ignoré (fichier non trouvé): $test_file"
        return 2
    fi
    
    if python "tests/$test_file"; then
        echo "✅ Test $test_name RÉUSSI"
        return 0
    else
        echo "❌ Test $test_name ÉCHOUÉ (code: $?)"
        return 1
    fi
}

# Fonction pour exécuter tous les tests
run_all_tests() {
    echo ""
    echo "🎯 DÉMARRAGE DE LA SUITE DE TESTS COMPLÈTE"
    echo "============================================================"
    
    # Attendre un peu pour que le serveur soit stable
    sleep 3
    
    local passed=0
    local failed=0
    
    # Liste des tests à exécuter
    local tests=(
        "test_database.py:Base de données"
        "test_auth.py:Authentification"
        "test_cache_circuit_breaker.py:Cache et Circuit Breaker"
        "test_ha_config.py:Configuration Home Assistant"
        "test_permissions_simple.py:Permissions"
        "test_web_interface.py:Interface Web"
        "test_complete.py:Tests Complets"
    )
    
    for test_info in "${tests[@]}"; do
        IFS=':' read -r test_file test_name <<< "$test_info"
        
        run_test "$test_file" "$test_name"
        case $? in
            0) ((passed++)) ;;
            1) ((failed++)) ;;
            2) ;; # Ignoré
        esac
        
        sleep 2  # Pause entre les tests
    done
    
    # Afficher le résumé
    echo ""
    echo "📊 RÉSUMÉ DES TESTS"
    echo "============================================================"
    echo "✅ Réussis: $passed"
    echo "❌ Échoués: $failed"
    
    local total=$((passed + failed))
    if [ $total -gt 0 ]; then
        local percentage=$((passed * 100 / total))
        echo "📊 Taux de réussite: ${percentage}%"
    else
        echo "📊 Taux de réussite: 0%"
    fi
    
    if [ $failed -eq 0 ] && [ $passed -gt 0 ]; then
        echo "🎉 TOUS LES TESTS ONT RÉUSSI !"
        return 0
    else
        echo "💥 CERTAINS TESTS ONT ÉCHOUÉ"
        return 1
    fi
}

# Fonction principale
main() {
    # 1. Arrêter les serveurs existants
    stop_existing_servers
    
    # 2. Démarrer le serveur
    if ! start_server; then
        echo "❌ Impossible de démarrer le serveur, arrêt des tests"
        exit 1
    fi
    
    # 3. Lancer tous les tests
    if run_all_tests; then
        exit_code=0
    else
        exit_code=1
    fi
    
    echo ""
    echo "🏁 Tests terminés"
    echo "💡 N'oubliez pas de fermer le terminal du serveur manuellement si nécessaire"
    
    exit $exit_code
}

# Gestion des interruptions
trap 'echo "🛑 Tests interrompus par l'\''utilisateur"; exit 1' INT TERM

# Lancer le script principal
main "$@"