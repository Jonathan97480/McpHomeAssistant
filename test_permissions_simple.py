#!/usr/bin/env python3
"""
🔐 Test simple du système de permissions
Test basique des fonctionnalités de permissions sans serveur externe
"""

import asyncio
import sys
import os

# Ajouter le chemin pour importer nos modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from permissions_manager import PermissionsManager, PermissionType
from database import setup_database, db_manager
from auth_manager import auth_manager, UserCreate

async def test_permissions_system():
    """Test des fonctionnalités de base du système de permissions"""
    print("🧪 Test du système de permissions MCP\n")
    
    try:
        # 1. Initialiser la base de données
        print("📂 Initialisation de la base de données...")
        await setup_database()
        print("✅ Base de données initialisée")
        
        # 2. Créer un utilisateur de test
        print("\n👤 Création d'un utilisateur de test...")
        user_data = UserCreate(
            username="testuser",
            email="test@example.com", 
            full_name="Test User",
            password="TestPass123!"
        )
        
        user = await auth_manager.create_user(user_data)
        if user:
            user_id = user.id
            print(f"✅ Utilisateur créé: {user.username} (ID: {user_id})")
        else:
            print("❌ Échec création utilisateur")
            return False
        
        # 3. Initialiser le gestionnaire de permissions
        print("\n🔐 Initialisation du gestionnaire de permissions...")
        permissions_manager = PermissionsManager()
        print("✅ Gestionnaire de permissions initialisé")
        
        # 4. Test permissions par défaut (aucune permission)
        print("\n🔍 Test: Permission par défaut (refusée)...")
        has_read = await permissions_manager.check_permission(
            user_id=user_id,
            tool_name="homeassistant.get_state",
            permission_type=PermissionType.READ
        )
        if not has_read:
            print("✅ Permission correctement refusée par défaut")
        else:
            print("❌ Permission accordée à tort")
            return False
        
        # 5. Définir une permission par défaut
        print("\n🔧 Test: Définition d'une permission par défaut...")
        success = await permissions_manager.set_default_permission(
            tool_name="homeassistant.get_state",
            can_read=True,
            can_write=False,
            can_execute=False
        )
        if success:
            print("✅ Permission par défaut définie")
        else:
            print("❌ Échec définition permission par défaut")
            return False
        
        # 6. Vérifier héritage des permissions par défaut
        print("\n📋 Test: Héritage des permissions par défaut...")
        has_read = await permissions_manager.has_permission(
            user_id=user_id,
            tool_name="homeassistant.get_state",
            permission_type=PermissionType.READ
        )
        if has_read:
            print("✅ Héritage des permissions par défaut fonctionnel")
        else:
            print("❌ Héritage des permissions par défaut défaillant")
            return False
        
        # 7. Définir une permission spécifique utilisateur
        print("\n👤 Test: Permission spécifique utilisateur...")
        success = await permissions_manager.set_user_permission(
            user_id=user_id,
            tool_name="homeassistant.call_service",
            can_read=False,
            can_write=True,
            can_execute=True
        )
        if success:
            print("✅ Permission utilisateur définie")
        else:
            print("❌ Échec définition permission utilisateur")
            return False
        
        # 8. Vérifier permission utilisateur WRITE
        print("\n✍️ Test: Validation permission WRITE...")
        has_write = await permissions_manager.has_permission(
            user_id=user_id,
            tool_name="homeassistant.call_service",
            permission_type=PermissionType.WRITE
        )
        if has_write:
            print("✅ Permission WRITE accordée")
        else:
            print("❌ Permission WRITE refusée")
            return False
        
        # 9. Vérifier permission utilisateur READ refusée
        print("\n👁️ Test: Validation permission READ refusée...")
        has_read = await permissions_manager.has_permission(
            user_id=user_id,
            tool_name="homeassistant.call_service",
            permission_type=PermissionType.READ
        )
        if not has_read:
            print("✅ Permission READ correctement refusée")
        else:
            print("❌ Permission READ accordée à tort")
            return False
        
        # 10. Test cache des permissions
        print("\n💾 Test: Système de cache...")
        import time
        start_time = time.time()
        
        # Première requête (pas en cache)
        await permissions_manager.has_permission(
            user_id=user_id,
            tool_name="homeassistant.get_state",
            permission_type=PermissionType.READ
        )
        first_time = time.time() - start_time
        
        start_time = time.time()
        # Deuxième requête (en cache)
        await permissions_manager.has_permission(
            user_id=user_id,
            tool_name="homeassistant.get_state",
            permission_type=PermissionType.READ
        )
        second_time = time.time() - start_time
        
        if second_time < first_time:
            print("✅ Système de cache fonctionnel")
        else:
            print("⚠️ Cache possiblement non actif (peut être normal)")
        
        # 11. Test résumé des permissions
        print("\n📊 Test: Résumé des permissions...")
        user_permissions = await permissions_manager.get_user_permissions(user_id)
        if len(user_permissions) > 0:
            print(f"✅ Résumé obtenu: {len(user_permissions)} permissions")
            for perm in user_permissions:
                print(f"   🔧 {perm.tool_name}: R={perm.can_read}, W={perm.can_write}, E={perm.can_execute}")
        else:
            print("❌ Aucune permission trouvée")
            return False
        
        print("\n🎉 Tous les tests de permissions ont réussi!")
        return True
        
    except Exception as e:
        print(f"\n💥 Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Fonction principale"""
    success = await test_permissions_system()
    
    if success:
        print("\n✅ Système de permissions validé!")
        return 0
    else:
        print("\n❌ Échec des tests de permissions")
        return 1

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(result)