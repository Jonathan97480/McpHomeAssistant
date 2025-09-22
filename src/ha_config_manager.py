#!/usr/bin/env python3
"""
🏠 Home Assistant Configuration Manager
Gestionnaire sécurisé des configurations Home Assistant avec chiffrement des tokens
"""

import json
import hashlib
import secrets
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import urlparse, urljoin
import base64

import aiohttp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pydantic import BaseModel, Field, validator

# Import du système de base de données
from database import db_manager

logger = logging.getLogger(__name__)

class HAConnectionStatus(Enum):
    """Statuts de connexion Home Assistant"""
    UNKNOWN = "unknown"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    INVALID_TOKEN = "invalid_token"
    INVALID_URL = "invalid_url"

@dataclass
class HAConfig:
    """Configuration Home Assistant"""
    user_id: int
    url: str
    token_encrypted: str
    name: str = "Default HA"
    is_active: bool = True
    last_test: Optional[datetime] = None
    last_status: HAConnectionStatus = HAConnectionStatus.UNKNOWN
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class HAConfigCreate(BaseModel):
    """Modèle de création de configuration HA"""
    name: str = Field(..., min_length=1, max_length=100, description="Nom de la configuration")
    url: str = Field(..., description="URL de Home Assistant")
    token: str = Field(..., min_length=20, description="Token d'accès long terme")
    
    @validator('url')
    def validate_url(cls, v):
        """Valide l'URL Home Assistant"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL doit commencer par http:// ou https://')
        
        parsed = urlparse(v)
        if not parsed.netloc:
            raise ValueError('URL invalide')
            
        # Recommandation HTTPS pour la production
        if not v.startswith('https://') and not parsed.hostname in ['localhost', '127.0.0.1']:
            logger.warning(f"URL non sécurisée détectée: {v}. HTTPS recommandé pour la production.")
        
        return v.rstrip('/')
    
    @validator('token')
    def validate_token(cls, v):
        """Valide le format du token"""
        # Token HA format: llat_xxxxxxx ou similaire
        if len(v) < 20:
            raise ValueError('Token trop court')
        return v

class HAConfigUpdate(BaseModel):
    """Modèle de mise à jour de configuration HA"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = None
    token: Optional[str] = Field(None, min_length=20)
    is_active: Optional[bool] = None
    
    @validator('url')
    def validate_url(cls, v):
        if v is not None:
            return HAConfigCreate.validate_url(v)
        return v
    
    @validator('token')
    def validate_token(cls, v):
        if v is not None:
            return HAConfigCreate.validate_token(v)
        return v

class HAConfigResponse(BaseModel):
    """Réponse configuration HA (sans token)"""
    config_id: int
    name: str
    url: str
    is_active: bool
    last_test: Optional[datetime]
    last_status: str
    created_at: datetime
    updated_at: datetime

class HATestResult(BaseModel):
    """Résultat de test de connexion HA"""
    success: bool
    status: HAConnectionStatus
    message: str
    response_time_ms: Optional[int] = None
    ha_version: Optional[str] = None
    entities_count: Optional[int] = None
    tested_at: datetime

class HAConfigManager:
    """Gestionnaire des configurations Home Assistant"""
    
    def __init__(self):
        self.encryption_key = None
        self._session: Optional[aiohttp.ClientSession] = None
        # L'initialisation du chiffrement se fera de manière async
    
    async def initialize(self):
        """Initialise le gestionnaire HA (méthode async)"""
        if self.encryption_key is None:
            await self._setup_encryption()
    
    async def _setup_encryption(self):
        """Configure le chiffrement des tokens"""
        try:
            # Récupérer ou créer la clé de chiffrement
            encryption_data = await db_manager.fetch_one(
                "SELECT encryption_key, salt FROM system_config WHERE config_type = 'ha_encryption'"
            )
            
            if encryption_data:
                # Reconstituer la clé depuis la base
                stored_key = encryption_data['encryption_key']
                self.encryption_key = base64.urlsafe_b64decode(stored_key.encode())
            else:
                # Générer une nouvelle clé
                password = secrets.token_bytes(32)
                salt = secrets.token_bytes(16)
                
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                self.encryption_key = kdf.derive(password)
                
                # Stocker dans la base
                key_b64 = base64.urlsafe_b64encode(self.encryption_key).decode()
                salt_b64 = base64.urlsafe_b64encode(salt).decode()
                
                await db_manager.execute(
                    """INSERT INTO system_config (config_type, encryption_key, salt, created_at) 
                       VALUES (?, ?, ?, ?)""",
                    ('ha_encryption', key_b64, salt_b64, datetime.now())
                )
                
            logger.info("Système de chiffrement initialisé")
            
        except Exception as e:
            logger.error(f"Erreur initialisation chiffrement: {e}")
            raise
    
    def _encrypt_token(self, token: str) -> str:
        """Chiffre un token"""
        if self.encryption_key is None:
            raise RuntimeError("HAConfigManager not initialized. Call initialize() first.")
        try:
            fernet = Fernet(base64.urlsafe_b64encode(self.encryption_key))
            encrypted = fernet.encrypt(token.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Erreur chiffrement token: {e}")
            raise
    
    def _decrypt_token(self, encrypted_token: str) -> str:
        """Déchiffre un token"""
        if self.encryption_key is None:
            raise RuntimeError("HAConfigManager not initialized. Call initialize() first.")
        try:
            fernet = Fernet(base64.urlsafe_b64encode(self.encryption_key))
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Erreur déchiffrement token: {e}")
            raise
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Récupère ou crée une session HTTP"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close_session(self):
        """Ferme la session HTTP"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def test_ha_connection(self, url: str, token: str) -> HATestResult:
        """Test la connexion à Home Assistant"""
        start_time = time.time()
        
        try:
            session = await self.get_session()
            
            # Préparer l'URL et les headers
            api_url = urljoin(url.rstrip('/') + '/', 'api/')
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Test 1: Vérifier l'API de base
            async with session.get(api_url, headers=headers) as response:
                if response.status == 401:
                    return HATestResult(
                        success=False,
                        status=HAConnectionStatus.INVALID_TOKEN,
                        message="Token d'accès invalide",
                        response_time_ms=int((time.time() - start_time) * 1000),
                        tested_at=datetime.now()
                    )
                
                if response.status != 200:
                    return HATestResult(
                        success=False,
                        status=HAConnectionStatus.ERROR,
                        message=f"Erreur HTTP {response.status}",
                        response_time_ms=int((time.time() - start_time) * 1000),
                        tested_at=datetime.now()
                    )
                
                api_data = await response.json()
            
            # Test 2: Récupérer les infos système
            config_url = urljoin(url.rstrip('/') + '/', 'api/config')
            async with session.get(config_url, headers=headers) as response:
                if response.status == 200:
                    config_data = await response.json()
                    ha_version = config_data.get('version', 'Unknown')
                else:
                    ha_version = None
            
            # Test 3: Compter les entités
            states_url = urljoin(url.rstrip('/') + '/', 'api/states')
            entities_count = None
            try:
                async with session.get(states_url, headers=headers) as response:
                    if response.status == 200:
                        states_data = await response.json()
                        entities_count = len(states_data) if isinstance(states_data, list) else None
            except:
                pass  # Non critique
            
            response_time = int((time.time() - start_time) * 1000)
            
            return HATestResult(
                success=True,
                status=HAConnectionStatus.CONNECTED,
                message="Connexion réussie",
                response_time_ms=response_time,
                ha_version=ha_version,
                entities_count=entities_count,
                tested_at=datetime.now()
            )
            
        except aiohttp.ClientConnectorError:
            return HATestResult(
                success=False,
                status=HAConnectionStatus.INVALID_URL,
                message="Impossible de se connecter à l'URL",
                response_time_ms=int((time.time() - start_time) * 1000),
                tested_at=datetime.now()
            )
        except asyncio.TimeoutError:
            return HATestResult(
                success=False,
                status=HAConnectionStatus.ERROR,
                message="Timeout de connexion",
                response_time_ms=int((time.time() - start_time) * 1000),
                tested_at=datetime.now()
            )
        except Exception as e:
            logger.error(f"Erreur test connexion HA: {e}")
            return HATestResult(
                success=False,
                status=HAConnectionStatus.ERROR,
                message=f"Erreur: {str(e)}",
                response_time_ms=int((time.time() - start_time) * 1000),
                tested_at=datetime.now()
            )
    
    async def create_config(self, user_id: int, config_data: HAConfigCreate) -> HAConfig:
        """Crée une nouvelle configuration HA"""
        try:
            # Tester la connexion avant de sauvegarder
            test_result = await self.test_ha_connection(config_data.url, config_data.token)
            
            # Chiffrer le token
            encrypted_token = self._encrypt_token(config_data.token)
            
            # Sauvegarder en base
            now = datetime.now()
            config_id = await db_manager.execute(
                """INSERT INTO ha_configs 
                   (user_id, name, url, token_encrypted, is_active, last_test, last_status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, config_data.name, config_data.url, encrypted_token, True, 
                 test_result.tested_at, test_result.status.value, now, now)
            )
            
            # Logs
            logger.info(f"Configuration HA créée: {config_id} pour utilisateur {user_id}")
            
            return HAConfig(
                user_id=user_id,
                url=config_data.url,
                token_encrypted=encrypted_token,
                name=config_data.name,
                is_active=True,
                last_test=test_result.tested_at,
                last_status=test_result.status,
                created_at=now,
                updated_at=now
            )
            
        except Exception as e:
            logger.error(f"Erreur création config HA: {e}")
            raise
    
    async def get_config(self, user_id: int, config_id: Optional[int] = None) -> Optional[HAConfig]:
        """Récupère une configuration HA"""
        try:
            if config_id:
                config_data = await db_manager.fetch_one(
                    "SELECT * FROM ha_configs WHERE user_id = ? AND config_id = ?",
                    (user_id, config_id)
                )
            else:
                # Récupérer la config active par défaut
                config_data = await db_manager.fetch_one(
                    "SELECT * FROM ha_configs WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC",
                    (user_id,)
                )
            
            if not config_data:
                return None
            
            return HAConfig(
                user_id=config_data['user_id'],
                url=config_data['url'],
                token_encrypted=config_data['token_encrypted'],
                name=config_data['name'],
                is_active=config_data['is_active'],
                last_test=config_data['last_test'],
                last_status=HAConnectionStatus(config_data['last_status']),
                created_at=config_data['created_at'],
                updated_at=config_data['updated_at']
            )
            
        except Exception as e:
            logger.error(f"Erreur récupération config HA: {e}")
            return None
    
    async def get_decrypted_token(self, user_id: int, config_id: Optional[int] = None) -> Optional[str]:
        """Récupère le token déchiffré pour une configuration"""
        try:
            config = await self.get_config(user_id, config_id)
            if not config:
                return None
            
            return self._decrypt_token(config.token_encrypted)
            
        except Exception as e:
            logger.error(f"Erreur déchiffrement token: {e}")
            return None
    
    async def update_config(self, user_id: int, config_id: int, update_data: HAConfigUpdate) -> Optional[HAConfig]:
        """Met à jour une configuration HA"""
        try:
            # Récupérer la config existante
            existing_config = await self.get_config(user_id, config_id)
            if not existing_config:
                return None
            
            # Préparer les données de mise à jour
            updates = {}
            params = []
            
            if update_data.name is not None:
                updates['name'] = '?'
                params.append(update_data.name)
            
            if update_data.url is not None:
                updates['url'] = '?'
                params.append(update_data.url)
            
            if update_data.token is not None:
                # Chiffrer le nouveau token
                encrypted_token = self._encrypt_token(update_data.token)
                updates['token_encrypted'] = '?'
                params.append(encrypted_token)
            
            if update_data.is_active is not None:
                updates['is_active'] = '?'
                params.append(update_data.is_active)
            
            if not updates:
                return existing_config  # Aucune mise à jour
            
            updates['updated_at'] = '?'
            params.append(datetime.now())
            params.append(config_id)
            params.append(user_id)
            
            # Construire la requête
            set_clause = ', '.join([f"{col} = {placeholder}" for col, placeholder in updates.items()])
            query = f"UPDATE ha_configs SET {set_clause} WHERE config_id = ? AND user_id = ?"
            
            await db_manager.execute(query, tuple(params))
            
            # Retourner la config mise à jour
            return await self.get_config(user_id, config_id)
            
        except Exception as e:
            logger.error(f"Erreur mise à jour config HA: {e}")
            return None
    
    async def delete_config(self, user_id: int, config_id: int) -> bool:
        """Supprime une configuration HA"""
        try:
            result = await db_manager.execute(
                "DELETE FROM ha_configs WHERE config_id = ? AND user_id = ?",
                (config_id, user_id)
            )
            
            logger.info(f"Configuration HA supprimée: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression config HA: {e}")
            return False
    
    async def list_configs(self, user_id: int) -> List[HAConfigResponse]:
        """Liste toutes les configurations HA d'un utilisateur"""
        try:
            configs_data = await db_manager.fetch_all(
                "SELECT * FROM ha_configs WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            
            return [
                HAConfigResponse(
                    config_id=config['config_id'],
                    name=config['name'],
                    url=config['url'],
                    is_active=config['is_active'],
                    last_test=config['last_test'],
                    last_status=config['last_status'],
                    created_at=config['created_at'],
                    updated_at=config['updated_at']
                )
                for config in configs_data
            ]
            
        except Exception as e:
            logger.error(f"Erreur liste configs HA: {e}")
            return []

# Instance globale du gestionnaire
ha_config_manager = HAConfigManager()

# Fonctions de nettoyage
async def cleanup_ha_manager():
    """Nettoie les ressources du gestionnaire HA"""
    await ha_config_manager.close_session()