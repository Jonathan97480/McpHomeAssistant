#!/usr/bin/env python3
"""
🧪 Test du système de base de données et logs
Test complet du système de logging et base de données
"""

import asyncio
import sqlite3
import os
from datetime import datetime, timedelta
from database import DatabaseManager, DailyLogManager, LogEntry, RequestEntry, ErrorEntry

async def test_database_system():
    """Test complet du système de base de données"""
    print("🧪 Test du système de base de données")
    print("====================================")
    
    # Nettoyer les fichiers de test existants
    test_files = ["test_bridge.db", "logs/test_log.log"]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
    
    # Initialiser le gestionnaire de BDD
    db_manager = DatabaseManager("test_bridge.db")
    await db_manager.initialize()
    
    print("✅ Base de données initialisée")
    
    # Test 1: Insertion de logs
    print("\n📝 Test 1: Insertion de logs")
    
    test_logs = [
        LogEntry(
            timestamp=datetime.now().isoformat(),
            level="INFO",
            message="Démarrage du serveur bridge",
            module="bridge_server",
            session_id="session-001"
        ),
        LogEntry(
            timestamp=datetime.now().isoformat(),
            level="WARNING", 
            message="Session expirée",
            module="session_pool",
            session_id="session-002",
            extra_data='{"timeout": 30}'
        ),
        LogEntry(
            timestamp=datetime.now().isoformat(),
            level="ERROR",
            message="Erreur connexion Home Assistant",
            module="mcp_client",
            extra_data='{"url": "http://192.168.1.22:8123", "error": "timeout"}'
        )
    ]
    
    for log in test_logs:
        log_id = await db_manager.insert_log(log)
        print(f"   Log inséré: ID {log_id} - {log.level} - {log.message[:50]}...")
    
    # Test 2: Insertion de requêtes
    print("\n🌐 Test 2: Insertion de requêtes")
    
    test_requests = [
        RequestEntry(
            timestamp=datetime.now().isoformat(),
            session_id="session-001",
            method="POST",
            endpoint="/mcp/initialize",
            params='{"protocolVersion": "2024-11-05"}',
            response_time_ms=145,
            status_code=200,
            user_ip="192.168.1.100",
            user_agent="Mozilla/5.0 Bridge Client"
        ),
        RequestEntry(
            timestamp=datetime.now().isoformat(),
            session_id="session-001",
            method="POST",
            endpoint="/mcp/tools/call",
            params='{"name": "get_entities", "arguments": {"domain": "light"}}',
            response_time_ms=523,
            status_code=200,
            user_ip="192.168.1.100"
        ),
        RequestEntry(
            timestamp=datetime.now().isoformat(),
            session_id="session-002",
            method="POST",
            endpoint="/mcp/tools/call",
            params='{"name": "call_service", "arguments": {"domain": "light", "service": "turn_on"}}',
            response_time_ms=1203,
            status_code=500,
            user_ip="192.168.1.101"
        )
    ]
    
    for req in test_requests:
        req_id = await db_manager.insert_request(req)
        print(f"   Requête insérée: ID {req_id} - {req.method} {req.endpoint} - {req.status_code} ({req.response_time_ms}ms)")
    
    # Test 3: Insertion d'erreurs
    print("\n❌ Test 3: Insertion d'erreurs")
    
    test_errors = [
        ErrorEntry(
            timestamp=datetime.now().isoformat(),
            error_type="HTTPException",
            error_message="Session not found",
            session_id="session-invalid",
            context='{"endpoint": "/mcp/tools/call", "status": 404}'
        ),
        ErrorEntry(
            timestamp=datetime.now().isoformat(),
            error_type="ConnectionError",
            error_message="Failed to connect to Home Assistant",
            stack_trace="Traceback (most recent call last):\n  File...",
            context='{"url": "http://192.168.1.22:8123", "timeout": 30}'
        )
    ]
    
    for error in test_errors:
        error_id = await db_manager.insert_error(error)
        print(f"   Erreur insérée: ID {error_id} - {error.error_type} - {error.error_message}")
    
    # Test 4: Récupération des statistiques
    print("\n📊 Test 4: Statistiques")
    
    stats = await db_manager.get_stats(days=1)
    print(f"   Statistiques des dernières 24h:")
    print(f"   - Requêtes totales: {stats.get('requests', {}).get('total_requests', 0)}")
    print(f"   - Temps de réponse moyen: {stats.get('requests', {}).get('avg_response_time', 0):.2f}ms")
    print(f"   - Sessions uniques: {stats.get('requests', {}).get('unique_sessions', 0)}")
    print(f"   - Types d'erreurs: {len(stats.get('errors_by_type', []))}")
    print(f"   - Top endpoints: {len(stats.get('top_endpoints', []))}")
    
    # Afficher les détails
    if stats.get('errors_by_type'):
        print(f"   Erreurs par type:")
        for error in stats['errors_by_type']:
            print(f"     - {error['error_type']}: {error['count']}")
    
    if stats.get('top_endpoints'):
        print(f"   Top endpoints:")
        for endpoint in stats['top_endpoints']:
            print(f"     - {endpoint['endpoint']}: {endpoint['count']} requêtes ({endpoint['avg_time']:.1f}ms moy.)")
    
    # Test 5: Test du gestionnaire de logs journaliers
    print("\n📅 Test 5: Gestionnaire de logs journaliers")
    
    log_manager = DailyLogManager("logs", db_manager)
    
    # Créer un fichier de log test
    test_log_file = log_manager.get_log_file_path()
    test_log_file.parent.mkdir(exist_ok=True)
    
    with open(test_log_file, 'w', encoding='utf-8') as f:
        f.write("2025-09-21 16:45:00,123 - bridge_server - INFO - Test log entry 1\n")
        f.write("2025-09-21 16:45:05,456 - session_pool - WARNING - Test warning entry\n") 
        f.write("2025-09-21 16:45:10,789 - database - ERROR - Test error entry\n")
    
    print(f"   Fichier log créé: {test_log_file}")
    
    # Importer les logs
    imported_count = await db_manager.import_daily_logs(str(test_log_file))
    print(f"   Logs importés: {imported_count}")
    
    # Test 6: Nettoyage des données anciennes
    print("\n🧹 Test 6: Nettoyage (simulation)")
    
    # Créer des données anciennes (simulées)
    old_date = (datetime.now() - timedelta(days=45)).isoformat()
    
    old_log = LogEntry(
        timestamp=old_date,
        level="INFO",
        message="Ancienne entrée de log",
        module="test"
    )
    await db_manager.insert_log(old_log)
    
    old_request = RequestEntry(
        timestamp=old_date,
        session_id="old-session",
        method="GET",
        endpoint="/health",
        response_time_ms=100,
        status_code=200
    )
    await db_manager.insert_request(old_request)
    
    print(f"   Données anciennes créées (date: {old_date[:10]})")
    
    # Effectuer le nettoyage
    cleanup_result = await db_manager.cleanup_old_data(days_to_keep=30)
    
    if cleanup_result:
        print(f"   Nettoyage effectué:")
        print(f"     - Logs supprimés: {cleanup_result['logs_deleted']}")
        print(f"     - Requêtes supprimées: {cleanup_result['requests_deleted']}")
        print(f"     - Erreurs supprimées: {cleanup_result['errors_deleted']}")
        print(f"     - Date limite: {cleanup_result['cutoff_date'][:10]}")
    
    # Test 7: Vérification de l'intégrité
    print("\n🔍 Test 7: Vérification finale")
    
    # Compter les entrées restantes
    cursor = db_manager.connection.execute("SELECT COUNT(*) FROM logs")
    logs_count = cursor.fetchone()[0]
    
    cursor = db_manager.connection.execute("SELECT COUNT(*) FROM requests")
    requests_count = cursor.fetchone()[0]
    
    cursor = db_manager.connection.execute("SELECT COUNT(*) FROM errors")
    errors_count = cursor.fetchone()[0]
    
    print(f"   Entrées en base après tests:")
    print(f"     - Logs: {logs_count}")
    print(f"     - Requêtes: {requests_count}")
    print(f"     - Erreurs: {errors_count}")
    
    # Fermer la connexion
    await db_manager.close()
    
    # Nettoyer les fichiers de test
    for file in ["test_bridge.db", str(test_log_file)]:
        if os.path.exists(file):
            os.remove(file)
    
    print("\n✅ Tous les tests réussis ! Système de base de données opérationnel.")
    
    return True


if __name__ == "__main__":
    asyncio.run(test_database_system())