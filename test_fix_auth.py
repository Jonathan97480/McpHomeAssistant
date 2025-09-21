#!/usr/bin/env python3
"""
Test rapide des corrections d'authentification
"""

import asyncio
import aiohttp
import time

PI_BASE_URL = "http://192.168.1.22:8080"

async def test_fixes():
    """Test des corrections d'authentification"""
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        
        print("🔧 Test des corrections d'authentification\n")
        
        # 1. Test d'accès non autorisé (doit retourner 401 maintenant)
        print("🔒 Test d'accès non autorisé...")
        try:
            async with session.get(f"{PI_BASE_URL}/auth/me") as resp:
                print(f"Status: {resp.status}")
                if resp.status == 401:
                    print("✅ CORRECTION RÉUSSIE: Code 401 correct")
                else:
                    print(f"❌ Code incorrect: {resp.status} (attendu: 401)")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # 2. Test d'inscription avec email unique
        print("\n📝 Test d'inscription avec email unique...")
        timestamp = int(time.time())
        unique_email = f"test_{timestamp}@example.com"
        unique_username = f"testuser_{timestamp}"
        
        registration_data = {
            "username": unique_username,
            "email": unique_email,
            "full_name": "Test User Fix",
            "password": "TestPassword123!"  # Mot de passe avec majuscule et caractère spécial
        }
        
        try:
            async with session.post(
                f"{PI_BASE_URL}/auth/register",
                json=registration_data
            ) as resp:
                print(f"Status: {resp.status}")
                if resp.status == 200:
                    user_data = await resp.json()
                    print("✅ CORRECTION RÉUSSIE: Inscription avec email unique")
                    print(f"Utilisateur créé: {user_data}")
                    
                    # Test de connexion immédiate
                    print("\n🔑 Test de connexion...")
                    login_data = {
                        "username": unique_username,
                        "password": "TestPassword123!"
                    }
                    
                    async with session.post(
                        f"{PI_BASE_URL}/auth/login",
                        json=login_data
                    ) as login_resp:
                        if login_resp.status == 200:
                            token_data = await login_resp.json()
                            print("✅ Connexion réussie")
                            
                            # Test d'accès avec token
                            access_token = token_data.get("access_token")
                            if access_token:
                                print("\n🎫 Test d'accès avec token...")
                                headers = {"Authorization": f"Bearer {access_token}"}
                                async with session.get(f"{PI_BASE_URL}/auth/me", headers=headers) as me_resp:
                                    if me_resp.status == 200:
                                        user_info = await me_resp.json()
                                        print("✅ Accès autorisé réussi")
                                        return True
                                    else:
                                        print(f"❌ Accès autorisé échoué: {me_resp.status}")
                        else:
                            print(f"❌ Connexion échouée: {login_resp.status}")
                else:
                    error_text = await resp.text()
                    print(f"❌ Inscription échouée: {resp.status}")
                    print(f"Erreur: {error_text}")
        except Exception as e:
            print(f"❌ Erreur d'inscription: {e}")
        
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fixes())
    if success:
        print("\n🎉 TOUTES LES CORRECTIONS FONCTIONNENT!")
    else:
        print("\n⚠️  Il reste des problèmes à corriger.")