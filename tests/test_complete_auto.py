#!/usr/bin/env python3
"""
🧪 Test Suite Automatique Complète - MCP Bridge
Gestion automatique du serveur et exécution de tous les tests
"""

import asyncio
import subprocess
import time
import sys
import os
import signal
import psutil
import logging
from pathlib import Path

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoTestRunner:
    def __init__(self):
        self.server_process = None
        self.project_root = Path(__file__).parent.parent
        self.server_port = 8080
        self.server_url = f"http://localhost:{self.server_port}"
        
    def kill_existing_servers(self):
        """Ferme tous les serveurs Python existants sur le port 8080"""
        logger.info("🔄 Arrêt des serveurs existants...")
        
        try:
            # Tuer les processus Python
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any('start_server.py' in str(cmd) or 'bridge_server' in str(cmd) for cmd in cmdline):
                            logger.info(f"🔪 Arrêt du processus Python: {proc.info['pid']}")
                            proc.kill()
                            proc.wait(timeout=3)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass
            
            # Vérifier les processus sur le port 8080
            for conn in psutil.net_connections():
                if conn.laddr.port == self.server_port and conn.status == psutil.CONN_LISTEN:
                    try:
                        proc = psutil.Process(conn.pid)
                        logger.info(f"🔪 Arrêt du processus sur port {self.server_port}: {conn.pid}")
                        proc.kill()
                        proc.wait(timeout=3)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        pass
                        
            time.sleep(2)  # Attendre que les processus se ferment
            logger.info("✅ Serveurs existants arrêtés")
            
        except Exception as e:
            logger.warning(f"⚠️ Erreur lors de l'arrêt des serveurs: {e}")
    
    def start_server(self):
        """Démarre le serveur dans un nouveau terminal"""
        logger.info("🚀 Démarrage du serveur dans un nouveau terminal...")
        
        try:
            # Changer vers le répertoire du projet
            os.chdir(self.project_root)
            
            # Préparer la commande selon l'OS
            if os.name == 'nt':  # Windows
                # Vérifier l'environnement virtuel
                venv_activate = self.project_root / "venv" / "Scripts" / "activate.bat"
                if venv_activate.exists():
                    cmd = f'start cmd /k "cd /d "{self.project_root}" && "{venv_activate}" && python src/start_server.py"'
                else:
                    cmd = f'start cmd /k "cd /d "{self.project_root}" && python src/start_server.py"'
                
                # Lancer dans un nouveau terminal Windows
                self.server_process = subprocess.Popen(
                    cmd,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:  # Linux/Mac
                # Vérifier l'environnement virtuel
                venv_activate = self.project_root / "venv" / "bin" / "activate"
                if venv_activate.exists():
                    cmd = f'gnome-terminal -- bash -c "cd {self.project_root} && source {venv_activate} && python src/start_server.py; read -p \'Appuyez sur Entrée pour fermer...\'"'
                else:
                    cmd = f'gnome-terminal -- bash -c "cd {self.project_root} && python src/start_server.py; read -p \'Appuyez sur Entrée pour fermer...\'"'
                
                # Lancer dans un nouveau terminal Linux
                self.server_process = subprocess.Popen(
                    cmd,
                    shell=True
                )
            
            logger.info(f"🖥️ Serveur lancé dans le terminal PID: {self.server_process.pid}")
            
            # Attendre que le serveur démarre
            max_wait = 25
            for i in range(max_wait):
                try:
                    import requests
                    response = requests.get(f"{self.server_url}/health", timeout=2)
                    if response.status_code == 200:
                        logger.info(f"✅ Serveur démarré et accessible sur {self.server_url}")
                        return True
                except:
                    # Vérifier si le processus existe encore
                    if self.server_process.poll() is not None:
                        logger.error("❌ Le processus serveur s'est arrêté prématurément")
                        return False
                
                logger.info(f"⏳ Attente du serveur... ({i+1}/{max_wait})")
                time.sleep(1)
            
            logger.warning("❌ Timeout: Le serveur n'a pas démarré dans les temps")
            logger.info("💡 Le serveur continue de démarrer dans le terminal séparé")
            return True  # On continue quand même, le serveur peut encore démarrer
            
        except Exception as e:
            logger.error(f"❌ Erreur de démarrage du serveur: {e}")
            return False
    
    def stop_server(self):
        """Arrête le serveur de manière complète"""
        logger.info("🛑 Arrêt du serveur...")
        
        try:
            # 1. D'abord, essayer d'arrêter le serveur proprement via l'API
            try:
                logger.info("📡 Tentative d'arrêt propre via l'API...")
                import requests
                response = requests.post(f"{self.server_url}/shutdown", timeout=3)
                if response.status_code == 200:
                    logger.info("✅ Serveur arrêté proprement via l'API")
                    time.sleep(2)
                else:
                    logger.warning("⚠️ Arrêt API échoué, utilisation de la méthode forcée")
            except:
                logger.warning("⚠️ Arrêt API échoué, utilisation de la méthode forcée")
            
            # 2. Arrêter tous les processus Python serveurs
            logger.info("🔪 Arrêt des processus Python serveurs...")
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any('start_server.py' in str(cmd) or 'bridge_server' in str(cmd) for cmd in cmdline):
                            logger.info(f"   Arrêt du processus Python: {proc.info['pid']}")
                            proc.kill()
                            proc.wait(timeout=3)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass
            
            # 3. Vérifier et arrêter les processus sur le port 8080
            logger.info(f"� Vérification du port {self.server_port}...")
            for conn in psutil.net_connections():
                if conn.laddr.port == self.server_port and conn.status == psutil.CONN_LISTEN:
                    try:
                        proc = psutil.Process(conn.pid)
                        logger.info(f"   Arrêt du processus sur port {self.server_port}: {conn.pid}")
                        proc.kill()
                        proc.wait(timeout=3)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        pass
            
            # 4. Arrêter le processus terminal si nécessaire
            if self.server_process:
                try:
                    logger.info(f"🖥️ Fermeture du terminal serveur (PID: {self.server_process.pid})...")
                    
                    # Différentes méthodes selon l'OS
                    if os.name == 'nt':  # Windows
                        self.server_process.terminate()
                    else:  # Linux/Mac
                        self.server_process.terminate()
                    
                    self.server_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️ Timeout, forçage de l'arrêt du terminal...")
                    self.server_process.kill()
                except Exception as e:
                    logger.error(f"❌ Erreur lors de l'arrêt du terminal: {e}")
            
            # 5. Vérification finale
            time.sleep(1)
            remaining_connections = [conn for conn in psutil.net_connections() 
                                   if conn.laddr.port == self.server_port and conn.status == psutil.CONN_LISTEN]
            
            if remaining_connections:
                logger.warning(f"⚠️ Des processus utilisent encore le port {self.server_port}")
            else:
                logger.info(f"✅ Port {self.server_port} libéré")
            
            logger.info("✅ Arrêt du serveur terminé")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'arrêt: {e}")
            logger.info(f"💡 Vérifiez manuellement qu'aucun processus n'utilise le port {self.server_port}")
    
    def run_test(self, test_file, test_name):
        """Exécute un test spécifique"""
        logger.info(f"🧪 Exécution du test: {test_name}")
        logger.info("=" * 50)
        
        try:
            test_path = self.project_root / "tests" / test_file
            if not test_path.exists():
                logger.error(f"❌ Fichier de test non trouvé: {test_path}")
                return False
            
            # Exécuter le test
            result = subprocess.run(
                ["python", str(test_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Afficher la sortie
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            success = result.returncode == 0
            if success:
                logger.info(f"✅ Test {test_name} RÉUSSI")
            else:
                logger.error(f"❌ Test {test_name} ÉCHOUÉ (code: {result.returncode})")
            
            return success
            
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ Test {test_name} - Timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exécution du test {test_name}: {e}")
            return False
    
    def run_all_tests(self):
        """Lance tous les tests disponibles"""
        logger.info("🎯 DÉMARRAGE DE LA SUITE DE TESTS COMPLÈTE")
        logger.info("=" * 60)
        
        # Liste des tests à exécuter
        tests = [
            ("test_database.py", "Base de données"),
            ("test_auth.py", "Authentification"),
            ("test_cache_circuit_breaker.py", "Cache et Circuit Breaker"),
            ("test_ha_config.py", "Configuration Home Assistant"),
            ("test_permissions_simple.py", "Permissions"),
            ("test_web_interface.py", "Interface Web"),
            ("test_complete.py", "Tests Complets")
        ]
        
        results = {}
        
        for test_file, test_name in tests:
            test_path = self.project_root / "tests" / test_file
            if test_path.exists():
                success = self.run_test(test_file, test_name)
                results[test_name] = success
                logger.info("")  # Ligne vide pour la lisibilité
                time.sleep(2)  # Pause entre les tests
            else:
                logger.warning(f"⚠️ Test ignoré (fichier non trouvé): {test_file}")
                results[test_name] = None
        
        return results
    
    def display_summary(self, results):
        """Affiche le résumé des résultats"""
        logger.info("📊 RÉSUMÉ DES TESTS")
        logger.info("=" * 60)
        
        passed = 0
        failed = 0
        skipped = 0
        
        for test_name, result in results.items():
            if result is True:
                logger.info(f"✅ {test_name:<30} RÉUSSI")
                passed += 1
            elif result is False:
                logger.info(f"❌ {test_name:<30} ÉCHOUÉ")
                failed += 1
            else:
                logger.info(f"⚠️ {test_name:<30} IGNORÉ")
                skipped += 1
        
        total = passed + failed
        percentage = (passed / total * 100) if total > 0 else 0
        
        logger.info("=" * 60)
        logger.info(f"📈 RÉSULTATS FINAUX:")
        logger.info(f"   ✅ Réussis: {passed}")
        logger.info(f"   ❌ Échoués: {failed}")
        logger.info(f"   ⚠️ Ignorés: {skipped}")
        logger.info(f"   📊 Taux de réussite: {percentage:.1f}%")
        
        if failed == 0 and passed > 0:
            logger.info("🎉 TOUS LES TESTS ONT RÉUSSI !")
            return True
        else:
            logger.error("💥 CERTAINS TESTS ONT ÉCHOUÉ")
            return False

def main():
    """Fonction principale"""
    runner = AutoTestRunner()
    
    try:
        # 1. Arrêter les serveurs existants
        runner.kill_existing_servers()
        
        # 2. Démarrer le serveur
        if not runner.start_server():
            logger.error("❌ Impossible de démarrer le serveur, arrêt des tests")
            return 1
        
        # 3. Attendre un peu pour que le serveur soit stable
        time.sleep(3)
        
        # 4. Lancer tous les tests
        results = runner.run_all_tests()
        
        # 5. Afficher le résumé
        success = runner.display_summary(results)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("🛑 Tests interrompus par l'utilisateur")
        return 1
    except Exception as e:
        logger.error(f"❌ Erreur critique: {e}")
        return 1
    finally:
        # 6. Arrêter le serveur
        runner.stop_server()
        logger.info("🏁 Tests terminés")

if __name__ == "__main__":
    sys.exit(main())