#!/usr/bin/env python3
"""
Automatisations spécifiques pour les prises connectées de l'utilisateur
"""

import asyncio
import sys
import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajouter le chemin du module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from homeassistant_mcp_server.server import HomeAssistantClient

async def create_smart_plug_automations():
    """Créer des automatisations personnalisées pour les prises connectées"""
    
    hass_url = os.getenv("HASS_URL", "http://192.168.1.22:8123")
    hass_token = os.getenv("HASS_TOKEN", "")
    
    if not hass_token:
        print("❌ Token requis")
        return
    
    async with HomeAssistantClient(hass_url, hass_token) as client:
        print("🔌 Automatisations personnalisées pour vos prises connectées\n")
        
        automations = []
        
        # 1. Sécurité Imprimante 3D - Extinction automatique après 3h
        print("🖨️ 1. Sécurité Imprimante 3D:")
        automation_3d = {
            "alias": "Sécurité Imprimante 3D - Extinction auto",
            "description": "Éteint automatiquement l'imprimante 3D après 3h pour éviter la surchauffe",
            "trigger": [
                {
                    "platform": "state",
                    "entity_id": "switch.imprimante_3d_hender_5_plus_prise",
                    "to": "on",
                    "for": "03:00:00"
                }
            ],
            "action": [
                {
                    "service": "switch.turn_off",
                    "target": {
                        "entity_id": "switch.imprimante_3d_hender_5_plus_prise"
                    }
                },
                {
                    "service": "persistent_notification.create",
                    "data": {
                        "title": "🖨️ Sécurité Imprimante 3D",
                        "message": "L'imprimante 3D a été éteinte automatiquement après 3h d'utilisation pour votre sécurité.",
                        "notification_id": "3d_printer_safety"
                    }
                }
            ]
        }
        automations.append(automation_3d)
        result = await client.create_automation(automation_3d)
        if result.get("yaml_content"):
            print(f"```yaml\n{result['yaml_content']}```")
        
        print("\n" + "="*60 + "\n")
        
        # 2. Économie d'énergie - Extinction nocturne des appareils non essentiels
        print("🌙 2. Économie d'énergie nocturne:")
        automation_night = {
            "alias": "Extinction nocturne appareils non essentiels",
            "description": "Éteint TV, vidéo projecteur et borne arcade à 23h30",
            "trigger": [
                {
                    "platform": "time",
                    "at": "23:30:00"
                }
            ],
            "action": [
                {
                    "service": "switch.turn_off",
                    "target": {
                        "entity_id": [
                            "switch.tv_switch_prise",
                            "switch.video_projecteur_prise",
                            "switch.borne_arcade_prise_1"
                        ]
                    }
                },
                {
                    "service": "persistent_notification.create",
                    "data": {
                        "title": "🌙 Économie d'énergie",
                        "message": "Appareils de divertissement éteints automatiquement à 23h30",
                        "notification_id": "night_energy_save"
                    }
                }
            ]
        }
        automations.append(automation_night)
        result = await client.create_automation(automation_night)
        if result.get("yaml_content"):
            print(f"```yaml\n{result['yaml_content']}```")
        
        print("\n" + "="*60 + "\n")
        
        # 3. Surveillance des appareils critiques (Congélateur et Frigidaire)
        print("❄️ 3. Surveillance appareils critiques:")
        automation_fridge = {
            "alias": "Alerte panne congélateur/frigidaire",
            "description": "Alerte si le congélateur ou frigidaire est éteint accidentellement",
            "trigger": [
                {
                    "platform": "state",
                    "entity_id": [
                        "switch.congelateur_prise_1",
                        "switch.frigidaire_micro_ondes_prise_1"
                    ],
                    "to": "off",
                    "for": "00:05:00"  # 5 minutes
                }
            ],
            "action": [
                {
                    "service": "persistent_notification.create",
                    "data": {
                        "title": "❄️ ALERTE CRITIQUE",
                        "message": "ATTENTION: {{ trigger.to_state.attributes.friendly_name }} est éteint depuis 5 minutes ! Vérifiez immédiatement.",
                        "notification_id": "critical_appliance_alert"
                    }
                }
            ]
        }
        automations.append(automation_fridge)
        result = await client.create_automation(automation_fridge)
        if result.get("yaml_content"):
            print(f"```yaml\n{result['yaml_content']}```")
        
        print("\n" + "="*60 + "\n")
        
        # 4. Gestion intelligente du bureau
        print("💻 4. Gestion intelligente bureau:")
        automation_office = {
            "alias": "Mode travail bureau",
            "description": "Allume automatiquement la prise bureau le matin en semaine",
            "trigger": [
                {
                    "platform": "time",
                    "at": "08:00:00"
                }
            ],
            "condition": [
                {
                    "condition": "time",
                    "weekday": ["mon", "tue", "wed", "thu", "fri"]
                }
            ],
            "action": [
                {
                    "service": "switch.turn_on",
                    "target": {
                        "entity_id": "switch.bureau_prise_1"
                    }
                },
                {
                    "service": "persistent_notification.create",
                    "data": {
                        "title": "💻 Mode Travail",
                        "message": "Prise bureau activée - Bonne journée de travail !",
                        "notification_id": "office_mode"
                    }
                }
            ]
        }
        automations.append(automation_office)
        result = await client.create_automation(automation_office)
        if result.get("yaml_content"):
            print(f"```yaml\n{result['yaml_content']}```")
        
        print("\n" + "="*60 + "\n")
        
        # 5. Automatisation plaque électrique (sécurité cuisine)
        print("🍳 5. Sécurité cuisine - Plaque électrique:")
        automation_cooking = {
            "alias": "Sécurité plaque électrique",
            "description": "Éteint automatiquement la plaque électrique après 2h",
            "trigger": [
                {
                    "platform": "state",
                    "entity_id": "switch.plaque_electrique_prise_1",
                    "to": "on",
                    "for": "02:00:00"
                }
            ],
            "action": [
                {
                    "service": "switch.turn_off",
                    "target": {
                        "entity_id": "switch.plaque_electrique_prise_1"
                    }
                },
                {
                    "service": "persistent_notification.create",
                    "data": {
                        "title": "🍳 Sécurité Cuisine",
                        "message": "ATTENTION: La plaque électrique a été éteinte automatiquement après 2h d'utilisation pour votre sécurité !",
                        "notification_id": "cooking_safety"
                    }
                }
            ]
        }
        automations.append(automation_cooking)
        result = await client.create_automation(automation_cooking)
        if result.get("yaml_content"):
            print(f"```yaml\n{result['yaml_content']}```")
        
        print("\n" + "="*60 + "\n")
        
        print("🎯 Résumé des automatisations créées:")
        print("✅ Sécurité imprimante 3D (extinction après 3h)")
        print("✅ Économie d'énergie nocturne (23h30)")
        print("✅ Surveillance appareils critiques (congélateur/frigidaire)")
        print("✅ Mode travail bureau (8h en semaine)")
        print("✅ Sécurité plaque électrique (extinction après 2h)")
        
        print("\n💡 Utilisations via Claude Desktop:")
        print('• "Allume la prise du vidéo projecteur"')
        print('• "Éteins toutes les prises de divertissement"')
        print('• "Quel est l\'état de mes prises critiques ?"')
        print('• "Crée une automatisation pour éteindre la TV à 22h"')
        print('• "Active le mode économie d\'énergie"')

if __name__ == "__main__":
    asyncio.run(create_smart_plug_automations())