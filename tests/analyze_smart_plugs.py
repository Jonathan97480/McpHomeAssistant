#!/usr/bin/env python3
"""
Analyse des prises connectées et de leur consommation
"""

import asyncio
import sys
import os
import json
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le chemin du module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from homeassistant_mcp_server.server import HomeAssistantClient

async def analyze_smart_plugs():
    """Analyser les prises connectées et leur consommation"""
    
    hass_url = os.getenv("HASS_URL", "http://192.168.1.22:8123")
    hass_token = os.getenv("HASS_TOKEN", "")
    
    if not hass_token:
        print("❌ Token requis")
        return
    
    async with HomeAssistantClient(hass_url, hass_token) as client:
        print("🔌 Analyse des prises connectées et capteurs de consommation\n")
        
        # Récupérer toutes les entités
        entities = await client.get_entities()
        
        # Rechercher les prises et capteurs de consommation
        smart_plugs = []
        power_sensors = []
        energy_sensors = []
        switches = []
        
        for entity in entities:
            entity_id = entity["entity_id"]
            attributes = entity.get("attributes", {})
            device_class = attributes.get("device_class", "")
            unit = attributes.get("unit_of_measurement", "")
            friendly_name = attributes.get("friendly_name", entity_id)
            
            # Identifier les prises connectées
            if (entity_id.startswith("switch.") and 
                ("prise" in friendly_name.lower() or 
                 "plug" in friendly_name.lower() or
                 "socket" in friendly_name.lower())):
                smart_plugs.append(entity)
            
            # Identifier les capteurs de puissance (W)
            elif (entity_id.startswith("sensor.") and 
                  (device_class == "power" or unit == "W")):
                power_sensors.append(entity)
            
            # Identifier les capteurs d'énergie (kWh, Wh)
            elif (entity_id.startswith("sensor.") and 
                  (device_class == "energy" or unit in ["kWh", "Wh"])):
                energy_sensors.append(entity)
            
            # Tous les switches (potentiellement des prises)
            elif entity_id.startswith("switch."):
                switches.append(entity)
        
        # Afficher les résultats
        print("🔍 Résultats de l'analyse:\n")
        
        # 1. Prises connectées identifiées
        print(f"🔌 Prises connectées trouvées: {len(smart_plugs)}")
        for plug in smart_plugs:
            state = "🟢 ON" if plug["state"] == "on" else "🔴 OFF"
            print(f"   - {plug['attributes'].get('friendly_name', plug['entity_id'])}: {state}")
        
        if not smart_plugs and switches:
            print("   ⚠️  Aucune prise explicitement identifiée, mais voici tous les switches:")
            for switch in switches[:10]:  # Limiter à 10
                state = "🟢 ON" if switch["state"] == "on" else "🔴 OFF"
                print(f"   - {switch['attributes'].get('friendly_name', switch['entity_id'])}: {state}")
        
        print()
        
        # 2. Capteurs de puissance instantanée
        print(f"⚡ Capteurs de puissance instantanée: {len(power_sensors)}")
        for sensor in power_sensors:
            state = sensor["state"]
            unit = sensor["attributes"].get("unit_of_measurement", "")
            friendly_name = sensor["attributes"].get("friendly_name", sensor["entity_id"])
            print(f"   - {friendly_name}: {state} {unit}")
        
        print()
        
        # 3. Capteurs d'énergie/consommation
        print(f"📊 Capteurs d'énergie/consommation: {len(energy_sensors)}")
        for sensor in energy_sensors:
            state = sensor["state"]
            unit = sensor["attributes"].get("unit_of_measurement", "")
            friendly_name = sensor["attributes"].get("friendly_name", sensor["entity_id"])
            print(f"   - {friendly_name}: {state} {unit}")
        
        print()
        
        # 4. Recherche plus large par mots-clés
        print("🔍 Recherche étendue par mots-clés (power, energy, consommation):")
        keywords = ["power", "energy", "consommation", "watt", "kwh", "current", "voltage"]
        keyword_entities = []
        
        for entity in entities:
            entity_id = entity["entity_id"]
            friendly_name = entity["attributes"].get("friendly_name", entity_id).lower()
            
            if any(keyword in friendly_name or keyword in entity_id.lower() for keyword in keywords):
                keyword_entities.append(entity)
        
        print(f"   Trouvé {len(keyword_entities)} entités liées à l'énergie:")
        for entity in keyword_entities[:15]:  # Limiter l'affichage
            state = entity["state"]
            unit = entity["attributes"].get("unit_of_measurement", "")
            friendly_name = entity["attributes"].get("friendly_name", entity["entity_id"])
            device_class = entity["attributes"].get("device_class", "N/A")
            print(f"   - {friendly_name}: {state} {unit} (classe: {device_class})")
        
        print()
        
        # 5. Exemple d'automatisation pour surveiller la consommation des prises
        if power_sensors or energy_sensors:
            print("💡 Exemples d'automatisations pour vos prises connectées:")
            
            # Automatisation d'alerte de consommation élevée
            if power_sensors:
                example_sensor = power_sensors[0]["entity_id"]
                print(f"\n🔋 Alerte consommation élevée sur {example_sensor}:")
                automation_example = {
                    "alias": "Alerte consommation prise élevée",
                    "trigger": [
                        {
                            "platform": "numeric_state",
                            "entity_id": example_sensor,
                            "above": 100  # Plus de 100W
                        }
                    ],
                    "action": [
                        {
                            "service": "persistent_notification.create",
                            "data": {
                                "title": "⚡ Consommation Élevée Détectée",
                                "message": f"La prise consomme plus de 100W: {{{{ states('{example_sensor}') }}}} W",
                                "notification_id": "high_power_alert"
                            }
                        }
                    ]
                }
                
                # Afficher le YAML pour cette automatisation
                yaml_content = yaml.dump([automation_example], default_flow_style=False, allow_unicode=True)
                print(f"```yaml\n{yaml_content}```")
            
            # Automatisation d'extinction automatique
            if smart_plugs or switches:
                example_switch = (smart_plugs[0] if smart_plugs else switches[0])["entity_id"]
                print(f"\n🔄 Extinction automatique de {example_switch} après 2h:")
                automation_example2 = {
                    "alias": "Extinction automatique prise",
                    "trigger": [
                        {
                            "platform": "state",
                            "entity_id": example_switch,
                            "to": "on",
                            "for": "02:00:00"  # 2 heures
                        }
                    ],
                    "action": [
                        {
                            "service": "switch.turn_off",
                            "target": {
                                "entity_id": example_switch
                            }
                        },
                        {
                            "service": "persistent_notification.create",
                            "data": {
                                "title": "🔌 Extinction Automatique",
                                "message": f"La prise {example_switch} a été éteinte après 2h d'utilisation",
                                "notification_id": "auto_shutdown"
                            }
                        }
                    ]
                }
                
                yaml_content2 = yaml.dump([automation_example2], default_flow_style=False, allow_unicode=True)
                print(f"```yaml\n{yaml_content2}```")
        
        print("\n🎯 Avec votre serveur MCP, vous pouvez maintenant:")
        print("✅ Surveiller la consommation de chaque prise")
        print("✅ Contrôler l'état ON/OFF des prises")
        print("✅ Créer des alertes de consommation excessive")
        print("✅ Programmer des extinctions automatiques")
        print("✅ Analyser l'historique de consommation par appareil")
        print("✅ Optimiser votre consommation énergétique globale")

if __name__ == "__main__":
    asyncio.run(analyze_smart_plugs())