#!/usr/bin/env python3
"""
Script pour supprimer et recréer l'utilisateur beroute
"""

import sqlite3
import os
import requests
from datetime import datetime

def delete_and_recreate_beroute():
    """Supprime complètement beroute et le recrée"""
    
    db_path = "bridge_data.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de données introuvable")
        return False
    
    print("🗑️ Suppression complète de l'utilisateur beroute...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer l'ID de beroute avant suppression
        cursor.execute("SELECT id FROM users WHERE username = 'beroute'")
        user_result = cursor.fetchone()
        
        if user_result:
            user_id = user_result[0]
            print(f"   ID utilisateur beroute: {user_id}")
            
            # Supprimer toutes les données liées à beroute
            cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
            sessions_deleted = cursor.rowcount
            print(f"   Sessions supprimées: {sessions_deleted}")
            
            cursor.execute("DELETE FROM user_tool_permissions WHERE user_id = ?", (user_id,))
            permissions_deleted = cursor.rowcount
            print(f"   Permissions supprimées: {permissions_deleted}")
            
            # Supprimer l'utilisateur lui-même
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            user_deleted = cursor.rowcount
            print(f"   Utilisateur supprimé: {user_deleted}")
            
            conn.commit()
            print("✅ Suppression terminée")
        else:
            print("⚠️ Utilisateur beroute introuvable")
        
        conn.close()
        
        # Maintenant recréer l'utilisateur via l'API
        print("\n👤 Recréation de l'utilisateur beroute...")
        
        user_data = {
            "username": "beroute",
            "password": "Anna97480",
            "email": "beroute@example.com",
            "full_name": "User beroute"
        }
        
        response = requests.post(
            "http://localhost:8080/auth/register",
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Utilisateur beroute recréé avec succès")
            print(f"   ID: {result.get('user_id')}")
            print(f"   Username: {result.get('username')}")
            
            # Tester immédiatement la connexion
            login_data = {
                "username": "beroute",
                "password": "Anna97480"
            }
            
            auth_response = requests.post(
                "http://localhost:8080/auth/login",
                json=login_data,
                timeout=10
            )
            
            if auth_response.status_code == 200:
                print("✅ Test de connexion réussi!")
                return True
            else:
                print(f"❌ Échec du test de connexion: {auth_response.status_code}")
                print(f"   Réponse: {auth_response.text}")
                return False
        else:
            print(f"❌ Erreur recréation: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔄 SUPPRESSION ET RECRÉATION DE BEROUTE")
    print("=" * 45)
    
    success = delete_and_recreate_beroute()
    
    if success:
        print("\n🎉 BEROUTE EST MAINTENANT OPÉRATIONNEL!")
        print("Vous pouvez lancer le script d'automatisation.")
    else:
        print("\n❌ Échec de la recréation")