#!/usr/bin/env python3
"""
Script pour nettoyer spécifiquement l'utilisateur beroute dans la nouvelle base
"""

import sqlite3
import os
import requests
from datetime import datetime

def clean_beroute_fresh():
    """Nettoie l'utilisateur beroute dans la nouvelle base"""
    
    db_path = "bridge_data.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de données introuvable")
        return False
    
    print("🧹 Nettoyage de l'utilisateur beroute dans la nouvelle base...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Supprimer complètement beroute
        cursor.execute("SELECT id FROM users WHERE username = 'beroute'")
        user_result = cursor.fetchone()
        
        if user_result:
            user_id = user_result[0]
            print(f"   Suppression de l'utilisateur ID: {user_id}")
            
            # Supprimer toutes les données liées
            cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM user_tool_permissions WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            
            conn.commit()
            print("✅ Utilisateur beroute supprimé de la base")
        else:
            print("⚠️ Utilisateur beroute introuvable")
        
        conn.close()
        
        # Maintenant créer via l'API
        print("\n👤 Création via l'API...")
        
        user_data = {
            "username": "beroute",
            "password": "Anna97480",
            "email": "beroute@example.com",
            "full_name": "User Beroute"
        }
        
        response = requests.post(
            "http://localhost:8080/auth/register",
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Utilisateur beroute créé avec succès!")
            
            # Test de connexion immédiat
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
                print(f"❌ Test de connexion échoué: {auth_response.status_code}")
                print(f"   Réponse: {auth_response.text}")
                return False
        else:
            print(f"❌ Erreur création: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🧹 NETTOYAGE COMPLET DE BEROUTE")
    print("=" * 35)
    
    success = clean_beroute_fresh()
    
    if success:
        print("\n🎉 BEROUTE PRÊT POUR L'AUTOMATISATION!")
    else:
        print("\n❌ Problème persistant")