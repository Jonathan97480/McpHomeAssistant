#!/usr/bin/env python3
"""
🔧 Script pour réinitialiser le mot de passe de l'utilisateur beroute
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import db_manager
from auth_manager import hash_password
import asyncio

async def reset_user_password(username, new_password):
    """Réinitialise le mot de passe d'un utilisateur"""
    try:
        # Initialiser la base de données
        await db_manager.initialize()
        
        # Hasher le nouveau mot de passe
        password_hash = hash_password(new_password)
        
        # Mettre à jour le mot de passe dans la base
        query = "UPDATE users SET password_hash = ? WHERE username = ?"
        result = await db_manager.execute(query, (password_hash, username))
        
        # Vérifier si l'utilisateur existe
        check_query = "SELECT username FROM users WHERE username = ?"
        user_exists = await db_manager.fetch_one(check_query, (username,))
        
        if user_exists:
            print(f"✅ Mot de passe réinitialisé pour l'utilisateur: {username}")
            return True
        else:
            print(f"❌ Utilisateur non trouvé: {username}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la réinitialisation: {e}")
        return False
    finally:
        await db_manager.close()

async def main():
    """Fonction principale"""
    username = "beroute"
    new_password = "Anna97480"
    
    print(f"🔧 Réinitialisation du mot de passe pour: {username}")
    success = await reset_user_password(username, new_password)
    
    if success:
        print(f"🎉 Mot de passe mis à jour avec succès!")
        return 0
    else:
        print(f"💥 Échec de la réinitialisation")
        return 1

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(result)