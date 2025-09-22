#!/usr/bin/env python3
"""
🔍 Script pour vérifier les utilisateurs et débugger l'authentification
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import db_manager
from auth_manager import hash_password, verify_password
import asyncio

async def debug_authentication():
    """Debug le système d'authentification"""
    try:
        # Initialiser la base de données
        await db_manager.initialize()
        
        username = "beroute"
        password = "Anna97480"
        
        # Récupérer l'utilisateur
        query = "SELECT id, username, password_hash FROM users WHERE username = ?"
        user_result = await db_manager.fetch_one(query, (username,))
        
        if user_result:
            print(f"✅ Utilisateur trouvé dans la base:")
            print(f"   ID: {user_result.get('id', 'N/A')}")
            print(f"   Username: {user_result.get('username', 'N/A')}")
            
            stored_hash = user_result.get('password_hash', '')
            print(f"   Password hash length: {len(stored_hash)}")
            
            # Tester la vérification du mot de passe
            if verify_password(password, stored_hash):
                print("✅ Mot de passe vérifié avec succès!")
            else:
                print("❌ Vérification du mot de passe échouée")
                
                # Créer un nouveau hash et le tester
                new_hash = hash_password(password)
                print(f"   Nouveau hash créé: {len(new_hash)} chars")
                
                if verify_password(password, new_hash):
                    print("✅ Le nouveau hash fonctionne")
                    
                    # Mettre à jour le hash dans la base
                    update_query = "UPDATE users SET password_hash = ? WHERE username = ?"
                    await db_manager.execute(update_query, (new_hash, username))
                    print("✅ Hash mis à jour dans la base de données")
                else:
                    print("❌ Problème avec le système de hash")
        else:
            print(f"❌ Utilisateur '{username}' non trouvé dans la base")
            
            # Lister tous les utilisateurs
            all_users_query = "SELECT username FROM users"
            all_users = await db_manager.fetch_all(all_users_query)
            print(f"Utilisateurs existants:")
            for user in all_users:
                print(f"   - {user.get('username', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Erreur lors du debug: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.close()

async def main():
    """Fonction principale"""
    print("🔍 Debug de l'authentification")
    await debug_authentication()

if __name__ == "__main__":
    asyncio.run(main())