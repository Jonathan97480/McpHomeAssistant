#!/usr/bin/env python3
"""
Script pour créer un nouvel utilisateur temporaire de test
"""

import requests
import json

def create_test_user():
    """Crée un utilisateur de test pour contourner le problème de beroute"""
    
    print("👤 Création d'un utilisateur de test...")
    
    username = "test_user"
    password = "Anna97480"
    
    user_data = {
        "username": username,
        "password": password,
        "email": f"{username}@example.com",
        "full_name": f"Test User"
    }
    
    try:
        # Créer l'utilisateur
        response = requests.post(
            "http://localhost:8080/auth/register",
            json=user_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Utilisateur {username} créé avec succès")
            
            # Tester immédiatement la connexion
            login_data = {
                "username": username,
                "password": password
            }
            
            auth_response = requests.post(
                "http://localhost:8080/auth/login",
                json=login_data,
                timeout=10
            )
            
            if auth_response.status_code == 200:
                result = auth_response.json()
                print(f"✅ Connexion réussie!")
                print(f"   Token: {result.get('access_token', 'N/A')[:50]}...")
                print(f"   User ID: {result.get('user_id')}")
                return username, password, result.get('access_token')
            else:
                print(f"❌ Erreur de connexion: {auth_response.status_code}")
                print(f"   Réponse: {auth_response.text}")
                return None, None, None
        else:
            print(f"❌ Erreur création: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None, None, None
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None, None, None

if __name__ == "__main__":
    print("🧪 CRÉATION D'UN UTILISATEUR DE TEST")
    print("=" * 40)
    
    username, password, token = create_test_user()
    
    if username:
        print(f"\n✅ Utilisateur de test prêt:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print("Vous pouvez maintenant utiliser cet utilisateur dans le script d'automatisation.")
    else:
        print("\n❌ Échec de la création de l'utilisateur de test")