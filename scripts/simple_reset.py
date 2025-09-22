#!/usr/bin/env python3
"""
Script pour réinitialiser simplement l'utilisateur beroute
"""

import sqlite3
import os
from datetime import datetime

def simple_reset_beroute():
    """Réinitialise simplement l'utilisateur beroute"""
    
    db_path = "bridge_data.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de données introuvable")
        return False
    
    print(f"📊 Réinitialisation de l'utilisateur beroute")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Réinitialiser l'utilisateur beroute
        cursor.execute("""
            UPDATE users 
            SET failed_login_attempts = 0, 
                locked_until = NULL,
                last_login = NULL,
                is_active = 1,
                updated_at = ?
            WHERE username = 'beroute'
        """, (datetime.now().isoformat(),))
        
        user_updated = cursor.rowcount
        
        # Nettoyer les sessions utilisateur
        cursor.execute("DELETE FROM user_sessions WHERE user_id = (SELECT id FROM users WHERE username = 'beroute')")
        sessions_deleted = cursor.rowcount
        
        conn.commit()
        
        print(f"✅ Utilisateur beroute réinitialisé: {user_updated} ligne(s)")
        print(f"🗑️ Sessions nettoyées: {sessions_deleted}")
        
        # Vérifier le statut final
        cursor.execute("""
            SELECT username, failed_login_attempts, locked_until, is_active
            FROM users 
            WHERE username = 'beroute'
        """)
        
        user = cursor.fetchone()
        if user:
            print(f"\n📊 Statut de beroute:")
            print(f"   Username: {user[0]}")
            print(f"   Failed attempts: {user[1]}")
            print(f"   Locked until: {user[2] or 'Non verrouillé'}")
            print(f"   Is active: {user[3]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔄 RÉINITIALISATION DE BEROUTE")
    print("=" * 35)
    
    success = simple_reset_beroute()
    
    if success:
        print("\n✅ Prêt pour une nouvelle connexion!")
    else:
        print("\n❌ Échec")