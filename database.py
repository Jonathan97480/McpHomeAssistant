#!/usr/bin/env python3
"""
🗃️ Database Manager pour HTTP-MCP Bridge
Gestion de la base de données SQLite pour logs, erreurs et historique utilisateur
"""

import sqlite3
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

@dataclass
class LogEntry:
    """Entrée de log pour la base de données"""
    id: Optional[int] = None
    timestamp: str = ""
    level: str = ""
    message: str = ""
    module: str = ""
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    user_ip: Optional[str] = None
    extra_data: Optional[str] = None  # JSON string

@dataclass 
class RequestEntry:
    """Entrée de requête utilisateur pour l'historique"""
    id: Optional[int] = None
    timestamp: str = ""
    session_id: str = ""
    method: str = ""
    endpoint: str = ""
    params: str = ""  # JSON string
    response_time_ms: int = 0
    status_code: int = 0
    user_ip: Optional[str] = None
    user_agent: Optional[str] = None

@dataclass
class ErrorEntry:
    """Entrée d'erreur pour le suivi des problèmes"""
    id: Optional[int] = None
    timestamp: str = ""
    error_type: str = ""
    error_message: str = ""
    stack_trace: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    context: Optional[str] = None  # JSON string


class DatabaseManager:
    """Gestionnaire de base de données pour le bridge"""
    
    def __init__(self, db_path: str = "bridge_data.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        
    async def initialize(self):
        """Initialise la base de données et crée les tables"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            # Créer les tables
            await self._create_tables()
            
            # Créer les index pour les performances
            await self._create_indexes()
            
            logging.info(f"✅ Base de données initialisée: {self.db_path}")
            
        except Exception as e:
            logging.error(f"❌ Erreur initialisation BDD: {e}")
            raise
    
    async def _create_tables(self):
        """Crée les tables de la base de données"""
        
        # Table des logs
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                module TEXT,
                session_id TEXT,
                request_id TEXT,
                user_ip TEXT,
                extra_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des requêtes utilisateur (historique)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                method TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                params TEXT,
                response_time_ms INTEGER DEFAULT 0,
                status_code INTEGER DEFAULT 0,
                user_ip TEXT,
                user_agent TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des erreurs
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                session_id TEXT,
                request_id TEXT,
                context TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des statistiques (pour le monitoring)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                total_requests INTEGER DEFAULT 0,
                total_errors INTEGER DEFAULT 0,
                avg_response_time_ms REAL DEFAULT 0,
                unique_sessions INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tables d'authentification
        # Table des utilisateurs
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until DATETIME,
                last_login DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des sessions utilisateur
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                access_token TEXT UNIQUE NOT NULL,
                refresh_token TEXT UNIQUE NOT NULL,
                access_token_expires DATETIME NOT NULL,
                refresh_token_expires DATETIME NOT NULL,
                user_agent TEXT,
                ip_address TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Table des configurations Home Assistant
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS ha_configs (
                config_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                token_encrypted TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                last_test DATETIME,
                last_status TEXT DEFAULT 'unknown',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # Table de configuration système (pour clés de chiffrement)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_type TEXT UNIQUE NOT NULL,
                encryption_key TEXT,
                salt TEXT,
                config_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
    
    async def _create_indexes(self):
        """Crée les index pour optimiser les performances"""
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)",
            "CREATE INDEX IF NOT EXISTS idx_logs_session_id ON logs(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_requests_timestamp ON requests(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_requests_session_id ON requests(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_requests_endpoint ON requests(endpoint)",
            "CREATE INDEX IF NOT EXISTS idx_errors_timestamp ON errors(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_errors_type ON errors(error_type)",
            "CREATE INDEX IF NOT EXISTS idx_stats_date ON stats(date)",
            # Index pour l'authentification
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_access_token ON user_sessions(access_token)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_refresh_token ON user_sessions(refresh_token)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_is_active ON user_sessions(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(access_token_expires)",
            # Index pour les configurations Home Assistant
            "CREATE INDEX IF NOT EXISTS idx_ha_configs_user_id ON ha_configs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_ha_configs_is_active ON ha_configs(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_system_config_type ON system_config(config_type)"
        ]
        
        for index_sql in indexes:
            self.connection.execute(index_sql)
        
        self.connection.commit()
    
    async def insert_log(self, entry: LogEntry):
        """Insère une entrée de log"""
        try:
            cursor = self.connection.execute("""
                INSERT INTO logs (timestamp, level, message, module, session_id, request_id, user_ip, extra_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.timestamp,
                entry.level,
                entry.message,
                entry.module,
                entry.session_id,
                entry.request_id,
                entry.user_ip,
                entry.extra_data
            ))
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logging.error(f"❌ Erreur insertion log: {e}")
            return None
    
    async def insert_request(self, entry: RequestEntry):
        """Insère une entrée de requête utilisateur"""
        try:
            cursor = self.connection.execute("""
                INSERT INTO requests (timestamp, session_id, method, endpoint, params, response_time_ms, status_code, user_ip, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.timestamp,
                entry.session_id,
                entry.method,
                entry.endpoint,
                entry.params,
                entry.response_time_ms,
                entry.status_code,
                entry.user_ip,
                entry.user_agent
            ))
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logging.error(f"❌ Erreur insertion requête: {e}")
            return None
    
    async def insert_error(self, entry: ErrorEntry):
        """Insère une entrée d'erreur"""
        try:
            cursor = self.connection.execute("""
                INSERT INTO errors (timestamp, error_type, error_message, stack_trace, session_id, request_id, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.timestamp,
                entry.error_type,
                entry.error_message,
                entry.stack_trace,
                entry.session_id,
                entry.request_id,
                entry.context
            ))
            self.connection.commit()
            return cursor.lastrowid
            
        except Exception as e:
            logging.error(f"❌ Erreur insertion erreur: {e}")
            return None
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Supprime les données anciennes (plus de X jours)"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            # Compter les entrées à supprimer
            logs_count = self.connection.execute(
                "SELECT COUNT(*) FROM logs WHERE timestamp < ?", (cutoff_date,)
            ).fetchone()[0]
            
            requests_count = self.connection.execute(
                "SELECT COUNT(*) FROM requests WHERE timestamp < ?", (cutoff_date,)
            ).fetchone()[0]
            
            errors_count = self.connection.execute(
                "SELECT COUNT(*) FROM errors WHERE timestamp < ?", (cutoff_date,)
            ).fetchone()[0]
            
            # Supprimer les anciennes données
            self.connection.execute("DELETE FROM logs WHERE timestamp < ?", (cutoff_date,))
            self.connection.execute("DELETE FROM requests WHERE timestamp < ?", (cutoff_date,))
            self.connection.execute("DELETE FROM errors WHERE timestamp < ?", (cutoff_date,))
            self.connection.commit()
            
            # Optimiser la base de données (en dehors de la transaction)
            self.connection.execute("VACUUM")
            
            logging.info(f"🧹 Nettoyage BDD terminé: {logs_count} logs, {requests_count} requêtes, {errors_count} erreurs supprimées (>{days_to_keep} jours)")
            
            return {
                "logs_deleted": logs_count,
                "requests_deleted": requests_count,
                "errors_deleted": errors_count,
                "cutoff_date": cutoff_date
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur nettoyage BDD: {e}")
            return None
    
    async def get_stats(self, days: int = 7) -> Dict[str, Any]:
        """Récupère les statistiques des derniers jours"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Statistiques des requêtes
            request_stats = self.connection.execute("""
                SELECT 
                    COUNT(*) as total_requests,
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    MIN(timestamp) as first_request,
                    MAX(timestamp) as last_request
                FROM requests 
                WHERE timestamp >= ?
            """, (cutoff_date,)).fetchone()
            
            # Statistiques des erreurs par type
            error_stats = self.connection.execute("""
                SELECT 
                    error_type,
                    COUNT(*) as count
                FROM errors 
                WHERE timestamp >= ?
                GROUP BY error_type
                ORDER BY count DESC
            """, (cutoff_date,)).fetchall()
            
            # Top endpoints
            top_endpoints = self.connection.execute("""
                SELECT 
                    endpoint,
                    COUNT(*) as count,
                    AVG(response_time_ms) as avg_time
                FROM requests 
                WHERE timestamp >= ?
                GROUP BY endpoint
                ORDER BY count DESC
                LIMIT 10
            """, (cutoff_date,)).fetchall()
            
            return {
                "period_days": days,
                "requests": dict(request_stats) if request_stats else {},
                "errors_by_type": [dict(row) for row in error_stats],
                "top_endpoints": [dict(row) for row in top_endpoints],
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"❌ Erreur récupération stats: {e}")
            return {}
    
    async def import_daily_logs(self, log_file_path: str):
        """Importe les logs d'un fichier journalier vers la BDD"""
        try:
            if not os.path.exists(log_file_path):
                logging.warning(f"⚠️ Fichier log non trouvé: {log_file_path}")
                return 0
            
            imported_count = 0
            
            with open(log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        # Parser la ligne de log (format: timestamp - module - level - message)
                        parts = line.strip().split(' - ', 3)
                        if len(parts) >= 4:
                            timestamp_str, module, level, message = parts
                            
                            # Créer l'entrée de log
                            log_entry = LogEntry(
                                timestamp=timestamp_str,
                                level=level,
                                message=message,
                                module=module
                            )
                            
                            # Insérer en BDD
                            await self.insert_log(log_entry)
                            imported_count += 1
                            
                    except Exception as e:
                        logging.warning(f"⚠️ Erreur parsing ligne log: {e}")
                        continue
            
            logging.info(f"📥 Import terminé: {imported_count} logs importés depuis {log_file_path}")
            return imported_count
            
        except Exception as e:
            logging.error(f"❌ Erreur import logs: {e}")
            return 0
    
    async def close(self):
        """Ferme la connexion à la base de données"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logging.info("🔌 Connexion BDD fermée")
    
    async def fetch_one(self, query: str, params: tuple = ()):
        """Exécute une requête et retourne une seule ligne"""
        try:
            # Activer row_factory pour obtenir des dictionnaires
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if result:
                # Convertir Row en dictionnaire
                return dict(result)
            return None
        except Exception as e:
            logging.error(f"❌ Erreur fetch_one: {e}")
            return None
        finally:
            # Remettre row_factory par défaut
            self.connection.row_factory = None
    
    async def fetch_all(self, query: str, params: tuple = ()):
        """Exécute une requête et retourne toutes les lignes"""
        try:
            # Activer row_factory pour obtenir des dictionnaires
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convertir chaque Row en dictionnaire
            return [dict(row) for row in results]
        except Exception as e:
            logging.error(f"❌ Erreur fetch_all: {e}")
            return []
        finally:
            # Remettre row_factory par défaut
            self.connection.row_factory = None
    
    async def execute(self, query: str, params: tuple = ()):
        """Exécute une requête sans retour"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            
            # Si c'est un INSERT, retourner l'ID du dernier insert
            if query.strip().upper().startswith('INSERT'):
                return cursor.lastrowid
            else:
                return cursor.rowcount
        except Exception as e:
            logging.error(f"❌ Erreur execute: {e}")
            self.connection.rollback()
            return 0
    
    def fetch_one_sync(self, query: str, params: tuple = ()):
        """Exécute une requête et retourne une seule ligne (synchrone)"""
        try:
            # Activer row_factory pour obtenir des dictionnaires
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if result:
                # Convertir Row en dictionnaire
                return dict(result)
            return None
        except Exception as e:
            logging.error(f"❌ Erreur fetch_one_sync: {e}")
            return None
        finally:
            # Remettre row_factory par défaut
            self.connection.row_factory = None
    
    def fetch_all_sync(self, query: str, params: tuple = ()):
        """Exécute une requête et retourne toutes les lignes (synchrone)"""
        try:
            # Activer row_factory pour obtenir des dictionnaires
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Convertir chaque Row en dictionnaire
            return [dict(row) for row in results]
        except Exception as e:
            logging.error(f"❌ Erreur fetch_all_sync: {e}")
            return []
        finally:
            # Remettre row_factory par défaut
            self.connection.row_factory = None
    
    def execute_sync(self, query: str, params: tuple = ()):
        """Exécute une requête sans retour (synchrone)"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            
            # Si c'est un INSERT, retourner l'ID du dernier insert
            if query.strip().upper().startswith('INSERT'):
                return cursor.lastrowid
            else:
                return cursor.rowcount
        except Exception as e:
            logging.error(f"❌ Erreur execute_sync: {e}")
            self.connection.rollback()
            return 0


class DailyLogManager:
    """Gestionnaire des logs journaliers"""
    
    def __init__(self, logs_dir: str = "logs", db_manager: DatabaseManager = None):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        self.db_manager = db_manager
        self.current_log_file = None
        self.current_date = None
        
    def get_log_file_path(self, date: datetime = None) -> Path:
        """Retourne le chemin du fichier log pour une date donnée"""
        if date is None:
            date = datetime.now()
        filename = f"bridge_{date.strftime('%Y-%m-%d')}.log"
        return self.logs_dir / filename
    
    async def rotate_logs_if_needed(self):
        """Effectue la rotation des logs si on change de jour"""
        current_date = datetime.now().date()
        
        if self.current_date != current_date:
            # Nouveau jour = rotation nécessaire
            if self.current_log_file and self.current_date:
                # Archiver l'ancien fichier
                await self.archive_previous_day()
            
            # Commencer nouveau fichier
            self.current_date = current_date
            self.current_log_file = self.get_log_file_path()
            
            logging.info(f"🔄 Rotation logs: nouveau fichier {self.current_log_file}")
    
    async def archive_previous_day(self):
        """Archive les logs du jour précédent en BDD et supprime le fichier"""
        try:
            if not self.db_manager:
                logging.warning("⚠️ Pas de DB manager pour archivage")
                return
            
            previous_date = self.current_date - timedelta(days=1) if self.current_date else datetime.now().date() - timedelta(days=1)
            previous_log_file = self.get_log_file_path(datetime.combine(previous_date, datetime.min.time()))
            
            if previous_log_file.exists():
                # Importer en BDD
                imported_count = await self.db_manager.import_daily_logs(str(previous_log_file))
                
                # Supprimer le fichier après import réussi
                if imported_count > 0:
                    previous_log_file.unlink()
                    logging.info(f"🗃️ Logs archivés et fichier supprimé: {previous_log_file}")
                else:
                    logging.warning(f"⚠️ Aucun log importé depuis {previous_log_file}")
            
        except Exception as e:
            logging.error(f"❌ Erreur archivage logs: {e}")
    
    def get_current_log_file(self) -> Path:
        """Retourne le fichier log actuel"""
        if not self.current_log_file:
            self.current_date = datetime.now().date()
            self.current_log_file = self.get_log_file_path()
        
        return self.current_log_file


# Instance globale
db_manager = DatabaseManager()
log_manager = DailyLogManager(db_manager=db_manager)


async def setup_database():
    """Initialise le système de base de données"""
    await db_manager.initialize()
    await log_manager.rotate_logs_if_needed()


async def cleanup_old_data_task():
    """Tâche de nettoyage automatique des anciennes données"""
    while True:
        try:
            # Attendre jusqu'à 2h du matin
            now = datetime.now()
            next_cleanup = now.replace(hour=2, minute=0, second=0, microsecond=0)
            if now >= next_cleanup:
                next_cleanup += timedelta(days=1)
            
            wait_seconds = (next_cleanup - now).total_seconds()
            await asyncio.sleep(wait_seconds)
            
            # Effectuer le nettoyage
            logging.info("🧹 Début du nettoyage automatique des données anciennes")
            result = await db_manager.cleanup_old_data(days_to_keep=30)
            
            if result:
                logging.info(f"✅ Nettoyage terminé: {result}")
            
            # Rotation des logs
            await log_manager.rotate_logs_if_needed()
            
        except Exception as e:
            logging.error(f"❌ Erreur tâche nettoyage: {e}")
            await asyncio.sleep(3600)  # Réessayer dans 1h en cas d'erreur


if __name__ == "__main__":
    # Test du système de base de données
    async def test_database():
        await setup_database()
        
        # Test insertion log
        log_entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level="INFO",
            message="Test log message",
            module="test_module",
            session_id="test-session-123"
        )
        
        log_id = await db_manager.insert_log(log_entry)
        print(f"Log inséré avec ID: {log_id}")
        
        # Test statistiques
        stats = await db_manager.get_stats(days=7)
        print(f"Statistiques: {json.dumps(stats, indent=2)}")
        
        await db_manager.close()
    
    asyncio.run(test_database())