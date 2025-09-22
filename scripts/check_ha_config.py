#!/usr/bin/env python3
"""
Script pour diagnostiquer la configuration Home Assistant dans la base de données
"""

import sqlite3
import os
import json

def check_ha_config():
    """Vérifie la configuration Home Assistant en base"""
    
    # Chercher la base de données
    db_paths = ["bridge_data.db", "src/bridge_data.db"]
    db_path = None
    
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Base de données introuvable")
        return False
    
    print(f"🔍 Vérification de la config HA dans: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lister toutes les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📋 Tables disponibles: {tables}")
        
        # Vérifier les configurations HA
        if 'ha_configs' in tables:
            cursor.execute("SELECT * FROM ha_configs")
            ha_configs = cursor.fetchall()
            
            print(f"\n🏠 Configurations Home Assistant ({len(ha_configs)}):")
            for config in ha_configs:
                print(f"   ID: {config[0]}")
                print(f"   User ID: {config[1]}")
                print(f"   Name: {config[2]}")
                print(f"   URL: {config[3]}")
                print(f"   Token: {config[4][:20]}...")
                print(f"   Created: {config[5]}")
                print("   ---")
        
        # Vérifier les utilisateurs pour le mapping
        if 'users' in tables:
            cursor.execute("SELECT id, username FROM users")
            users = cursor.fetchall()
            
            print(f"\n👥 Utilisateurs ({len(users)}):")
            for user in users:
                print(f"   ID {user[0]}: {user[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNOSTIC CONFIGURATION HOME ASSISTANT")
    print("=" * 50)
    check_ha_config()