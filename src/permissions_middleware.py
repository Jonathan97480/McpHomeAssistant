"""
Middleware de validation des permissions pour les outils MCP.
Valide les permissions granulaires avant l'exécution d'outils MCP.
"""

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, List
import logging
import json
from datetime import datetime

from permissions_manager import PermissionsManager, PermissionType
from auth_manager import auth_manager

logger = logging.getLogger(__name__)

async def get_current_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Obtient les données utilisateur depuis un token JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        Dict avec user_id, username, role ou None si invalide
    """
    try:
        token_data = auth_manager.verify_token(token)
        if not token_data:
            return None
            
        user = await auth_manager.get_user_by_id(token_data.user_id)
        if not user:
            return None
            
        return {
            'user_id': user.id,
            'username': user.username,
            'role': user.role.value,
            'email': user.email,
            'full_name': user.full_name
        }
        
    except Exception as e:
        logger.error(f"Erreur décodage token: {e}")
        return None

class PermissionsMiddleware:
    """Middleware pour la validation des permissions MCP."""
    
    def __init__(self):
        self.permissions_manager = PermissionsManager()
        self.security = HTTPBearer(auto_error=False)
        
    async def validate_mcp_permission(
        self, 
        request: Request,
        tool_name: str,
        permission_type: PermissionType,
        credentials: Optional[HTTPAuthorizationCredentials] = None
    ) -> Dict[str, Any]:
        """
        Valide les permissions pour un outil MCP spécifique.
        
        Args:
            request: Requête FastAPI
            tool_name: Nom de l'outil MCP
            permission_type: Type de permission (READ/WRITE/EXECUTE)
            credentials: Credentials d'autorisation
            
        Returns:
            Dict contenant user_id et les informations de validation
            
        Raises:
            HTTPException: Si permission refusée
        """
        try:
            # Extraire le token
            if not credentials:
                credentials = await self.security(request)
                
            if not credentials:
                logger.warning(f"Accès refusé - pas de token pour outil {tool_name}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token d'autorisation requis"
                )
            
            # Obtenir l'utilisateur depuis le token
            user_data = await get_current_user_from_token(credentials.credentials)
            if not user_data:
                logger.warning(f"Token invalide pour outil {tool_name}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide"
                )
            
            user_id = user_data.get('user_id')
            if not user_id:
                logger.error(f"User ID manquant dans token pour outil {tool_name}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID invalide"
                )
            
            # Vérifier les permissions
            has_permission = await self.permissions_manager.check_permission(
                user_id=user_id,
                tool_name=tool_name,
                permission_type=permission_type
            )
            
            if not has_permission:
                logger.warning(
                    f"Permission refusée - User {user_id}, outil {tool_name}, "
                    f"type {permission_type.value}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission {permission_type.value} refusée pour l'outil {tool_name}"
                )
            
            logger.info(
                f"Permission accordée - User {user_id}, outil {tool_name}, "
                f"type {permission_type.value}"
            )
            
            return {
                'user_id': user_id,
                'username': user_data.get('username'),
                'tool_name': tool_name,
                'permission_type': permission_type.value,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur validation permission: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur interne de validation des permissions"
            )

    async def validate_bulk_permissions(
        self,
        request: Request,
        tool_permissions: List[Dict[str, str]],
        credentials: Optional[HTTPAuthorizationCredentials] = None
    ) -> Dict[str, Any]:
        """
        Valide plusieurs permissions en une seule fois.
        
        Args:
            request: Requête FastAPI
            tool_permissions: Liste de dict avec tool_name et permission_type
            credentials: Credentials d'autorisation
            
        Returns:
            Dict avec user_id et résultats de validation
            
        Raises:
            HTTPException: Si au moins une permission est refusée
        """
        try:
            # Extraire le token
            if not credentials:
                credentials = await self.security(request)
                
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token d'autorisation requis"
                )
            
            # Obtenir l'utilisateur
            user_data = await get_current_user_from_token(credentials.credentials)
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide"
                )
            
            user_id = user_data.get('user_id')
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User ID invalide"
                )
            
            # Préparer les vérifications
            check_list = []
            for tool_perm in tool_permissions:
                tool_name = tool_perm.get('tool_name')
                perm_type_str = tool_perm.get('permission_type', 'READ')
                
                if not tool_name:
                    continue
                    
                try:
                    permission_type = PermissionType(perm_type_str.upper())
                    check_list.append((tool_name, permission_type))
                except ValueError:
                    logger.warning(f"Type de permission invalide: {perm_type_str}")
                    continue
            
            # Vérifier toutes les permissions
            results = []
            denied_permissions = []
            
            for tool_name, permission_type in check_list:
                has_permission = await self.permissions_manager.check_permission(
                    user_id=user_id,
                    tool_name=tool_name,
                    permission_type=permission_type
                )
                
                result = {
                    'tool_name': tool_name,
                    'permission_type': permission_type.value,
                    'granted': has_permission
                }
                results.append(result)
                
                if not has_permission:
                    denied_permissions.append(f"{tool_name}:{permission_type.value}")
            
            # Si des permissions sont refusées, lever une exception
            if denied_permissions:
                logger.warning(
                    f"Permissions refusées pour User {user_id}: {', '.join(denied_permissions)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissions refusées: {', '.join(denied_permissions)}"
                )
            
            logger.info(f"Toutes les permissions accordées pour User {user_id}")
            
            return {
                'user_id': user_id,
                'username': user_data.get('username'),
                'results': results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur validation permissions bulk: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur interne de validation des permissions"
            )

    async def log_permission_usage(
        self, 
        user_id: int, 
        tool_name: str, 
        permission_type: PermissionType,
        success: bool = True,
        details: Optional[str] = None
    ):
        """
        Log l'utilisation des permissions pour audit.
        
        Args:
            user_id: ID de l'utilisateur
            tool_name: Nom de l'outil MCP
            permission_type: Type de permission
            success: Si l'opération a réussi
            details: Détails additionnels
        """
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'tool_name': tool_name,
                'permission_type': permission_type.value,
                'success': success,
                'details': details
            }
            
            logger.info(f"Permission usage: {json.dumps(log_entry)}")
            
        except Exception as e:
            logger.error(f"Erreur lors du log des permissions: {e}")

    async def get_user_permissions_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Obtient un résumé des permissions d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict avec résumé des permissions
        """
        try:
            # Obtenir toutes les permissions de l'utilisateur
            user_permissions = await self.permissions_manager.get_user_permissions(user_id)
            
            # Organiser par outil
            tools_summary = {}
            for perm in user_permissions:
                tool_name = perm.tool_name
                if tool_name not in tools_summary:
                    tools_summary[tool_name] = {
                        'read': False,
                        'write': False,
                        'execute': False
                    }
                
                if perm.can_read:
                    tools_summary[tool_name]['read'] = True
                if perm.can_write:
                    tools_summary[tool_name]['write'] = True
                if perm.can_execute:
                    tools_summary[tool_name]['execute'] = True
            
            return {
                'user_id': user_id,
                'total_tools': len(tools_summary),
                'tools': tools_summary,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur obtention résumé permissions: {e}")
            return {
                'user_id': user_id,
                'total_tools': 0,
                'tools': {},
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

# Instance globale du middleware
permissions_middleware = PermissionsMiddleware()