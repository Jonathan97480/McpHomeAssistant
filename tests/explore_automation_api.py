#!/usr/bin/env python3
"""
Exploration des endpoints d'automatisation disponibles
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le chemin du module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from homeassistant_mcp_server.server import HomeAssistantClient

async def explore_automation_endpoints():
    """Explorer les endpoints d'automatisation disponibles"""
    
    hass_url = os.getenv("HASS_URL", "http://192.168.1.22:8123")
    hass_token = os.getenv("HASS_TOKEN", "")
    
    if not hass_token:
        print("❌ Token requis")
        return
    
    async with HomeAssistantClient(hass_url, hass_token) as client:
        print("🔍 Exploration des endpoints d'automatisation\n")
        
        # Test différents endpoints possibles
        endpoints_to_test = [
            "/api/config/automation/config",
            "/api/states?entity_id=automation",
            "/api/states",
            "/api/services/automation",
            "/api/services",
            "/api/config",
        ]
        
        for endpoint in endpoints_to_test:
            print(f"🔗 Test de {endpoint}:")
            try:
                async with client.session.get(f"{client.base_url}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Succès (Status: {response.status})")
                        
                        if "automation" in endpoint.lower():
                            print(f"   📄 Données: {json.dumps(data, indent=2)[:500]}...")
                        elif endpoint == "/api/states":
                            # Chercher les entités automation
                            automation_entities = [item for item in data if item.get("entity_id", "").startswith("automation.")]
                            print(f"   🤖 Trouvé {len(automation_entities)} entités automation")
                            for auto in automation_entities[:3]:
                                print(f"      - {auto.get('entity_id')}: {auto.get('attributes', {}).get('friendly_name', 'N/A')}")
                        elif endpoint == "/api/services":
                            # Chercher les services automation
                            automation_services = data.get("automation", {})
                            if automation_services:
                                print(f"   🔧 Services automation disponibles: {list(automation_services.keys())}")
                            else:
                                print("   ⚠️  Aucun service automation trouvé")
                        else:
                            print(f"   📊 Type de données: {type(data)}")
                            if isinstance(data, dict):
                                print(f"   🔑 Clés disponibles: {list(data.keys())[:10]}")
                    else:
                        print(f"   ❌ Échec (Status: {response.status})")
                        
            except Exception as e:
                print(f"   💥 Erreur: {e}")
            
            print()
        
        # Tester la création d'automatisation via le service automation.reload
        print("🔄 Test de rechargement des automatisations:")
        try:
            result = await client.call_service("automation", "reload")
            print(f"   ✅ Service automation.reload appelé avec succès")
            print(f"   📋 Résultat: {result}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        print()
        
        # Vérifier si on peut créer via les services
        print("📝 Vérification des services de création:")
        try:
            services = await client.get_services()
            automation_services = services.get("automation", {})
            
            print(f"   Services automation disponibles:")
            for service_name, service_info in automation_services.items():
                print(f"   - {service_name}: {service_info.get('description', 'Pas de description')}")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(explore_automation_endpoints())