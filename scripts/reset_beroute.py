#!/usr/bin/env python3
"""
Script pour nettoyer les sessions et réinitialiser l'utilisateur beroute
"""

import sqlite3
import os
from datetime import datetime

def reset_user_beroute():
    """Remet à zéro complètement l'utilisateur beroute"""
    
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
    
    print(f"📊 Nettoyage de la base de données: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Nettoyer les sessions utilisateur pour beroute
        cursor.execute("DELETE FROM user_sessions WHERE user_id = (SELECT id FROM users WHERE username = 'beroute')")
        sessions_deleted = cursor.rowcount
        print(f"🗑️ {sessions_deleted} sessions supprimées")
        
        # 2. Réinitialiser complètement l'utilisateur beroute
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
        print(f"👤 Utilisateur beroute réinitialisé: {user_updated} ligne(s) modifiée(s)")
        
        # 3. Nettoyer les logs d'erreur liés à beroute
        cursor.execute("DELETE FROM logs WHERE message LIKE '%beroute%' AND level = 'ERROR'")
        logs_deleted = cursor.rowcount
        print(f"📝 {logs_deleted} logs d'erreur supprimés")
        
        # 4. Nettoyer les erreurs liées à l'authentification
        cursor.execute("DELETE FROM errors WHERE message LIKE '%authentication%' OR message LIKE '%login%'")
        errors_deleted = cursor.rowcount
        print(f"❌ {errors_deleted} erreurs d'authentification supprimées")
        
        conn.commit()
        
        # Vérifier le statut final
        cursor.execute("""
            SELECT username, failed_login_attempts, locked_until, is_active, last_login
            FROM users 
            WHERE username = 'beroute'
        """)
        
        user = cursor.fetchone()
        if user:
            print(f"\n✅ Statut final de l'utilisateur beroute:")
            print(f"   Username: {user[0]}")
            print(f"   Failed attempts: {user[1]}")
            print(f"   Locked until: {user[2] or 'Non verrouillé'}")
            print(f"   Is active: {user[3]}")
            print(f"   Last login: {user[4] or 'Jamais connecté'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔄 RÉINITIALISATION COMPLÈTE DE L'UTILISATEUR BEROUTE")
    print("=" * 55)
    
    success = reset_user_beroute()
    
    if success:
        print("\n✅ Réinitialisation terminée avec succès!")
        print("L'utilisateur beroute est maintenant prêt pour une nouvelle connexion.")
    else:
        print("\n❌ Échec de la réinitialisation")