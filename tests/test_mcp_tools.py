#!/usr/bin/env python3
"""
Test des outils MCP Home Assistant
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

async def test_mcp_tools():
    """Test des différents outils MCP"""
    
    hass_url = os.getenv("HASS_URL", "http://192.168.1.22:8123")
    hass_token = os.getenv("HASS_TOKEN", "")
    
    if not hass_token:
        print("❌ Token requis pour ce test")
        return
    
    async with HomeAssistantClient(hass_url, hass_token) as client:
        print("🧪 Test des outils MCP Home Assistant\n")
        
        # 1. Test get_entities
        print("📋 1. Test get_entities...")
        try:
            entities = await client.get_entities()
            print(f"✅ Trouvé {len(entities)} entités")
            
            # Grouper par domaine
            domains = {}
            for entity in entities:
                domain = entity["entity_id"].split(".")[0]
                if domain not in domains:
                    domains[domain] = []
                domains[domain].append(entity)
            
            print("📊 Entités par domaine:")
            for domain, domain_entities in domains.items():
                print(f"  - {domain}: {len(domain_entities)} entités")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print()
        
        # 2. Test get_entity_state sur une entité spécifique
        print("🔍 2. Test get_entity_state...")
        try:
            # Prendre la première entité disponible
            entities = await client.get_entities()
            if entities:
                test_entity = entities[0]
                entity_id = test_entity["entity_id"]
                
                entity_state = await client.get_entity_state(entity_id)
                print(f"✅ État de {entity_id}:")
                print(f"  - État: {entity_state['state']}")
                print(f"  - Dernière mise à jour: {entity_state['last_updated']}")
                
                # Afficher quelques attributs
                attributes = entity_state.get("attributes", {})
                if attributes:
                    print(f"  - Attributs: {list(attributes.keys())[:3]}...")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print()
        
        # 3. Test get_services
        print("🛠️ 3. Test get_services...")
        try:
            services = await client.get_services()
            print(f"✅ Trouvé {len(services)} domaines de services")
            
            # Afficher quelques services populaires
            common_services = ["homeassistant", "light", "switch", "automation"]
            for service_domain in common_services:
                if service_domain in services:
                    domain_services = list(services[service_domain].keys())
                    print(f"  - {service_domain}: {domain_services[:3]}...")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print()
        
        # 4. Test get_history (sur une entité capteur si disponible)
        print("📈 4. Test get_history...")
        try:
            entities = await client.get_entities()
            sensor_entities = [e for e in entities if e["entity_id"].startswith("sensor.")]
            
            if sensor_entities:
                test_sensor = sensor_entities[0]
                entity_id = test_sensor["entity_id"]
                
                history = await client.get_history(entity_id)
                print(f"✅ Historique de {entity_id}:")
                print(f"  - {len(history)} entrées d'historique")
                
                if history:
                    print(f"  - Première entrée: {history[0]['state']} à {history[0]['last_updated'][:19]}")
                    print(f"  - Dernière entrée: {history[-1]['state']} à {history[-1]['last_updated'][:19]}")
            else:
                print("⚠️ Aucun capteur trouvé pour tester l'historique")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print("\n🎉 Tests terminés ! Votre serveur MCP est prêt à être utilisé avec Claude.")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())