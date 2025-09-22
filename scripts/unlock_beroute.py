#!/usr/bin/env python3
"""
Script pour débloquer le compte beroute
"""

import sqlite3
import os
from datetime import datetime

def unlock_account():
    """Débloque le compte beroute"""
    
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
        return False
    
    print(f"📊 Utilisation de la base de données: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Réinitialiser les tentatives de connexion pour beroute
        cursor.execute("""
            UPDATE users 
            SET failed_attempts = 0, 
                locked_until = NULL,
                last_failed_attempt = NULL
            WHERE username = 'beroute'
        """)
        
        rows_affected = cursor.rowcount
        conn.commit()
        
        if rows_affected > 0:
            print("✅ Compte beroute débloqué avec succès")
            
            # Vérifier le statut actuel
            cursor.execute("""
                SELECT username, failed_attempts, locked_until, created_at
                FROM users 
                WHERE username = 'beroute'
            """)
            
            user = cursor.fetchone()
            if user:
                print(f"📊 Statut utilisateur:")
                print(f"   Username: {user[0]}")
                print(f"   Failed attempts: {user[1]}")
                print(f"   Locked until: {user[2] or 'Non verrouillé'}")
                print(f"   Created at: {user[3]}")
            
        else:
            print("⚠️ Aucun utilisateur 'beroute' trouvé")
            
        conn.close()
        return rows_affected > 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔓 DÉBLOCAGE DU COMPTE BEROUTE")
    print("=" * 40)
    
    success = unlock_account()
    
    if success:
        print("\n✅ Déblocage terminé avec succès!")
        print("Vous pouvez maintenant relancer le script d'automatisation.")
    else:
        print("\n❌ Échec du déblocage")