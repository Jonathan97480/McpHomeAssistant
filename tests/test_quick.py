#!/usr/bin/env python3
"""
Test simple qui lance le serveur et effectue des tests basiques
Fonctionne correctement avec la gestion des processus
"""

import requests
import time
import subprocess
import sys
import os
import signal
import psutil

class ServerManager:
    def __init__(self):
        self.server_proc = None
        self.base_url = "http://localhost:8080"
        
    def start_server(self):
        """Lance le serveur en arrière-plan"""
        try:
            print('🚀 Démarrage du serveur McP Bridge...')
            
            # Tuer les processus existants sur le port
            self.kill_existing_servers()
            
            # Démarrer le serveur
            cmd = [sys.executable, 'bridge_server.py']
            self.server_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # Répertoire parent (racine)
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Attendre que le serveur démarre
            max_wait = 15
            for i in range(max_wait):
                try:
                    response = requests.get(f'{self.base_url}/health', timeout=2)
                    if response.status_code == 200:
                        print(f'✅ Serveur démarré avec succès (en {i+1}s)')
                        return True
                except:
                    time.sleep(1)
                    print(f'   Attente du serveur... ({i+1}/{max_wait})')
            
            print('❌ Timeout: Le serveur n\'a pas démarré dans les temps')
            return False
            
        except Exception as e:
            print(f'❌ Erreur lors du démarrage du serveur: {e}')
            return False
    
    def kill_existing_servers(self):
        """Tue les serveurs existants sur le port"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['cmdline'] and any('start_server.py' in str(arg) or 'bridge_server.py' in str(arg) for arg in proc.info['cmdline']):
                        print(f'   Arrêt du processus existant: {proc.info["pid"]}')
                        proc.terminate()
                        time.sleep(1)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            print(f'   Avertissement: {e}')
    
    def stop_server(self):
        """Arrête le serveur"""
        try:
            if self.server_proc:
                print('🛑 Arrêt du serveur...')
                if os.name == 'nt':  # Windows
                    self.server_proc.terminate()
                else:  # Unix/Linux
                    self.server_proc.send_signal(signal.SIGTERM)
                
                # Attendre l'arrêt
                try:
                    self.server_proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.server_proc.kill()
                
                self.server_proc = None
                print('✅ Serveur arrêté')
        except Exception as e:
            print(f'⚠️ Erreur lors de l\'arrêt: {e}')

def run_tests():
    """Exécute les tests principaux"""
    server = ServerManager()
    
    print('🧪 TEST SIMPLE - McP Bridge Phase 3.4')
    print('=' * 50)
    
    # Démarrer le serveur
    if not server.start_server():
        return False
    
    success_count = 0
    total_tests = 0
    
    try:
        # Test 1: Health Check
        print('\n🩺 Test 1: Health Check')
        total_tests += 1
        try:
            response = requests.get(f'{server.base_url}/health', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f'   ✅ Serveur en ligne - Status: {data.get("status", "unknown")}')
                success_count += 1
            else:
                print(f'   ❌ Status code: {response.status_code}')
        except Exception as e:
            print(f'   ❌ Erreur: {e}')
        
        # Test 2: Interface Web
        print('\n🌐 Test 2: Interface Web')
        total_tests += 1
        try:
            response = requests.get(server.base_url, timeout=5)
            if response.status_code == 200 and ('HTTP-MCP Bridge' in response.text or 'Redirection' in response.text):
                print('   ✅ Page d\'accueil accessible')
                success_count += 1
            else:
                print(f'   ❌ Page non accessible ou contenu incorrect')
        except Exception as e:
            print(f'   ❌ Erreur: {e}')
        
        # Test 3: API Status
        print('\n📊 Test 3: API Status')
        total_tests += 1
        try:
            response = requests.get(f'{server.base_url}/mcp/status', timeout=5)
            if response.status_code in [200, 401]:  # 401 = auth requise (normal)
                print('   ✅ API accessible (authentification requise)')
                success_count += 1
            else:
                print(f'   ❌ API non accessible: {response.status_code}')
        except Exception as e:
            print(f'   ❌ Erreur: {e}')
        
        # Test 4: Login
        print('\n🔐 Test 4: Authentification')
        total_tests += 1
        try:
            login_data = {'username': 'admin', 'password': 'Admin123!'}
            response = requests.post(f'{server.base_url}/auth/login', json=login_data, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    print('   ✅ Authentification réussie')
                    success_count += 1
                else:
                    print('   ❌ Token non reçu')
            else:
                print(f'   ❌ Login échoué: {response.status_code}')
        except Exception as e:
            print(f'   ❌ Erreur: {e}')
        
        # Test 5: Base de données
        print('\n💾 Test 5: Base de données')
        total_tests += 1
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bridge_data.db')
        if os.path.exists(db_path):
            print('   ✅ Base de données présente')
            success_count += 1
        else:
            print('   ❌ Base de données manquante')
        
    finally:
        # Arrêter le serveur
        server.stop_server()
    
    # Résultats
    print('\n' + '=' * 50)
    print('📊 RÉSULTATS DES TESTS')
    print('=' * 50)
    print(f'Tests réussis: {success_count}/{total_tests}')
    
    if success_count == total_tests:
        print('🎉 TOUS LES TESTS RÉUSSIS !')
        print('✅ McP Bridge fonctionne correctement')
        return True
    else:
        print('❌ CERTAINS TESTS ONT ÉCHOUÉ')
        print('⚠️ Vérifiez les erreurs ci-dessus')
        return False

if __name__ == "__main__":
    try:
        # Installer psutil si nécessaire
        try:
            import psutil
        except ImportError:
            print('📦 Installation de psutil...')
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psutil'])
            import psutil
        
        success = run_tests()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print('\n🛑 Test interrompu par l\'utilisateur')
        sys.exit(1)
    except Exception as e:
        print(f'\n❌ Erreur critique: {e}')
        sys.exit(1)