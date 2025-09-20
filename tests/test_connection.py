#!/usr/bin/env python3
"""
Script de test pour vérifier la connexion à Home Assistant
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le chemin du module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from homeassistant_mcp_server.server import HomeAssistantClient

async def test_connection():
    """Test de connexion basique à Home Assistant"""
    
    hass_url = os.getenv("HASS_URL", "http://192.168.1.22:8123")
    hass_token = os.getenv("HASS_TOKEN", "")
    
    print(f"🏠 Test de connexion à Home Assistant...")
    print(f"📍 URL: {hass_url}")
    print(f"🔑 Token configuré: {'✅ Oui' if hass_token else '❌ Non'}")
    print()
    
    # Test sans token d'abord
    print("🔓 Test sans authentification...")
    try:
        async with HomeAssistantClient(hass_url, "") as client:
            entities = await client.get_entities()
            print(f"✅ Connexion réussie ! Trouvé {len(entities)} entités")
    except Exception as e:
        print(f"❌ Échec attendu sans token: {e}")
    
    print()
    
    # Test avec token si disponible
    if hass_token:
        print("🔐 Test avec authentification...")
        try:
            async with HomeAssistantClient(hass_url, hass_token) as client:
                entities = await client.get_entities()
                print(f"🎉 Connexion authentifiée réussie !")
                print(f"📊 Trouvé {len(entities)} entités Home Assistant")
                
                # Afficher quelques exemples d'entités
                if entities:
                    print(f"\n📋 Exemples d'entités:")
                    for i, entity in enumerate(entities[:5]):
                        friendly_name = entity["attributes"].get("friendly_name", entity["entity_id"])
                        print(f"  {i+1}. {entity['entity_id']} ({friendly_name}) - {entity['state']}")
                    
                    if len(entities) > 5:
                        print(f"  ... et {len(entities) - 5} autres entités")
                        
        except Exception as e:
            print(f"❌ Erreur avec token: {e}")
            print("💡 Vérifiez que le token est correct et n'a pas expiré")
    else:
        print("📝 Pour tester avec authentification:")
        print("1. Allez sur http://192.168.1.22:8123")
        print("2. Connectez-vous")
        print("3. Profil > Tokens d'accès à long terme > Créer un token")
        print("4. Copiez le token dans le fichier .env")
        print("5. Relancez ce script")

if __name__ == "__main__":
    asyncio.run(test_connection())