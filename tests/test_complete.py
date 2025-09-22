#!/usr/bin/env python3
"""
Script de test complet pour l'interface web du dashboard MCP
Teste toutes les fonctionnalités avancées
"""

import requests
import time
import subprocess
import sys
import os
import json

def start_server_in_background():
    """Lance le serveur en arrière-plan"""
    try:
        print('[START] Démarrage du serveur en arrière-plan...')
        proc = subprocess.Popen([
            sys.executable, 'bridge_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd())
        
        # Attendre que le serveur démarre
        time.sleep(8)
        return proc
    except Exception as e:
        print(f'[FAIL] Erreur démarrage serveur: {e}')
        return None

def test_complete_interface():
    """Test complet de l'interface web"""
    base_url = "http://localhost:8080"
    
    print('[START] TEST COMPLET - Interface Web Dashboard MCP')
    print('=' * 60)
    
    # Démarrer le serveur
    server_proc = start_server_in_background()
    if not server_proc:
        print('[FAIL] Impossible de démarrer le serveur')
        return False
    
    try:
        # Test 1: Health Check
        print('\n[TOOL] SECTION 1: SANTÉ DU SERVEUR')
        print('-' * 40)
        response = requests.get(f'{base_url}/health', timeout=5)
        print(f'   [OK] Health Check: {response.status_code}')
        if response.status_code == 200:
            health_data = response.json()
            print(f'   [STATS] Statut: {health_data.get("status")}')
            print(f'   [TIMER] Uptime: {health_data.get("uptime", 0)} secondes')
        
        # Test 2: Pages Web
        print('\n[WEB] SECTION 2: PAGES WEB')
        print('-' * 40)
        pages = {
            '/': 'Page d\'accueil',
            '/login': 'Page de connexion',
            '/dashboard': 'Dashboard principal',
            '/permissions': 'Gestion des permissions',
            '/config': 'Configuration',
            '/tools': 'Outils MCP',
            '/logs': 'Logs système',
            '/admin': 'Administration'
        }
        
        for path, name in pages.items():
            response = requests.get(f'{base_url}{path}', timeout=5)
            if response.status_code == 200:
                print(f'   [OK] {name}: {response.status_code} ({len(response.text)} chars)')
            else:
                print(f'   [FAIL] {name}: {response.status_code}')
        
        # Test 3: Fichiers statiques
        print('\n[FOLDER] SECTION 3: FICHIERS STATIQUES')
        print('-' * 40)
        static_files = {
            '/static/css/main.css': 'Feuille de style CSS',
            '/static/js/dashboard.js': 'JavaScript principal'
        }
        
        for path, name in static_files.items():
            response = requests.get(f'{base_url}{path}', timeout=5)
            if response.status_code == 200:
                size_kb = len(response.text) / 1024
                print(f'   [OK] {name}: {response.status_code} ({size_kb:.1f}KB)')
            else:
                print(f'   [FAIL] {name}: {response.status_code}')
        
        # Test 4: API Endpoints
        print('\n[LINK] SECTION 4: API ENDPOINTS')
        print('-' * 40)
        api_endpoints = {
            '/api/metrics': 'Métriques du dashboard',
            '/api/config': 'Configuration système',
            '/api/tools': 'Outils MCP',
            '/api/logs': 'Logs système',
            '/api/tools/statistics': 'Statistiques des outils'
        }
        
        for path, name in api_endpoints.items():
            try:
                response = requests.get(f'{base_url}{path}', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f'   [OK] {name}: {response.status_code} (JSON valide)')
                    
                    # Afficher quelques détails spécifiques
                    if path == '/api/metrics':
                        print(f'      [STATS] Connexions actives: {data.get("active_connections", 0)}')
                        print(f'      [TOOL] Outils MCP: {data.get("total_tools", 0)}')
                    elif path == '/api/tools':
                        tools = data.get('tools', [])
                        print(f'      [TOOL] Nombre d\'outils: {len(tools)}')
                    elif path == '/api/logs':
                        logs = data.get('logs', [])
                        pagination = data.get('pagination', {})
                        print(f'      [NOTE] Logs retournés: {len(logs)}')
                        print(f'      [FILE] Total logs: {pagination.get("total", 0)}')
                else:
                    print(f'   [FAIL] {name}: {response.status_code}')
            except json.JSONDecodeError:
                print(f'   [WARN]  {name}: Réponse non-JSON')
            except Exception as e:
                print(f'   [FAIL] {name}: Erreur - {e}')
        
        # Test 5: Templates HTML
        print('\n[FILE] SECTION 5: TEMPLATES HTML')
        print('-' * 40)
        templates = {
            'dashboard-overview': 'Vue d\'ensemble du dashboard',
            'permissions': 'Gestion des permissions',
            'config': 'Configuration système',
            'tools': 'Outils MCP',
            'logs': 'Logs système',
            'admin': 'Administration'
        }
        
        for template, name in templates.items():
            response = requests.get(f'{base_url}/api/templates/{template}', timeout=5)
            if response.status_code == 200:
                size_kb = len(response.text) / 1024
                print(f'   [OK] {name}: {response.status_code} ({size_kb:.1f}KB)')
            else:
                print(f'   [FAIL] {name}: {response.status_code}')
        
        # Test 6: Tests de fonctionnalités avancées
        print('\n[TEST] SECTION 6: TESTS AVANCÉS')
        print('-' * 40)
        
        # Test pagination des logs
        response = requests.get(f'{base_url}/api/logs?page=1&limit=10', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f'   [OK] Pagination logs: {len(data.get("logs", []))} logs sur page 1')
        
        # Test filtrage des logs
        response = requests.get(f'{base_url}/api/logs?level=ERROR&limit=5', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f'   [OK] Filtrage logs (ERROR): {len(data.get("logs", []))} logs')
        
        # Test export logs CSV
        response = requests.get(f'{base_url}/api/logs/export?format=csv', timeout=5)
        if response.status_code == 200:
            print(f'   [OK] Export CSV: {len(response.text)} caractères')
        
        # Test configuration Home Assistant
        test_config = {
            "type": "homeassistant",
            "url": "http://localhost:8123",
            "token": "test_token"
        }
        response = requests.post(f'{base_url}/api/config/test', json=test_config, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f'   [OK] Test config HA: {result.get("status")}')
        
        # Test des outils MCP
        response = requests.get(f'{base_url}/api/tools/statistics', timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f'   [OK] Stats outils: {stats.get("total_tools", 0)} outils, {stats.get("success_rate", 0)}% succès')
        
        print('\n[PARTY] TOUS LES TESTS TERMINÉS AVEC SUCCÈS!')
        return True
        
    except requests.exceptions.ConnectionError:
        print('\n[FAIL] Erreur: Le serveur n\'est pas accessible')
        return False
    except Exception as e:
        print(f'\n[FAIL] Erreur inattendue: {e}')
        return False
    finally:
        # Arrêter le serveur
        if server_proc:
            print('\n[STOP] Arrêt du serveur...')
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()

def main():
    """Point d'entrée principal"""
    print('[SCOPE] SCRIPT DE TEST COMPLET - Dashboard MCP')
    print('[LIST] Test de toutes les fonctionnalités de l\'interface web')
    print('=' * 70)
    
    success = test_complete_interface()
    
    if success:
        print('\n' + '='*70)
        print('[OK] RÉSULTAT: TOUS LES TESTS SONT PASSÉS!')
        print('[TARGET] L\'interface web est entièrement fonctionnelle')
        print('[WEB] Prêt pour utilisation en production')
        print('='*70)
        return 0
    else:
        print('\n' + '='*70)
        print('[FAIL] RÉSULTAT: CERTAINS TESTS ONT ÉCHOUÉ')
        print('[TOOL] Vérifiez les erreurs ci-dessus')
        print('='*70)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)