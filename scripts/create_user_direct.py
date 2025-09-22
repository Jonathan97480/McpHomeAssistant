#!/usr/bin/env python3
"""
👤 Script pour créer directement l'utilisateur beroute dans la base de données
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import db_manager
from auth_manager import hash_password
import asyncio

async def create_user_direct(username, password, email, full_name):
    """Crée un utilisateur directement dans la base de données"""
    try:
        # Initialiser la base de données
        await db_manager.initialize()
        
        # Hasher le mot de passe
        password_hash = hash_password(password)
        
        # Insérer l'utilisateur
        query = """
        INSERT INTO users (username, email, password_hash, full_name, created_at)
        VALUES (?, ?, ?, ?, ?)
        """
        
        from datetime import datetime
        result = await db_manager.execute(query, (
            username,
            email,
            password_hash,
            full_name,
            datetime.now().isoformat()
        ))
        
        if result:
            print(f"✅ Utilisateur créé avec succès: {username}")
            
            # Récupérer l'ID de l'utilisateur créé
            user_query = "SELECT id, username, email FROM users WHERE username = ?"
            user_result = await db_manager.fetch_one(user_query, (username,))
            
            if user_result:
                print(f"   ID: {user_result[0]}")
                print(f"   Username: {user_result[1]}")
                print(f"   Email: {user_result[2]}")
            
            return True
        else:
            print(f"❌ Erreur lors de la création de l'utilisateur")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await db_manager.close()

async def main():
    """Fonction principale"""
    username = "beroute"
    password = "Anna97480"
    email = "beroute@example.com"
    full_name = "Beroute User"
    
    print(f"👤 Création de l'utilisateur: {username}")
    success = await create_user_direct(username, password, email, full_name)
    
    if success:
        print(f"🎉 Utilisateur créé avec succès!")
        return 0
    else:
        print(f"💥 Échec de la création")
        return 1

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(result)