#!/usr/bin/env python3
"""
🔐 Système d'authentification pour HTTP-MCP Bridge
Gestion des utilisateurs, sessions JWT et sécurité
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

from jose import JWTError, jwt
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, EmailStr, validator

from database import db_manager
import logging

logger = logging.getLogger(__name__)

# Configuration JWT
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Configuration de sécurité simplifiée
HASH_ALGORITHM = "sha256"
SALT_LENGTH = 32

def hash_password(password: str) -> str:
    """Hache un mot de passe avec salt et SHA-256"""
    salt = secrets.token_bytes(SALT_LENGTH)
    password_hash = hashlib.pbkdf2_hmac(HASH_ALGORITHM, password.encode('utf-8'), salt, 100000)
    # Combine salt + hash en hex
    return salt.hex() + password_hash.hex()

def verify_password(password: str, hashed: str) -> bool:
    """Vérifie un mot de passe contre un hash"""
    if len(hashed) < SALT_LENGTH * 2:
        return False
    
    # Extraire le salt et le hash
    salt_hex = hashed[:SALT_LENGTH * 2]
    hash_hex = hashed[SALT_LENGTH * 2:]
    
    salt = bytes.fromhex(salt_hex)
    password_hash = hashlib.pbkdf2_hmac(HASH_ALGORITHM, password.encode('utf-8'), salt, 100000)
    
    return password_hash.hex() == hash_hex


class UserRole(str, Enum):
    """Rôles d'utilisateur"""
    ADMIN = "admin"
    USER = "user"


class UserCreate(BaseModel):
    """Modèle pour création d'utilisateur"""
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Valide la complexité du mot de passe"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """Modèle pour connexion utilisateur"""
    username: str
    password: str


class RefreshRequest(BaseModel):
    """Modèle pour demande de rafraîchissement de token"""
    refresh_token: str


class UserResponse(BaseModel):
    """Modèle de réponse utilisateur (sans mot de passe)"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime


class TokenResponse(BaseModel):
    """Réponse avec tokens d'authentification"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Données extraites du token"""
    user_id: int
    username: str
    role: UserRole


class AuthManager:
    """Gestionnaire d'authentification"""
    
    def __init__(self):
        self.max_failed_attempts = 5
        self.lockout_duration_minutes = 30
    
    async def initialize(self):
        """Initialise le système d'authentification"""
        try:
            logger.info("🔐 Initializing authentication system...")
            
            # Créer un utilisateur admin par défaut s'il n'existe pas
            admin_exists = await self.get_user_by_username("admin")
            if not admin_exists:
                logger.info("👤 Creating default admin user...")
                
                admin_user = UserCreate(
                    username="admin",
                    email="admin@example.com",
                    password="Admin123!",
                    full_name="Administrator"
                )
                
                await self.create_user(admin_user, role=UserRole.ADMIN)
                logger.info("✅ Default admin user created (username: admin, password: Admin123!)")
            
            logger.info("✅ Authentication system initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize auth system: {e}")
            raise
    
    async def create_user(self, user_data: UserCreate, role: UserRole = UserRole.USER) -> UserResponse:
        """Crée un nouvel utilisateur"""
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = await self.get_user_by_username(user_data.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            
            existing_email = await self.get_user_by_email(user_data.email)
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            
            # Hacher le mot de passe
            hashed_password = hash_password(user_data.password)
            
            # Insérer l'utilisateur
            query = """
                INSERT INTO users (username, email, full_name, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            now = datetime.utcnow()
            user_id = await db_manager.execute(
                query,
                (user_data.username, user_data.email, user_data.full_name, hashed_password, role.value, now)
            )
            
            # Récupérer l'utilisateur créé
            user = await self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
            
            logger.info(f"✅ User created: {user.username} ({user.role})")
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to create user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed"
            )
    
    async def authenticate_user(self, username: str, password: str, 
                               user_agent: Optional[str] = None,
                               ip_address: Optional[str] = None) -> Optional[UserResponse]:
        """Authentifie un utilisateur"""
        try:
            # Récupérer l'utilisateur
            user = await self.get_user_by_username(username)
            if not user:
                # Simuler la même charge que si l'utilisateur existait
                hash_password("dummy_password")
                return None
            
            # Vérifier si le compte est verrouillé
            if await self._is_user_locked(user.id):
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Account locked for {self.lockout_duration_minutes} minutes due to too many failed attempts"
                )
            
            # Récupérer le hash du mot de passe
            password_hash = await self._get_user_password_hash(user.id)
            if not password_hash:
                return None
            
            # Vérifier le mot de passe
            if not verify_password(password, password_hash):
                await self._increment_failed_attempts(user.id)
                return None
            
            # Réinitialiser les tentatives échouées
            await self._reset_failed_attempts(user.id)
            
            # Mettre à jour la dernière connexion
            await self._update_last_login(user.id)
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return None
    
    async def create_user_session(self, user: UserResponse, user_agent: Optional[str] = None,
                                 ip_address: Optional[str] = None) -> TokenResponse:
        """Crée une session utilisateur avec tokens JWT"""
        try:
            # Créer les tokens
            access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
            access_token = self._create_access_token(
                data={"sub": str(user.id), "username": user.username, "role": user.role},
                expires_delta=access_token_expires
            )
            
            refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            refresh_token = self._create_refresh_token(
                data={"sub": str(user.id)},
                expires_delta=refresh_token_expires
            )
            
            # Sauvegarder la session en base
            now = datetime.utcnow()
            access_expires = now + access_token_expires
            refresh_expires = now + refresh_token_expires
            
            query = """
                INSERT INTO user_sessions 
                (user_id, access_token, refresh_token, access_token_expires, 
                 refresh_token_expires, user_agent, ip_address, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            await db_manager.execute(
                query,
                (user.id, access_token, refresh_token, access_expires, refresh_expires, user_agent, ip_address, now, now)
            )
            
            # Nettoyer les anciennes sessions
            await self._cleanup_expired_sessions(user.id)
            
            logger.info(f"✅ Session created for user: {user.username}")
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=int(access_token_expires.total_seconds()),
                user=user
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create session: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Session creation failed"
            )
    
    async def refresh_token(self, refresh_token: str) -> Optional[TokenResponse]:
        """Rafraîchit un token d'accès"""
        try:
            # Vérifier si le token de rafraîchissement existe et est valide
            query = """
                SELECT us.*, u.username, u.role 
                FROM user_sessions us 
                JOIN users u ON us.user_id = u.id 
                WHERE us.refresh_token = ? AND us.refresh_token_expires > ? AND us.is_active = 1
            """
            session_data = await db_manager.fetch_one(query, (refresh_token, datetime.utcnow()))
            
            if not session_data:
                return None
            
            # Récupérer l'utilisateur
            user = await self.get_user_by_id(session_data['user_id'])
            if not user:
                return None
            
            # Créer un nouveau token d'accès
            access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
            new_access_token = self._create_access_token(
                data={"sub": str(user.id), "username": user.username, "role": user.role},
                expires_delta=access_token_expires
            )
            
            # Mettre à jour la session
            new_access_expires = datetime.utcnow() + access_token_expires
            update_query = """
                UPDATE user_sessions 
                SET access_token = ?, access_token_expires = ?, updated_at = ?
                WHERE refresh_token = ?
            """
            await db_manager.execute(
                update_query,
                (new_access_token, new_access_expires, datetime.utcnow(), refresh_token)
            )
            
            return TokenResponse(
                access_token=new_access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=int(access_token_expires.total_seconds()),
                user=user
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to refresh token: {e}")
            return None
    
    async def revoke_session(self, access_token: str) -> bool:
        """Révoque une session utilisateur"""
        try:
            query = "UPDATE user_sessions SET is_active = 0 WHERE access_token = ?"
            rows_affected = await db_manager.execute(query, (access_token,))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"❌ Failed to revoke session: {e}")
            return False
    
    def _create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token d'accès JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def _create_refresh_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token de rafraîchissement JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            user_id: int = int(payload.get("sub"))
            username: str = payload.get("username")
            role: str = payload.get("role")
            
            if user_id is None or username is None:
                return None
            
            return TokenData(
                user_id=user_id,
                username=username,
                role=UserRole(role)
            )
        except JWTError:
            return None
    
    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """Récupère un utilisateur par ID"""
        try:
            query = "SELECT * FROM users WHERE id = ? AND is_active = 1"
            user_data = await db_manager.fetch_one(query, (user_id,))
            
            if user_data:
                return UserResponse(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    full_name=user_data['full_name'],
                    role=UserRole(user_data['role']),
                    is_active=user_data['is_active'],
                    last_login=user_data['last_login'],
                    created_at=user_data['created_at']
                )
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get user by ID: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        """Récupère un utilisateur par nom d'utilisateur"""
        try:
            query = "SELECT * FROM users WHERE username = ? AND is_active = 1"
            user_data = await db_manager.fetch_one(query, (username,))
            
            if user_data:
                return UserResponse(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    full_name=user_data['full_name'],
                    role=UserRole(user_data['role']),
                    is_active=user_data['is_active'],
                    last_login=user_data['last_login'],
                    created_at=user_data['created_at']
                )
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get user by username: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Récupère un utilisateur par email"""
        try:
            query = "SELECT * FROM users WHERE email = ? AND is_active = 1"
            user_data = await db_manager.fetch_one(query, (email,))
            
            if user_data:
                return UserResponse(
                    id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    full_name=user_data['full_name'],
                    role=UserRole(user_data['role']),
                    is_active=user_data['is_active'],
                    last_login=user_data['last_login'],
                    created_at=user_data['created_at']
                )
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get user by email: {e}")
            return None
    
    async def get_active_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Récupère les sessions actives d'un utilisateur"""
        try:
            query = """
                SELECT id, user_agent, ip_address, created_at, access_token_expires
                FROM user_sessions 
                WHERE user_id = ? AND is_active = 1 AND access_token_expires > ?
                ORDER BY created_at DESC
            """
            sessions = await db_manager.fetch_all(query, (user_id, datetime.utcnow()))
            return sessions
        except Exception as e:
            logger.error(f"❌ Failed to get active sessions: {e}")
            return []
    
    async def _get_user_password_hash(self, user_id: int) -> Optional[str]:
        """Récupère le hash du mot de passe"""
        try:
            query = "SELECT password_hash FROM users WHERE id = ?"
            result = await db_manager.fetch_one(query, (user_id,))
            return result['password_hash'] if result else None
        except Exception as e:
            logger.error(f"❌ Failed to get password hash: {e}")
            return None
    
    async def _is_user_locked(self, user_id: int) -> bool:
        """Vérifie si un utilisateur est verrouillé"""
        try:
            query = "SELECT failed_login_attempts, locked_until FROM users WHERE id = ?"
            result = await db_manager.fetch_one(query, (user_id,))
            
            if not result:
                return False
            
            if result['locked_until'] and datetime.fromisoformat(result['locked_until']) > datetime.utcnow():
                return True
            
            return False
        except Exception as e:
            logger.error(f"❌ Failed to check if user is locked: {e}")
            return False
    
    async def _increment_failed_attempts(self, user_id: int):
        """Incrémente les tentatives de connexion échouées"""
        try:
            # Incrémenter le compteur
            query = "UPDATE users SET failed_login_attempts = failed_login_attempts + 1 WHERE id = ?"
            await db_manager.execute(query, (user_id,))
            
            # Vérifier si on doit verrouiller le compte
            check_query = "SELECT failed_login_attempts FROM users WHERE id = ?"
            result = await db_manager.fetch_one(check_query, (user_id,))
            
            if result and result['failed_login_attempts'] >= self.max_failed_attempts:
                lockout_time = datetime.utcnow() + timedelta(minutes=self.lockout_duration_minutes)
                lock_query = """
                    UPDATE users 
                    SET locked_until = ? 
                    WHERE id = ?
                """
                await db_manager.execute(lock_query, (lockout_time, user_id))
                logger.warning(f"🔒 User {user_id} locked until {lockout_time}")
        except Exception as e:
            logger.error(f"❌ Failed to increment failed attempts: {e}")
    
    async def _reset_failed_attempts(self, user_id: int):
        """Remet à zéro les tentatives échouées"""
        try:
            query = "UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE id = ?"
            await db_manager.execute(query, (user_id,))
        except Exception as e:
            logger.error(f"❌ Failed to reset failed attempts: {e}")
    
    async def _update_last_login(self, user_id: int):
        """Met à jour la dernière connexion"""
        try:
            query = "UPDATE users SET last_login = ? WHERE id = ?"
            await db_manager.execute(query, (datetime.utcnow(), user_id))
        except Exception as e:
            logger.error(f"❌ Failed to update last login: {e}")
    
    async def _cleanup_expired_sessions(self, user_id: int):
        """Nettoie les sessions expirées"""
        try:
            now = datetime.utcnow()
            query = """
                UPDATE user_sessions 
                SET is_active = 0 
                WHERE (access_token_expires < ? OR refresh_token_expires < ?) AND user_id = ?
            """
            await db_manager.execute(query, (now, now, user_id))
        except Exception as e:
            logger.error(f"❌ Failed to cleanup expired sessions: {e}")


# Instance globale du gestionnaire d'authentification
auth_manager = AuthManager()