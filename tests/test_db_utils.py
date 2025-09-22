#!/usr/bin/env python3
"""
Utilitaires pour l'isolation des tests avec base de données
"""

import sqlite3
import os
import time
import uuid
from pathlib import Path

class TestDBManager:
    """Gestionnaire de base de données pour tests isolés"""
    
    def __init__(self, test_name: str = None):
        self.test_name = test_name or f"test_{int(time.time())}"
        self.db_path = f"test_db_{self.test_name}_{uuid.uuid4().hex[:8]}.db"
        self.original_db_path = None
        
    def setup_test_db(self):
        """Configure une base de données de test isolée"""
        try:
            # Sauvegarder le chemin original si il existe
            original_db = "bridge_data.db"
            if os.path.exists(original_db):
                self.original_db_path = original_db
                
            # Créer la structure de base dans la DB de test
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Créer les tables nécessaires
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    is_admin BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ha_url TEXT,
                    ha_token TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_token TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ha_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    ha_url TEXT,
                    ha_token TEXT,
                    ha_token_encrypted BLOB,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level TEXT,
                    message TEXT,
                    source TEXT,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            print(f"[DB] Base de données de test créée: {self.db_path}")
            return self.db_path
            
        except Exception as e:
            print(f"[DB] Erreur création DB test: {e}")
            return None
    
    def cleanup_test_db(self):
        """Nettoie la base de données de test"""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                print(f"[DB] Base de données de test supprimée: {self.db_path}")
                
        except Exception as e:
            print(f"[DB] Erreur suppression DB test: {e}")
    
    def get_unique_test_data(self):
        """Génère des données de test uniques"""
        timestamp = int(time.time())
        random_id = uuid.uuid4().hex[:8]
        
        return {
            'username': f'testuser_{timestamp}_{random_id}',
            'email': f'test_{timestamp}_{random_id}@example.com',
            'password': 'TestPassword123!',
            'ha_url': 'http://localhost:8123',
            'ha_token': f'test_token_{timestamp}_{random_id}'
        }

def setup_isolated_test(test_name: str = None):
    """Décorateur pour configurer un test isolé"""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            db_manager = TestDBManager(test_name)
            
            try:
                # Setup
                db_path = db_manager.setup_test_db()
                if not db_path:
                    raise Exception("Impossible de créer la DB de test")
                
                # Modifier temporairement la variable d'environnement
                original_db_env = os.environ.get('DATABASE_PATH')
                os.environ['DATABASE_PATH'] = db_path
                
                # Exécuter le test avec les données uniques
                test_data = db_manager.get_unique_test_data()
                result = test_func(test_data, *args, **kwargs)
                
                return result
                
            except Exception as e:
                print(f"[TEST] Erreur dans test isolé: {e}")
                raise
                
            finally:
                # Cleanup
                if original_db_env:
                    os.environ['DATABASE_PATH'] = original_db_env
                elif 'DATABASE_PATH' in os.environ:
                    del os.environ['DATABASE_PATH']
                
                db_manager.cleanup_test_db()
        
        return wrapper
    return decorator

# Utilitaires de nettoyage rapide
def clean_all_test_dbs():
    """Nettoie toutes les bases de données de test existantes"""
    current_dir = Path('.')
    test_dbs = list(current_dir.glob('test_db_*.db'))
    
    cleaned = 0
    for db_file in test_dbs:
        try:
            db_file.unlink()
            cleaned += 1
        except Exception as e:
            print(f"[CLEANUP] Impossible de supprimer {db_file}: {e}")
    
    if cleaned > 0:
        print(f"[CLEANUP] {cleaned} base(s) de données de test nettoyée(s)")
    
    return cleaned

def reset_main_db():
    """Remet à zéro la base de données principale (ATTENTION: destructeur!)"""
    main_db = "bridge_data.db"
    if os.path.exists(main_db):
        try:
            os.remove(main_db)
            print(f"[RESET] Base de données principale supprimée: {main_db}")
            return True
        except Exception as e:
            print(f"[RESET] Erreur suppression DB principale: {e}")
            return False
    return True

if __name__ == "__main__":
    # Test rapide du système
    print("[TEST] Test du système d'isolation DB...")
    
    @setup_isolated_test("demo")
    def test_demo(test_data):
        print(f"[DEMO] Données de test: {test_data}")
        return True
    
    # Test
    result = test_demo()
    print(f"[TEST] Résultat: {result}")
    
    # Nettoyage final
    clean_all_test_dbs()