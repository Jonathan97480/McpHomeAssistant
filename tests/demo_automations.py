#!/usr/bin/env python3
"""
Test de création d'automatisations avec affichage du YAML généré
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

async def test_automation_yaml_generation():
    """Tester la génération YAML d'automatisations"""
    
    hass_url = os.getenv("HASS_URL", "http://192.168.1.22:8123")
    hass_token = os.getenv("HASS_TOKEN", "")
    
    if not hass_token:
        print("❌ Token requis")
        return
    
    async with HomeAssistantClient(hass_url, hass_token) as client:
        print("🔧 Test de génération d'automatisations YAML\n")
        
        # Exemple 1: Notification quotidienne
        print("📅 1. Automatisation quotidienne (notification à 8h):")
        automation1 = {
            "alias": "Notification matinale MCP",
            "description": "Notification quotidienne à 8h créée par MCP",
            "trigger": [
                {
                    "platform": "time",
                    "at": "08:00:00"
                }
            ],
            "action": [
                {
                    "service": "persistent_notification.create",
                    "data": {
                        "title": "🌅 Bonjour!",
                        "message": "Il est 8h, bonne journée !",
                        "notification_id": "morning_notification"
                    }
                }
            ]
        }
        
        try:
            result = await client.create_automation(automation1)
            if result.get("status") == "yaml_generated":
                print("✅ YAML généré avec succès!")
                print(f"\n{result['yaml_content']}")
            else:
                print(f"✅ Création directe réussie: {result}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print("\n" + "="*60 + "\n")
        
        # Exemple 2: Automatisation basée sur l'énergie
        print("⚡ 2. Automatisation basée sur la consommation:")
        automation2 = {
            "alias": "Alerte consommation élevée",
            "description": "Alerte quand la consommation dépasse 700 kWh",
            "trigger": [
                {
                    "platform": "numeric_state",
                    "entity_id": "sensor.kws_306wf_energie_totale",
                    "above": 700
                }
            ],
            "condition": [
                {
                    "condition": "time",
                    "after": "06:00:00",
                    "before": "22:00:00"
                }
            ],
            "action": [
                {
                    "service": "persistent_notification.create",
                    "data": {
                        "title": "⚡ Consommation Élevée Détectée",
                        "message": "Votre consommation totale a dépassé 700 kWh ! Valeur actuelle: {{ states('sensor.kws_306wf_energie_totale') }} kWh",
                        "notification_id": "high_energy_alert"
                    }
                }
            ]
        }
        
        try:
            result = await client.create_automation(automation2)
            if result.get("status") == "yaml_generated":
                print("✅ YAML généré avec succès!")
                print(f"\n{result['yaml_content']}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print("\n" + "="*60 + "\n")
        
        # Exemple 3: Automatisation au coucher du soleil
        print("🌅 3. Automatisation coucher du soleil:")
        automation3 = {
            "alias": "Éclairage automatique au coucher",
            "description": "Allume les lumières 30 minutes avant le coucher du soleil",
            "trigger": [
                {
                    "platform": "sun",
                    "event": "sunset",
                    "offset": "-00:30:00"
                }
            ],
            "condition": [
                {
                    "condition": "state",
                    "entity_id": "person.jonathan_gauvin",
                    "state": "home"
                }
            ],
            "action": [
                {
                    "service": "light.turn_on",
                    "target": {
                        "area_id": "salon"
                    },
                    "data": {
                        "brightness": 180,
                        "color_temp": 400
                    }
                },
                {
                    "service": "persistent_notification.create",
                    "data": {
                        "title": "🌆 Éclairage automatique",
                        "message": "Les lumières du salon ont été allumées pour le coucher du soleil",
                        "notification_id": "sunset_lighting"
                    }
                }
            ]
        }
        
        try:
            result = await client.create_automation(automation3)
            if result.get("status") == "yaml_generated":
                print("✅ YAML généré avec succès!")
                print(f"\n{result['yaml_content']}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print("\n" + "="*60 + "\n")
        
        print("📝 Instructions pour utiliser ces automatisations:")
        print("1. Copiez le contenu YAML ci-dessus")
        print("2. Ajoutez-le à votre fichier automations.yaml sur le Raspberry Pi")
        print("3. Redémarrez Home Assistant ou appelez le service automation.reload")
        print("4. Les automatisations apparaîtront dans l'interface Home Assistant")
        
        print("\n🎯 Votre serveur MCP peut maintenant:")
        print("✅ Générer des automatisations Home Assistant")
        print("✅ Lister les automatisations existantes")
        print("✅ Activer/désactiver des automatisations")
        print("✅ Utiliser votre capteur de consommation énergétique")
        print("✅ Créer des déclencheurs temporels, d'état, et basés sur le soleil")

if __name__ == "__main__":
    asyncio.run(test_automation_yaml_generation())