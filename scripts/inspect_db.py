#!/usr/bin/env python3
"""
🔍 Script pour inspecter la structure de la base de données
"""

import sys
import os

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import db_manager
import asyncio

async def inspect_database():
    """Inspecte la structure de la base de données"""
    try:
        # Initialiser la base de données
        await db_manager.initialize()
        
        # Lister toutes les tables
        tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = await db_manager.fetch_all(tables_query)
        
        print("📊 Tables dans la base de données:")
        for table in tables:
            if isinstance(table, (tuple, list)):
                table_name = table[0]
            else:
                table_name = str(table)
            print(f"\n🗂️ Table: {table_name}")
            
            # Obtenir la structure de la table
            pragma_query = f"PRAGMA table_info({table_name});"
            columns = await db_manager.fetch_all(pragma_query)
            
            print("   Colonnes:")
            for col in columns:
                if isinstance(col, (tuple, list)) and len(col) >= 6:
                    col_id, name, data_type, not_null, default, pk = col
                    print(f"   - {name} ({data_type}) {'NOT NULL' if not_null else 'NULL'} {'PRIMARY KEY' if pk else ''}")
                else:
                    print(f"   - {col}")
        
        # Voir les utilisateurs existants
        print("\n👥 Utilisateurs existants:")
        users_query = "SELECT * FROM users LIMIT 5;"
        users = await db_manager.fetch_all(users_query)
        
        if users:
            for user in users:
                print(f"   User: {user}")
        else:
            print("   Aucun utilisateur trouvé")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'inspection: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db_manager.close()

async def main():
    """Fonction principale"""
    print("🔍 Inspection de la base de données")
    await inspect_database()

if __name__ == "__main__":
    asyncio.run(main())