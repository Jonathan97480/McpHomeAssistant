#!/usr/bin/env python3
"""
Affichage détaillé de tous les capteurs Home Assistant
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

async def show_sensors():
    """Afficher tous les capteurs en détail"""
    
    hass_url = os.getenv("HASS_URL", "http://192.168.1.22:8123")
    hass_token = os.getenv("HASS_TOKEN", "")
    
    if not hass_token:
        print("❌ Token requis")
        return
    
    async with HomeAssistantClient(hass_url, hass_token) as client:
        print("🔍 Analyse détaillée de vos capteurs Home Assistant\n")
        
        # Récupérer toutes les entités
        entities = await client.get_entities()
        
        # Filtrer les capteurs
        sensors = [e for e in entities if e["entity_id"].startswith("sensor.")]
        
        print(f"📊 Trouvé {len(sensors)} capteurs :\n")
        
        for i, sensor in enumerate(sensors, 1):
            entity_id = sensor["entity_id"]
            state = sensor["state"]
            attributes = sensor["attributes"]
            
            friendly_name = attributes.get("friendly_name", entity_id)
            unit = attributes.get("unit_of_measurement", "")
            device_class = attributes.get("device_class", "")
            
            print(f"🔸 {i}. {friendly_name}")
            print(f"   ID: {entity_id}")
            print(f"   État: {state} {unit}")
            
            if device_class:
                print(f"   Type: {device_class}")
            
            # Rechercher des mots-clés liés à la consommation
            keywords = ["power", "energy", "consumption", "consommation", "watts", "watt", "kwh", "total"]
            text_to_search = f"{entity_id} {friendly_name}".lower()
            
            matching_keywords = [kw for kw in keywords if kw in text_to_search]
            if matching_keywords:
                print(f"   🔋 Mots-clés énergétiques détectés: {', '.join(matching_keywords)}")
            
            print()

if __name__ == "__main__":
    asyncio.run(show_sensors())