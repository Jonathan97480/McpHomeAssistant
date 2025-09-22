#!/usr/bin/env python3
"""
Script pour inspecter la structure de la base de données
"""

import sqlite3
import os

def inspect_database():
    """Inspecte la structure de la base de données"""
    
    # Chemins des bases de données possibles
    db_paths = [
        "bridge_data.db",
        "src/bridge_data.db", 
        "../bridge_data.db"
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Base de données introuvable")
        return
    
    print(f"📊 Inspection de la base de données: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lister toutes les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📋 Tables disponibles:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Examiner la structure de la table users
        if ('users',) in tables:
            print(f"\n📊 Structure de la table 'users':")
            cursor.execute("PRAGMA table_info(users);")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"   - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'} {'PK' if col[5] else ''}")
            
            # Afficher quelques données utilisateur
            print(f"\n👥 Utilisateurs existants:")
            cursor.execute("SELECT * FROM users LIMIT 5;")
            users = cursor.fetchall()
            
            if users:
                # Afficher l'en-tête
                column_names = [desc[1] for desc in columns]
                print(f"   {' | '.join(column_names)}")
                print(f"   {'-' * (len(' | '.join(column_names)))}")
                
                for user in users:
                    print(f"   {' | '.join(str(x) if x is not None else 'NULL' for x in user)}")
            else:
                print("   Aucun utilisateur trouvé")
        
        # Examiner aussi la table auth_sessions si elle existe
        if ('auth_sessions',) in tables:
            print(f"\n🔐 Sessions d'authentification:")
            cursor.execute("SELECT * FROM auth_sessions WHERE username = 'beroute' LIMIT 3;")
            sessions = cursor.fetchall()
            
            if sessions:
                for session in sessions:
                    print(f"   {session}")
            else:
                print("   Aucune session pour beroute")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🔍 INSPECTION DE LA BASE DE DONNÉES")
    print("=" * 40)
    inspect_database()