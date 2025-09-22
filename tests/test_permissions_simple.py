#!/usr/bin/env python3
"""
[CLOSED_LOCK_KEY] Test simple du système de permissions
Test basique des fonctionnalités de permissions sans serveur externe
"""

import asyncio
import sys
import os
import time
import uuid

# Ajouter le chemin pour importer nos modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from permissions_manager import PermissionsManager, PermissionType, UserPermissionUpdate
from database import setup_database, db_manager
from auth_manager import auth_manager, UserCreate

async def test_permissions_system():
    """Test des fonctionnalités de base du système de permissions"""
    print("[TEST] Test du système de permissions MCP\n")
    
    try:
        # 1. Initialiser la base de données
        print("[FILES] Initialisation de la base de données...")
        await setup_database()
        print("[OK] Base de données initialisée")
        
        # 1.5. Nettoyer les permissions par défaut existantes pour ce test
        print("\n[CLEAN] Nettoyage des permissions par défaut existantes...")
        await db_manager.execute("DELETE FROM default_permissions WHERE tool_name = ?", ("homeassistant.get_state",))
        print("[OK] Permissions par défaut nettoyées")
        
        # 2. Créer un utilisateur de test avec données uniques
        import time
        timestamp = int(time.time())
        random_id = uuid.uuid4().hex[:8]
        
        print("\n[USER] Création d'un utilisateur de test...")
        user_data = UserCreate(
            username=f"testuser_{timestamp}_{random_id}",
            email=f"test_{timestamp}_{random_id}@example.com", 
            full_name="Test User",
            password="TestPass123!"
        )
        
        user = await auth_manager.create_user(user_data)
        if user:
            user_id = user.id
            print(f"[OK] Utilisateur créé: {user.username} (ID: {user_id})")
        else:
            print("[FAIL] Échec création utilisateur")
            return False
        
        # 3. Initialiser le gestionnaire de permissions
        print("\n[CLOSED_LOCK_KEY] Initialisation du gestionnaire de permissions...")
        permissions_manager = PermissionsManager()
        print("[OK] Gestionnaire de permissions initialisé")
        
        # 4. Test permissions par défaut (aucune permission)
        print("\n[SEARCH] Test: Permission par défaut (refusée)...")
        has_read = await permissions_manager.check_permission(
            user_id=user_id,
            tool_name="homeassistant.get_state",
            permission_type=PermissionType.READ
        )
        if not has_read:
            print("[OK] Permission correctement refusée par défaut")
        else:
            print("[FAIL] Permission accordée à tort")
            return False
        
        # 5. Définir une permission par défaut
        print("\n[TOOL] Test: Définition d'une permission par défaut...")
        success = await permissions_manager.set_default_permission(
            tool_name="homeassistant.get_state",
            can_read=True,
            can_write=False,
            can_execute=False
        )
        if success:
            print("[OK] Permission par défaut définie")
        else:
            print("[FAIL] Échec définition permission par défaut")
            return False
        
        # 6. Vérifier héritage des permissions par défaut
        print("\n[LIST] Test: Héritage des permissions par défaut...")
        has_read = await permissions_manager.check_permission(
            user_id=user_id,
            tool_name="homeassistant.get_state",
            permission_type=PermissionType.READ
        )
        if has_read:
            print("[OK] Héritage des permissions par défaut fonctionnel")
        else:
            print("[FAIL] Héritage des permissions par défaut défaillant")
            return False
        
        # 7. Définir une permission spécifique utilisateur
        print("\n[USER] Test: Permission spécifique utilisateur...")
        update = UserPermissionUpdate(
            can_read=False,
            can_write=True,
            is_enabled=True
        )
        success = await permissions_manager.update_user_permission(
            user_id=user_id,
            tool_name="homeassistant.call_service",
            updates=update
        )
        if success:
            print("[OK] Permission utilisateur définie")
        else:
            print("[FAIL] Échec définition permission utilisateur")
            return False
        
        # 8. Vérifier permission utilisateur WRITE
        print("\n[EMOJI] Test: Validation permission WRITE...")
        has_write = await permissions_manager.check_permission(
            user_id=user_id,
            tool_name="homeassistant.call_service",
            permission_type=PermissionType.WRITE
        )
        if has_write:
            print("[OK] Permission WRITE accordée")
        else:
            print("[FAIL] Permission WRITE refusée")
            return False
        
        # 9. Vérifier permission utilisateur READ refusée
        print("\n[EMOJI] Test: Validation permission READ refusée...")
        has_read = await permissions_manager.check_permission(
            user_id=user_id,
            tool_name="homeassistant.call_service",
            permission_type=PermissionType.READ
        )
        if not has_read:
            print("[OK] Permission READ correctement refusée")
        else:
            print("[FAIL] Permission READ accordée à tort")
            return False
        
        # 10. Test cache des permissions
        print("\n[EMOJI] Test: Système de cache...")
        import time
        start_time = time.time()
        
        # Première requête (pas en cache)
        await permissions_manager.check_permission(
            user_id=user_id,
            tool_name="homeassistant.get_state",
            permission_type=PermissionType.READ
        )
        first_time = time.time() - start_time
        
        start_time = time.time()
        # Deuxième requête (en cache)
        await permissions_manager.check_permission(
            user_id=user_id,
            tool_name="homeassistant.get_state",
            permission_type=PermissionType.READ
        )
        second_time = time.time() - start_time
        
        if second_time < first_time:
            print("[OK] Système de cache fonctionnel")
        else:
            print("[WARN] Cache possiblement non actif (peut être normal)")
        
        # 11. Test résumé des permissions
        print("\n[STATS] Test: Résumé des permissions...")
        user_permissions = await permissions_manager.get_user_permission_summary(user_id)
        if len(user_permissions) > 0:
            print(f"[OK] Résumé obtenu: {len(user_permissions)} permissions")
            for perm in user_permissions:
                print(f"   [TOOL] {perm.tool_name}: R={perm.can_read}, W={perm.can_write}, enabled={perm.is_enabled}")
        else:
            print("[FAIL] Aucune permission trouvée")
            return False
        
        print("\n[PARTY] Tous les tests de permissions ont réussi!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Fonction principale"""
    success = await test_permissions_system()
    
    if success:
        print("\n[OK] Système de permissions validé!")
        return 0
    else:
        print("\n[FAIL] Échec des tests de permissions")
        return 1

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(result)