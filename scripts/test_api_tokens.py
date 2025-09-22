#!/usr/bin/env python3
"""
🔑 Test du système de tokens API personnalisés pour LM Studio
"""

import asyncio
import aiohttp
import json
import sys
import os

async def test_api_tokens():
    """Test complet du système de tokens API"""
    
    print("🔑 Test du système de tokens API personnalisés")
    print("=" * 60)
    
    base_url = "http://localhost:8080"
    
    # 1. Connexion avec utilisateur beroute
    print("1️⃣ Connexion utilisateur beroute...")
    
    login_data = {
        "username": "beroute",
        "password": "Anna97480"
    }
    
    async with aiohttp.ClientSession() as session:
        # Login pour obtenir le JWT token
        async with session.post(f"{base_url}/auth/login", json=login_data) as resp:
            if resp.status != 200:
                print(f"❌ Erreur login: {resp.status}")
                text = await resp.text()
                print(f"   Réponse: {text}")
                return
            
            login_response = await resp.json()
            jwt_token = login_response["access_token"]
            print(f"✅ Login réussi, JWT token obtenu")
        
        # Headers avec JWT token
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        # 2. Générer un token API
        print("\n2️⃣ Génération d'un token API pour LM Studio...")
        
        token_request = {
            "token_name": "LM Studio Test",
            "expires_days": 365
        }
        
        async with session.post(f"{base_url}/api/tokens/generate", 
                              json=token_request, headers=headers) as resp:
            if resp.status != 200:
                print(f"❌ Erreur génération token: {resp.status}")
                text = await resp.text()
                print(f"   Réponse: {text}")
                return
            
            token_response = await resp.json()
            api_token = token_response["token"]
            token_id = token_response["token_id"]
            print(f"✅ Token API généré:")
            print(f"   Token: {api_token}")
            print(f"   ID: {token_id}")
            print(f"   Expire le: {token_response['expires_at']}")
        
        # 3. Tester l'authentification avec le token API
        print("\n3️⃣ Test d'authentification avec le token API...")
        
        api_headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "X-Session-ID": "api-test-session"
        }
        
        # Test du endpoint status avec token API
        async with session.get(f"{base_url}/auth/me", headers=api_headers) as resp:
            if resp.status != 200:
                print(f"❌ Erreur auth token API: {resp.status}")
                text = await resp.text()
                print(f"   Réponse: {text}")
                return
            
            user_response = await resp.json()
            print(f"✅ Authentification token API réussie:")
            print(f"   Utilisateur: {user_response['username']}")
            print(f"   Auth par API token: {user_response.get('api_token_auth', False)}")
        
        # 4. Tester un appel MCP avec le token API
        print("\n4️⃣ Test d'appel MCP avec token API...")
        
        mcp_request = {
            "method": "get_entities",
            "params": {"format": "json"}
        }
        
        async with session.post(f"{base_url}/mcp/tools/call", 
                              json=mcp_request, headers=api_headers) as resp:
            if resp.status != 200:
                print(f"❌ Erreur appel MCP: {resp.status}")
                text = await resp.text()
                print(f"   Réponse: {text}")
                return
            
            mcp_response = await resp.json()
            entities = mcp_response.get("result", {}).get("entities", [])
            print(f"✅ Appel MCP réussi avec token API:")
            print(f"   {len(entities)} entités récupérées")
            
            # Afficher quelques entités
            for i, entity in enumerate(entities[:3]):
                print(f"   - {entity.get('entity_id', 'N/A')}: {entity.get('state', 'N/A')}")
        
        # 5. Lister les tokens de l'utilisateur
        print("\n5️⃣ Liste des tokens API de l'utilisateur...")
        
        async with session.get(f"{base_url}/api/tokens", headers=api_headers) as resp:
            if resp.status != 200:
                print(f"❌ Erreur liste tokens: {resp.status}")
                text = await resp.text()
                print(f"   Réponse: {text}")
                return
            
            tokens_response = await resp.json()
            tokens = tokens_response.get("tokens", [])
            print(f"✅ {len(tokens)} token(s) trouvé(s):")
            for token in tokens:
                status = "Actif" if token["is_active"] else "Révoqué"
                print(f"   - {token['name']} (ID: {token['id']}) - {status}")
        
        # 6. Créer la configuration LM Studio mise à jour
        print("\n6️⃣ Création de la configuration LM Studio...")
        
        lm_config = {
            "mcpServers": {
                "homeassistant-bridge": {
                    "name": "Home Assistant MCP Bridge Server",
                    "command": "node",
                    "args": ["-e", "console.log('MCP Bridge Server')"],
                    "description": "Bridge HTTP vers Home Assistant via tokens API personnalisés",
                    "env": {
                        "BRIDGE_URL": "http://localhost:8080",
                        "HASS_URL": "http://raspberrypi:8123",
                        "API_TOKEN": api_token
                    },
                    "timeout": 30,
                    "autoStart": False
                }
            }
        }
        
        # Sauvegarder la configuration
        config_path = "configs/lm-studio-config-with-api-token.json"
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(lm_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuration LM Studio sauvegardée: {config_path}")
        print(f"   Utilisez ce token dans LM Studio: {api_token}")
        
        print("\n🎉 Test du système de tokens API terminé avec succès!")
        print("\n📋 Prochaines étapes:")
        print("   1. Utilisez le token API dans LM Studio au lieu du token HA")
        print("   2. Les vrais tokens HA restent sécurisés sur le serveur")
        print("   3. Chaque utilisateur peut avoir ses propres tokens personnalisés")
        
        return api_token

def main():
    """Point d'entrée principal"""
    try:
        return asyncio.run(test_api_tokens())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    token = main()
    if token:
        print(f"\n🔑 Token API généré: {token}")