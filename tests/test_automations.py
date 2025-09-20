#!/usr/bin/env python3
"""
Script de test des fonctionnalités d'automatisation
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

async def test_automation_features():
    """Tester les fonctionnalités d'automatisation"""
    
    hass_url = os.getenv("HASS_URL", "http://192.168.1.22:8123")
    hass_token = os.getenv("HASS_TOKEN", "")
    
    if not hass_token:
        print("❌ Token requis")
        return
    
    async with HomeAssistantClient(hass_url, hass_token) as client:
        print("🤖 Test des fonctionnalités d'automatisation\n")
        
        # 1. Lister les automatisations existantes
        print("📋 1. Liste des automatisations existantes:")
        try:
            automations = await client.list_automations()
            print(f"   Trouvé {len(automations)} automatisations")
            
            if automations:
                for i, auto in enumerate(automations[:3]):  # Afficher seulement les 3 premières
                    print(f"   [{i+1}] {auto.get('alias', 'Sans nom')} (ID: {auto.get('id', 'N/A')})")
            else:
                print("   Aucune automatisation trouvée")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        print()
        
        # 2. Créer une automatisation de test simple
        print("🔧 2. Création d'une automatisation de test:")
        
        # Automatisation simple : notification quotidienne à 8h00
        test_automation = {
            "alias": "Test MCP - Notification matinale",
            "description": "Automatisation de test créée par le serveur MCP",
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
                        "title": "Bonjour!",
                        "message": "Automatisation MCP fonctionne ! Il est 8h00.",
                        "notification_id": "mcp_test_notification"
                    }
                }
            ]
        }
        
        try:
            result = await client.create_automation(test_automation)
            print(f"   ✅ Automatisation créée avec succès!")
            print(f"   ID: {result.get('id', 'N/A')}")
            
            # Stocker l'ID pour nettoyage éventuel
            test_automation_id = result.get('id')
            
        except Exception as e:
            print(f"   ❌ Erreur lors de la création: {e}")
            test_automation_id = None
        
        print()
        
        # 3. Créer une automatisation basée sur le capteur d'énergie
        print("⚡ 3. Automatisation basée sur la consommation énergétique:")
        
        energy_automation = {
            "alias": "Test MCP - Alerte consommation élevée",
            "description": "Alerte quand la consommation dépasse un seuil",
            "trigger": [
                {
                    "platform": "numeric_state",
                    "entity_id": "sensor.kws_306wf_energie_totale",
                    "above": 700  # Alerte si plus de 700 kWh
                }
            ],
            "action": [
                {
                    "service": "persistent_notification.create",
                    "data": {
                        "title": "⚡ Consommation Élevée",
                        "message": "La consommation totale a dépassé 700 kWh!",
                        "notification_id": "high_energy_consumption"
                    }
                }
            ]
        }
        
        try:
            result = await client.create_automation(energy_automation)
            print(f"   ✅ Automatisation énergétique créée!")
            print(f"   ID: {result.get('id', 'N/A')}")
            
            energy_automation_id = result.get('id')
            
        except Exception as e:
            print(f"   ❌ Erreur lors de la création: {e}")
            energy_automation_id = None
        
        print()
        
        # 4. Vérifier les automatisations créées
        print("🔍 4. Vérification des automatisations créées:")
        try:
            automations = await client.list_automations()
            mcp_automations = [a for a in automations if a.get('alias', '').startswith('Test MCP')]
            
            print(f"   Trouvé {len(mcp_automations)} automatisations MCP:")
            for auto in mcp_automations:
                print(f"   - {auto.get('alias', 'Sans nom')} (ID: {auto.get('id', 'N/A')})")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        print()
        
        # 5. Option de nettoyage (commentée pour éviter la suppression accidentelle)
        print("🧹 5. Nettoyage (automatisations de test):")
        print("   ⚠️  Les automatisations de test ont été créées.")
        print("   ⚠️  Pour les supprimer, utilisez Home Assistant UI ou décommentez le code ci-dessous.")
        
        # Décommenter ces lignes pour nettoyer automatiquement
        # if test_automation_id:
        #     try:
        #         await client.delete_automation(test_automation_id)
        #         print(f"   ✅ Automatisation de test supprimée (ID: {test_automation_id})")
        #     except Exception as e:
        #         print(f"   ❌ Erreur suppression: {e}")
        # 
        # if energy_automation_id:
        #     try:
        #         await client.delete_automation(energy_automation_id)
        #         print(f"   ✅ Automatisation énergétique supprimée (ID: {energy_automation_id})")
        #     except Exception as e:
        #         print(f"   ❌ Erreur suppression: {e}")
        
        print("\n🎉 Test des automatisations terminé!")
        print("\n💡 Exemples d'automatisations que vous pouvez créer:")
        print("   - Allumer les lumières au coucher du soleil")
        print("   - Éteindre les appareils quand personne n'est à la maison")
        print("   - Notifications sur la consommation énergétique")
        print("   - Climatisation automatique selon la température")
        print("   - Sauvegarde des données de capteurs")

if __name__ == "__main__":
    asyncio.run(test_automation_features())