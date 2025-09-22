#!/usr/bin/env python3
"""
Script pour vérifier en détail l'état de l'utilisateur beroute et forcer un déblocage
"""

import sqlite3
import os
import requests
import time
from datetime import datetime, timezone

def check_user_status():
    """Vérifie en détail l'état de l'utilisateur beroute"""
    
    db_path = "bridge_data.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de données introuvable")
        return False
    
    print(f"🔍 Vérification détaillée de l'utilisateur beroute")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier l'utilisateur beroute
        cursor.execute("""
            SELECT id, username, failed_login_attempts, locked_until, is_active, created_at, updated_at
            FROM users 
            WHERE username = 'beroute'
        """)
        
        user = cursor.fetchone()
        if not user:
            print("❌ Utilisateur beroute introuvable")
            return False
        
        user_id, username, failed_attempts, locked_until, is_active, created_at, updated_at = user
        
        print(f"📊 État actuel de l'utilisateur:")
        print(f"   ID: {user_id}")
        print(f"   Username: {username}")
        print(f"   Failed attempts: {failed_attempts}")
        print(f"   Locked until: {locked_until}")
        print(f"   Is active: {is_active}")
        print(f"   Created: {created_at}")
        print(f"   Updated: {updated_at}")
        
        # Vérifier si la date de verrouillage est dans le futur
        if locked_until:
            try:
                lock_time = datetime.fromisoformat(locked_until.replace('Z', '+00:00'))
                current_time = datetime.now(timezone.utc)
                print(f"   Current time: {current_time}")
                print(f"   Lock time: {lock_time}")
                
                if lock_time > current_time:
                    print(f"⚠️ UTILISATEUR ENCORE VERROUILLÉ jusqu'à {lock_time}")
                    
                    # Forcer le déblocage
                    cursor.execute("""
                        UPDATE users 
                        SET failed_login_attempts = 0, 
                            locked_until = NULL,
                            updated_at = ?
                        WHERE id = ?
                    """, (datetime.now().isoformat(), user_id))
                    
                    conn.commit()
                    print("🔓 DÉBLOCAGE FORCÉ APPLIQUÉ")
                else:
                    print("✅ Le verrouillage a expiré")
            except Exception as e:
                print(f"❌ Erreur de parsing de date: {e}")
                # En cas d'erreur, forcer le déblocage
                cursor.execute("""
                    UPDATE users 
                    SET failed_login_attempts = 0, 
                        locked_until = NULL,
                        updated_at = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), user_id))
                
                conn.commit()
                print("🔓 DÉBLOCAGE FORCÉ APPLIQUÉ (erreur de date)")
        
        # Vérifier les sessions actives
        cursor.execute("""
            SELECT COUNT(*) FROM user_sessions WHERE user_id = ?
        """, (user_id,))
        
        session_count = cursor.fetchone()[0]
        print(f"   Sessions actives: {session_count}")
        
        # Si il y a des sessions, les supprimer
        if session_count > 0:
            cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
            conn.commit()
            print("🗑️ Sessions supprimées")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_server_auth():
    """Teste l'authentification directement avec le serveur"""
    
    print(f"\n🔗 Test de connexion au serveur...")
    
    try:
        # Tester la disponibilité du serveur
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Serveur indisponible: {response.status_code}")
            return False
        
        print("✅ Serveur accessible")
        
        # Tester l'authentification
        login_data = {
            "username": "beroute",
            "password": "Anna97480"
        }
        
        auth_response = requests.post(
            "http://localhost:8080/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"🔐 Réponse auth: {auth_response.status_code}")
        print(f"   Contenu: {auth_response.text}")
        
        return auth_response.status_code == 200
        
    except Exception as e:
        print(f"❌ Erreur de test serveur: {e}")
        return False

def main():
    print("🔍 DIAGNOSTIC COMPLET DE L'UTILISATEUR BEROUTE")
    print("=" * 55)
    
    # 1. Vérifier l'état de la base de données
    db_ok = check_user_status()
    
    if not db_ok:
        print("❌ Problème avec la base de données")
        return
    
    # 2. Tester l'authentification serveur
    auth_ok = test_server_auth()
    
    if auth_ok:
        print("\n✅ TOUT FONCTIONNE CORRECTEMENT!")
    else:
        print("\n⚠️ IL FAUT PEUT-ÊTRE REDÉMARRER LE SERVEUR")
        print("Le serveur peut avoir un cache en mémoire qu'il faut vider.")

if __name__ == "__main__":
    main()