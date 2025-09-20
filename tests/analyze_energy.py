#!/usr/bin/env python3
"""
Analyse du capteur de consommation énergétique
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Charger les variables d'environnement
load_dotenv()

# Ajouter le chemin du module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from homeassistant_mcp_server.server import HomeAssistantClient

async def analyze_energy_consumption():
    """Analyser le capteur de consommation énergétique"""
    
    hass_url = os.getenv("HASS_URL", "http://192.168.1.22:8123")
    hass_token = os.getenv("HASS_TOKEN", "")
    
    if not hass_token:
        print("❌ Token requis")
        return
    
    async with HomeAssistantClient(hass_url, hass_token) as client:
        energy_sensor = "sensor.kws_306wf_energie_totale"
        
        print("⚡ Analyse de votre consommation énergétique\n")
        
        # État actuel
        print("📊 État actuel du capteur:")
        try:
            current_state = await client.get_entity_state(energy_sensor)
            state = current_state["state"]
            unit = current_state["attributes"].get("unit_of_measurement", "")
            friendly_name = current_state["attributes"].get("friendly_name", energy_sensor)
            last_updated = current_state["last_updated"]
            
            print(f"🔸 {friendly_name}")
            print(f"   Consommation totale: {state} {unit}")
            print(f"   Dernière mise à jour: {last_updated}")
            
            # Informations supplémentaires
            attributes = current_state["attributes"]
            if "device_class" in attributes:
                print(f"   Type de capteur: {attributes['device_class']}")
            if "state_class" in attributes:
                print(f"   Classe d'état: {attributes['state_class']}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la lecture: {e}")
            return
        
        print()
        
        # Historique des dernières 24h
        print("📈 Historique des dernières 24 heures:")
        try:
            # Calculer la date de début (24h en arrière)
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)
            
            history = await client.get_history(
                entity_id=energy_sensor,
                start_time=start_time,
                end_time=end_time
            )
            
            if history:
                print(f"   Trouvé {len(history)} points de données")
                
                # Premier et dernier point
                first_point = history[0]
                last_point = history[-1]
                
                first_value = float(first_point["state"]) if first_point["state"] != "unknown" else None
                last_value = float(last_point["state"]) if last_point["state"] != "unknown" else None
                
                if first_value is not None and last_value is not None:
                    consumption_24h = last_value - first_value
                    print(f"   🏠 Consommation des 24h: {consumption_24h:.2f} kWh")
                    print(f"   📅 Du {first_point['last_updated'][:19]} au {last_point['last_updated'][:19]}")
                    
                    # Estimation consommation journalière moyenne
                    if consumption_24h > 0:
                        daily_average = consumption_24h
                        monthly_estimate = daily_average * 30
                        yearly_estimate = daily_average * 365
                        
                        print(f"\n💡 Estimations basées sur les dernières 24h:")
                        print(f"   📊 Consommation journalière: {daily_average:.2f} kWh/jour")
                        print(f"   📊 Estimation mensuelle: {monthly_estimate:.1f} kWh/mois")
                        print(f"   📊 Estimation annuelle: {yearly_estimate:.0f} kWh/an")
                        
                        # Coût estimé (environ 0.20€/kWh en France)
                        cost_per_kwh = 0.20
                        daily_cost = daily_average * cost_per_kwh
                        monthly_cost = monthly_estimate * cost_per_kwh
                        yearly_cost = yearly_estimate * cost_per_kwh
                        
                        print(f"\n💰 Estimation des coûts (à ~{cost_per_kwh}€/kWh):")
                        print(f"   💶 Coût journalier: {daily_cost:.2f}€/jour")
                        print(f"   💶 Coût mensuel: {monthly_cost:.1f}€/mois")
                        print(f"   💶 Coût annuel: {yearly_cost:.0f}€/an")
                
                # Afficher quelques points récents
                print(f"\n📋 Dernières mesures:")
                for point in history[-5:]:
                    time = point["last_updated"][:19].replace("T", " ")
                    value = point["state"]
                    print(f"   {time}: {value} kWh")
                    
            else:
                print("   ⚠️ Aucun historique trouvé")
                
        except Exception as e:
            print(f"❌ Erreur lors de la lecture de l'historique: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_energy_consumption())