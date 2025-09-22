#!/usr/bin/env python3
"""
Script pour vérifier l'état de la nouvelle base de données
"""

import sqlite3
import os

def check_fresh_db():
    """Vérifie l'état de la nouvelle base de données"""
    
    db_path = "bridge_data.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de données introuvable dans la racine")
        return False
    
    print(f"🔍 Vérification de la nouvelle base de données")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier les utilisateurs
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"👥 Nombre d'utilisateurs: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT username FROM users")
            users = cursor.fetchall()
            print(f"   Utilisateurs existants: {[u[0] for u in users]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔍 VÉRIFICATION DE LA NOUVELLE BASE DE DONNÉES")
    print("=" * 50)
    check_fresh_db()