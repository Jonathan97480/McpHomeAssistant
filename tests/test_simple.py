#!/usr/bin/env python3
"""
Script simple pour tester l'interface web
Lance automatiquement le serveur et effectue les tests
"""

import requests
import time
import subprocess
import sys
import threading
import os

def start_server_in_background():
    """Lance le serveur en arrière-plan"""
    try:
        print('🚀 Démarrage du serveur en arrière-plan...')
        # Lancer le serveur en arrière-plan
        proc = subprocess.Popen([
            sys.executable, 'bridge_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd())
        
        # Attendre que le serveur démarre
        time.sleep(8)
        return proc
    except Exception as e:
        print(f'❌ Erreur démarrage serveur: {e}')
        return None

def test_interface():
    """Test simple de l'interface web"""
    base_url = "http://localhost:8080"
    
    print('🚀 Test de l\'interface web dashboard')
    print('=' * 50)
    
    # Démarrer le serveur
    server_proc = start_server_in_background()
    if not server_proc:
        print('❌ Impossible de démarrer le serveur')
        return False
    
    try:
        # Test 1: Health check
        print('\n🧪 Test 1: Health check')
        response = requests.get(f'{base_url}/health', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            print('   ✅ Serveur en ligne')
            data = response.json()
            print(f'   📊 Statut: {data.get("status")}')
        
        # Test 2: Page principale
        print('\n🧪 Test 2: Page principale')
        response = requests.get(f'{base_url}/', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            print('   ✅ Page principale accessible')
            print(f'   📄 Taille: {len(response.text)} caractères')
        
        # Test 3: Page de connexion
        print('\n🧪 Test 3: Page de connexion')
        response = requests.get(f'{base_url}/login', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            print('   ✅ Page de connexion accessible')
        
        # Test 4: Dashboard
        print('\n🧪 Test 4: Dashboard')
        response = requests.get(f'{base_url}/dashboard', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            print('   ✅ Dashboard accessible')
        
        # Test 5: CSS
        print('\n🧪 Test 5: Fichier CSS')
        response = requests.get(f'{base_url}/static/css/main.css', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            print('   ✅ CSS accessible')
            print(f'   📄 Taille: {len(response.text)} caractères')
        
        # Test 6: JavaScript
        print('\n🧪 Test 6: Fichier JavaScript')
        response = requests.get(f'{base_url}/static/js/dashboard.js', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            print('   ✅ JavaScript accessible')
            print(f'   📄 Taille: {len(response.text)} caractères')
        
        # Test 7: API Métriques
        print('\n🧪 Test 7: API Métriques')
        response = requests.get(f'{base_url}/api/metrics', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print('   ✅ API métriques fonctionnelle')
            print(f'   📊 Connexions actives: {data.get("active_connections", 0)}')
            print(f'   🔧 Outils MCP: {data.get("total_tools", 0)}')
        
        # Test 8: API Configuration
        print('\n🧪 Test 8: API Configuration')
        response = requests.get(f'{base_url}/api/config', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print('   ✅ API configuration accessible')
            print(f'   🏠 Home Assistant configuré: {data.get("homeassistant", {}).get("connected", False)}')
        
        # Test 9: Templates
        print('\n🧪 Test 9: Templates HTML')
        templates = ['dashboard-overview', 'permissions', 'config', 'tools', 'logs', 'admin']
        for template in templates:
            response = requests.get(f'{base_url}/api/templates/{template}', timeout=5)
            if response.status_code == 200:
                print(f'   ✅ Template {template}')
            else:
                print(f'   ❌ Template {template} - Status: {response.status_code}')
        
        print('\n🎉 Tests terminés avec succès!')
        return True
        
    except requests.exceptions.ConnectionError:
        print('\n❌ Erreur: Le serveur n\'est pas accessible')
        return False
    except Exception as e:
        print(f'\n❌ Erreur inattendue: {e}')
        return False
    finally:
        # Arrêter le serveur
        if server_proc:
            print('\n🛑 Arrêt du serveur...')
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()

def main():
    """Point d'entrée principal"""
    print('🔧 Script de test automatique du dashboard MCP')
    print('📋 Ce script va démarrer le serveur et effectuer des tests')
    print('=' * 60)
    
    success = test_interface()
    
    if success:
        print('\n✅ Tous les tests sont passés!')
        return 0
    else:
        print('\n❌ Certains tests ont échoué')
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)