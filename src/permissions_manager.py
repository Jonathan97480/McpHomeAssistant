#!/usr/bin/env python3
"""
🔐 Permissions Manager
Gestionnaire des permissions granulaires par outil MCP avec cache et héritage
"""

import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

from pydantic import BaseModel, Field

# Import du système de base de données
from database import db_manager

logger = logging.getLogger(__name__)

class PermissionType(Enum):
    """Types de permissions"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"  # Pour les appels d'outils

class ToolCategory(Enum):
    """Catégories d'outils MCP"""
    GENERAL = "general"
    LIGHTS = "lights"
    SENSORS = "sensors"
    CLIMATE = "climate"
    MEDIA = "media"
    SCRIPTS = "scripts"
    AUTOMATION = "automation"
    SECURITY = "security"
    ENERGY = "energy"
    DIAGNOSTICS = "diagnostics"

@dataclass
class ToolPermission:
    """Permission pour un outil spécifique"""
    tool_name: str
    can_read: bool = True
    can_write: bool = False
    is_enabled: bool = True
    tool_category: str = "general"
    description: Optional[str] = None
    last_used: Optional[datetime] = None

@dataclass
class UserPermissionCache:
    """Cache des permissions utilisateur"""
    user_id: int
    permissions: Dict[str, ToolPermission]
    last_updated: datetime
    cache_ttl: int = 300  # 5 minutes par défaut

class DefaultPermissionCreate(BaseModel):
    """Modèle pour créer des permissions par défaut"""
    tool_name: str = Field(..., min_length=1, max_length=100)
    can_read: bool = True
    can_write: bool = False
    is_enabled: bool = True
    tool_category: str = "general"
    description: Optional[str] = Field(None, max_length=500)

class UserPermissionUpdate(BaseModel):
    """Modèle pour mettre à jour les permissions utilisateur"""
    can_read: Optional[bool] = None
    can_write: Optional[bool] = None
    is_enabled: Optional[bool] = None
    custom_settings: Optional[Dict[str, Any]] = None

class PermissionSummary(BaseModel):
    """Résumé des permissions d'un utilisateur"""
    tool_name: str
    can_read: bool
    can_write: bool
    is_enabled: bool
    tool_category: str
    description: Optional[str]
    is_custom: bool = False  # True si l'utilisateur a personnalisé cette permission
    last_used: Optional[datetime] = None

class BulkPermissionUpdate(BaseModel):
    """Mise à jour en masse des permissions"""
    tool_names: List[str]
    can_read: Optional[bool] = None
    can_write: Optional[bool] = None
    is_enabled: Optional[bool] = None

class PermissionsManager:
    """Gestionnaire des permissions granulaires"""
    
    def __init__(self):
        self.permission_cache: Dict[int, UserPermissionCache] = {}
        self.default_permissions_cache: Optional[Dict[str, ToolPermission]] = None
        self.default_cache_ttl = 600  # 10 minutes pour les permissions par défaut
        self.last_default_update = datetime.min
        
        # Permissions par défaut pour les outils courants HA
        self.builtin_permissions = {
            # Éclairage
            "light.toggle": ToolPermission("light.toggle", True, True, True, "lights", "Allumer/éteindre les lumières"),
            "light.set_brightness": ToolPermission("light.set_brightness", True, True, True, "lights", "Régler la luminosité"),
            "light.set_color": ToolPermission("light.set_color", True, True, True, "lights", "Changer la couleur"),
            
            # Capteurs
            "sensor.read_temperature": ToolPermission("sensor.read_temperature", True, False, True, "sensors", "Lire les capteurs de température"),
            "sensor.read_humidity": ToolPermission("sensor.read_humidity", True, False, True, "sensors", "Lire les capteurs d'humidité"),
            "sensor.read_motion": ToolPermission("sensor.read_motion", True, False, True, "sensors", "Lire les détecteurs de mouvement"),
            
            # Climat
            "climate.set_temperature": ToolPermission("climate.set_temperature", True, True, True, "climate", "Régler la température"),
            "climate.set_mode": ToolPermission("climate.set_mode", True, True, True, "climate", "Changer le mode climatisation"),
            
            # Médias
            "media_player.play": ToolPermission("media_player.play", True, True, True, "media", "Contrôler la lecture média"),
            "media_player.volume": ToolPermission("media_player.volume", True, True, True, "media", "Régler le volume"),
            
            # Scripts et automatisations
            "script.run": ToolPermission("script.run", True, True, False, "scripts", "Exécuter des scripts"),
            "automation.trigger": ToolPermission("automation.trigger", True, True, False, "automation", "Déclencher des automatisations"),
            
            # Sécurité
            "alarm.arm": ToolPermission("alarm.arm", True, True, False, "security", "Armer l'alarme"),
            "alarm.disarm": ToolPermission("alarm.disarm", True, True, False, "security", "Désarmer l'alarme"),
            "lock.control": ToolPermission("lock.control", True, True, False, "security", "Contrôler les serrures"),
            
            # Énergie
            "energy.usage": ToolPermission("energy.usage", True, False, True, "energy", "Consulter la consommation énergétique"),
            
            # Diagnostics
            "system.diagnostics": ToolPermission("system.diagnostics", True, False, False, "diagnostics", "Diagnostics système"),
            "log.view": ToolPermission("log.view", True, False, False, "diagnostics", "Consulter les logs")
        }
    
    async def initialize(self):
        """Initialise le gestionnaire de permissions"""
        try:
            # Créer les permissions par défaut si elles n'existent pas
            await self._ensure_default_permissions()
            logger.info("🔐 Gestionnaire de permissions initialisé")
        except Exception as e:
            logger.error(f"Erreur initialisation permissions: {e}")
            raise
    
    async def _ensure_default_permissions(self):
        """Assure que les permissions par défaut existent en base"""
        try:
            # Vérifier les permissions existantes
            existing_perms = await db_manager.fetch_all(
                "SELECT tool_name FROM default_permissions"
            )
            existing_tools = {perm['tool_name'] for perm in existing_perms}
            
            # Ajouter les permissions manquantes
            for tool_name, perm in self.builtin_permissions.items():
                if tool_name not in existing_tools:
                    await db_manager.execute(
                        """INSERT INTO default_permissions 
                           (tool_name, can_read, can_write, is_enabled, tool_category, description, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (perm.tool_name, perm.can_read, perm.can_write, perm.is_enabled, 
                         perm.tool_category, perm.description, datetime.now(), datetime.now())
                    )
            
            logger.info(f"✅ {len(self.builtin_permissions)} permissions par défaut assurées")
            
        except Exception as e:
            logger.error(f"Erreur création permissions par défaut: {e}")
            raise
    
    async def get_default_permissions(self) -> Dict[str, ToolPermission]:
        """Récupère les permissions par défaut avec cache"""
        try:
            # Vérifier le cache
            if (self.default_permissions_cache is not None and 
                (datetime.now() - self.last_default_update).total_seconds() < self.default_cache_ttl):
                return self.default_permissions_cache
            
            # Charger depuis la base
            perms_data = await db_manager.fetch_all(
                "SELECT * FROM default_permissions ORDER BY tool_category, tool_name"
            )
            
            permissions = {}
            for perm in perms_data:
                permissions[perm['tool_name']] = ToolPermission(
                    tool_name=perm['tool_name'],
                    can_read=perm['can_read'],
                    can_write=perm['can_write'],
                    is_enabled=perm['is_enabled'],
                    tool_category=perm['tool_category'],
                    description=perm['description']
                )
            
            # Mettre à jour le cache
            self.default_permissions_cache = permissions
            self.last_default_update = datetime.now()
            
            return permissions
            
        except Exception as e:
            logger.error(f"Erreur récupération permissions par défaut: {e}")
            return {}
    
    async def get_user_permissions(self, user_id: int, force_refresh: bool = False) -> Dict[str, ToolPermission]:
        """Récupère les permissions d'un utilisateur avec cache"""
        try:
            # Vérifier le cache utilisateur
            if not force_refresh and user_id in self.permission_cache:
                cache = self.permission_cache[user_id]
                if (datetime.now() - cache.last_updated).total_seconds() < cache.cache_ttl:
                    return cache.permissions
            
            # Charger les permissions par défaut
            default_perms = await self.get_default_permissions()
            
            # Charger les permissions personnalisées de l'utilisateur
            user_perms_data = await db_manager.fetch_all(
                "SELECT * FROM user_tool_permissions WHERE user_id = ?",
                (user_id,)
            )
            
            # Construire le dictionnaire des permissions finales
            final_permissions = {}
            
            # Commencer par les permissions par défaut
            for tool_name, default_perm in default_perms.items():
                final_permissions[tool_name] = ToolPermission(
                    tool_name=default_perm.tool_name,
                    can_read=default_perm.can_read,
                    can_write=default_perm.can_write,
                    is_enabled=default_perm.is_enabled,
                    tool_category=default_perm.tool_category,
                    description=default_perm.description
                )
            
            # Appliquer les personnalisations utilisateur
            for user_perm in user_perms_data:
                tool_name = user_perm['tool_name']
                
                # Si l'outil existe dans les permissions par défaut
                if tool_name in final_permissions:
                    perm = final_permissions[tool_name]
                    perm.can_read = user_perm['can_read']
                    perm.can_write = user_perm['can_write']
                    perm.is_enabled = user_perm['is_enabled']
                    perm.last_used = user_perm['last_used']
                else:
                    # Outil personnalisé pas dans les défauts
                    final_permissions[tool_name] = ToolPermission(
                        tool_name=tool_name,
                        can_read=user_perm['can_read'],
                        can_write=user_perm['can_write'],
                        is_enabled=user_perm['is_enabled'],
                        tool_category="general",
                        last_used=user_perm['last_used']
                    )
            
            # Mettre à jour le cache
            self.permission_cache[user_id] = UserPermissionCache(
                user_id=user_id,
                permissions=final_permissions,
                last_updated=datetime.now()
            )
            
            return final_permissions
            
        except Exception as e:
            logger.error(f"Erreur récupération permissions utilisateur {user_id}: {e}")
            return {}
    
    async def check_permission(self, user_id: int, tool_name: str, permission_type: PermissionType) -> bool:
        """Vérifie si un utilisateur a une permission spécifique"""
        try:
            user_perms = await self.get_user_permissions(user_id)
            
            if tool_name not in user_perms:
                logger.warning(f"Outil {tool_name} non trouvé dans les permissions utilisateur {user_id}")
                return False
            
            perm = user_perms[tool_name]
            
            # Vérifier si l'outil est activé
            if not perm.is_enabled:
                return False
            
            # Vérifier le type de permission
            if permission_type == PermissionType.READ:
                return perm.can_read
            elif permission_type == PermissionType.WRITE or permission_type == PermissionType.EXECUTE:
                return perm.can_write
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur vérification permission {tool_name} pour utilisateur {user_id}: {e}")
            return False
    
    async def update_user_permission(self, user_id: int, tool_name: str, updates: UserPermissionUpdate) -> bool:
        """Met à jour une permission utilisateur spécifique"""
        try:
            # Vérifier si la permission existe déjà
            existing = await db_manager.fetch_one(
                "SELECT * FROM user_tool_permissions WHERE user_id = ? AND tool_name = ?",
                (user_id, tool_name)
            )
            
            now = datetime.now()
            
            if existing:
                # Mettre à jour la permission existante
                set_clauses = []
                params = []
                
                if updates.can_read is not None:
                    set_clauses.append("can_read = ?")
                    params.append(updates.can_read)
                
                if updates.can_write is not None:
                    set_clauses.append("can_write = ?")
                    params.append(updates.can_write)
                
                if updates.is_enabled is not None:
                    set_clauses.append("is_enabled = ?")
                    params.append(updates.is_enabled)
                
                if updates.custom_settings is not None:
                    set_clauses.append("custom_settings = ?")
                    params.append(json.dumps(updates.custom_settings))
                
                set_clauses.append("updated_at = ?")
                params.extend([now, user_id, tool_name])
                
                query = f"UPDATE user_tool_permissions SET {', '.join(set_clauses)} WHERE user_id = ? AND tool_name = ?"
                await db_manager.execute(query, tuple(params))
                
            else:
                # Créer une nouvelle permission personnalisée
                # Récupérer les valeurs par défaut
                default_perms = await self.get_default_permissions()
                default_perm = default_perms.get(tool_name)
                
                can_read = updates.can_read if updates.can_read is not None else (default_perm.can_read if default_perm else True)
                can_write = updates.can_write if updates.can_write is not None else (default_perm.can_write if default_perm else False)
                is_enabled = updates.is_enabled if updates.is_enabled is not None else (default_perm.is_enabled if default_perm else True)
                custom_settings = json.dumps(updates.custom_settings) if updates.custom_settings else None
                
                await db_manager.execute(
                    """INSERT INTO user_tool_permissions 
                       (user_id, tool_name, can_read, can_write, is_enabled, custom_settings, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, tool_name, can_read, can_write, is_enabled, custom_settings, now, now)
                )
            
            # Invalider le cache utilisateur
            if user_id in self.permission_cache:
                del self.permission_cache[user_id]
            
            logger.info(f"Permission {tool_name} mise à jour pour utilisateur {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour permission {tool_name} pour utilisateur {user_id}: {e}")
            return False
    
    async def update_bulk_permissions(self, user_id: int, bulk_update: BulkPermissionUpdate) -> int:
        """Met à jour plusieurs permissions en une fois"""
        try:
            updated_count = 0
            
            for tool_name in bulk_update.tool_names:
                update = UserPermissionUpdate(
                    can_read=bulk_update.can_read,
                    can_write=bulk_update.can_write,
                    is_enabled=bulk_update.is_enabled
                )
                
                if await self.update_user_permission(user_id, tool_name, update):
                    updated_count += 1
            
            logger.info(f"Mise à jour en masse: {updated_count}/{len(bulk_update.tool_names)} permissions pour utilisateur {user_id}")
            return updated_count
            
        except Exception as e:
            logger.error(f"Erreur mise à jour en masse pour utilisateur {user_id}: {e}")
            return 0
    
    async def get_user_permission_summary(self, user_id: int) -> List[PermissionSummary]:
        """Récupère un résumé des permissions d'un utilisateur"""
        try:
            user_perms = await self.get_user_permissions(user_id)
            default_perms = await self.get_default_permissions()
            
            # Récupérer les permissions personnalisées
            custom_perms = await db_manager.fetch_all(
                "SELECT tool_name FROM user_tool_permissions WHERE user_id = ?",
                (user_id,)
            )
            custom_tools = {perm['tool_name'] for perm in custom_perms}
            
            summary = []
            
            for tool_name, perm in user_perms.items():
                is_custom = tool_name in custom_tools
                
                summary.append(PermissionSummary(
                    tool_name=perm.tool_name,
                    can_read=perm.can_read,
                    can_write=perm.can_write,
                    is_enabled=perm.is_enabled,
                    tool_category=perm.tool_category,
                    description=perm.description,
                    is_custom=is_custom,
                    last_used=perm.last_used
                ))
            
            # Trier par catégorie puis par nom
            summary.sort(key=lambda x: (x.tool_category, x.tool_name))
            
            return summary
            
        except Exception as e:
            logger.error(f"Erreur récupération résumé permissions pour utilisateur {user_id}: {e}")
            return []
    
    async def record_tool_usage(self, user_id: int, tool_name: str):
        """Enregistre l'utilisation d'un outil"""
        try:
            await db_manager.execute(
                """UPDATE user_tool_permissions 
                   SET last_used = ?, updated_at = ?
                   WHERE user_id = ? AND tool_name = ?""",
                (datetime.now(), datetime.now(), user_id, tool_name)
            )
            
            # Invalider le cache pour cet utilisateur
            if user_id in self.permission_cache:
                del self.permission_cache[user_id]
                
        except Exception as e:
            logger.warning(f"Erreur enregistrement utilisation outil {tool_name}: {e}")
    
    async def get_tools_by_category(self) -> Dict[str, List[str]]:
        """Récupère les outils groupés par catégorie"""
        try:
            default_perms = await self.get_default_permissions()
            
            categories = defaultdict(list)
            for tool_name, perm in default_perms.items():
                categories[perm.tool_category].append(tool_name)
            
            # Trier les outils dans chaque catégorie
            for category in categories:
                categories[category].sort()
            
            return dict(categories)
            
        except Exception as e:
            logger.error(f"Erreur récupération outils par catégorie: {e}")
            return {}
    
    async def cleanup_cache(self):
        """Nettoie le cache des permissions expirées"""
        try:
            now = datetime.now()
            expired_users = []
            
            for user_id, cache in self.permission_cache.items():
                if (now - cache.last_updated).total_seconds() > cache.cache_ttl:
                    expired_users.append(user_id)
            
            for user_id in expired_users:
                del self.permission_cache[user_id]
            
            # Nettoyer le cache des permissions par défaut
            if (now - self.last_default_update).total_seconds() > self.default_cache_ttl:
                self.default_permissions_cache = None
                self.last_default_update = datetime.min
            
            if expired_users:
                logger.info(f"🧹 Cache permissions nettoyé: {len(expired_users)} utilisateurs")
            
        except Exception as e:
            logger.error(f"Erreur nettoyage cache permissions: {e}")

# Instance globale du gestionnaire
permissions_manager = PermissionsManager()

# Fonctions de nettoyage
async def cleanup_permissions_manager():
    """Nettoie les ressources du gestionnaire de permissions"""
    await permissions_manager.cleanup_cache()