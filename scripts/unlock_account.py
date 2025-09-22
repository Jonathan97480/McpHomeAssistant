#!/usr/bin/env python3
"""
🔓 Script pour débloquer un compte utilisateur
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import db_manager
import asyncio

async def unlock_user_account(username):
    """Débloque un compte utilisateur"""
    try:
        # Initialiser la base de données
        await db_manager.initialize()
        
        # Réinitialiser les tentatives de connexion
        # Selon le code, il peut y avoir une table pour les tentatives
        tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = await db_manager.fetch_all(tables_query)
        
        print(f"🔓 Déblocage du compte: {username}")
        
        # Essayer de nettoyer les tables potentielles de tentatives de connexion
        possible_tables = ['login_attempts', 'user_sessions', 'failed_logins']
        
        for table_info in tables:
            table_name = table_info.get('name', '')
            if any(name in table_name.lower() for name in ['attempt', 'session', 'login']):
                print(f"   Nettoyage de la table: {table_name}")
                try:
                    delete_query = f"DELETE FROM {table_name} WHERE username = ? OR user_id = (SELECT id FROM users WHERE username = ?)"
                    await db_manager.execute(delete_query, (username, username))
                except Exception as e:
                    print(f"     ⚠️ Erreur sur {table_name}: {e}")
        
        # Vérifier si l'utilisateur existe
        user_query = "SELECT id, username FROM users WHERE username = ?"
        user = await db_manager.fetch_one(user_query, (username,))
        
        if user:
            print(f"✅ Compte débloqué pour: {username}")
            return True
        else:
            print(f"❌ Utilisateur non trouvé: {username}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du déblocage: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await db_manager.close()

async def main():
    """Fonction principale"""
    username = "beroute"
    
    print(f"🔓 Déblocage du compte utilisateur: {username}")
    success = await unlock_user_account(username)
    
    if success:
        print(f"🎉 Compte débloqué avec succès!")
        return 0
    else:
        print(f"💥 Échec du déblocage")
        return 1

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(result)