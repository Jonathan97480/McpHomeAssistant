#!/usr/bin/env python3
"""
🏠 Script automatisé pour Home Assistant MCP Bridge
Création d'utilisateur et récupération des données de consommation
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

class MCPHomeAssistantManager:
    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def check_server_status(self):
        """Vérifie si le serveur est accessible"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Serveur MCP Bridge accessible")
                return True
            else:
                print(f"❌ Serveur répond avec le code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Impossible de contacter le serveur: {e}")
            return False
    
    def create_user_if_needed(self, username, password, email=None):
        """Crée un nouvel utilisateur seulement s'il n'existe pas déjà"""
        print(f"👤 Vérification de l'utilisateur: {username}")
        
        # D'abord essayer de se connecter pour voir si l'utilisateur existe
        if self.login_user(username, password):
            print(f"✅ Utilisateur {username} existe déjà et est connecté")
            return True
        
        # Si la connexion échoue, essayer de créer l'utilisateur
        print(f"👤 Création de l'utilisateur: {username}")
        
        user_data = {
            "username": username,
            "password": password,
            "email": email or f"{username}@example.com",
            "full_name": f"User {username}"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json=user_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Utilisateur créé avec succès")
                print(f"   ID: {result.get('user_id')}")
                print(f"   Username: {result.get('username')}")
                return True
            else:
                print(f"❌ Erreur création utilisateur: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau lors de la création: {e}")
            return False
    
    def login_user(self, username, password):
        """Connecte l'utilisateur et récupère le token"""
        print(f"🔐 Connexion de l'utilisateur: {username}")
        
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result.get('access_token')
                self.user_id = result.get('user_id')
                
                # Ajouter le token aux headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                
                print(f"✅ Connexion réussie")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Erreur de connexion: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau lors de la connexion: {e}")
            return False
    
    def test_home_assistant_connectivity(self, ha_url, ha_token):
        """Teste la connectivité vers Home Assistant"""
        print(f"🏠 Test de connectivité Home Assistant: {ha_url}")
        
        try:
            # Test de base de l'URL
            response = requests.get(ha_url, timeout=10)
            if response.status_code == 200:
                print("✅ Home Assistant accessible")
                
                # Test avec le token
                headers = {
                    'Authorization': f'Bearer {ha_token}',
                    'Content-Type': 'application/json'
                }
                
                api_response = requests.get(f"{ha_url}/api/", headers=headers, timeout=10)
                if api_response.status_code == 200:
                    print("✅ Token Home Assistant valide")
                    return True
                else:
                    print(f"⚠️ Problème avec le token: {api_response.status_code}")
                    return True  # Continuer quand même
            else:
                print(f"❌ Home Assistant non accessible: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connectivité HA: {e}")
            return False
    
    def configure_home_assistant(self, ha_url, ha_token):
        """Configure la connexion Home Assistant"""
        print(f"🏠 Configuration de Home Assistant: {ha_url}")
        
        ha_config = {
            "name": "Default HA Config",
            "url": ha_url,
            "token": ha_token
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/config/homeassistant",
                json=ha_config,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Configuration Home Assistant sauvegardée")
                return True
            else:
                print(f"❌ Erreur configuration HA: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau configuration HA: {e}")
            return False
    
    def initialize_mcp_session(self):
        """Initialise une session MCP"""
        print("🔗 Initialisation de la session MCP...")
        
        mcp_init = {
            "serverName": "home-assistant",
            "client_info": {
                "name": "home-assistant-bridge",
                "version": "1.0.0"
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/mcp/initialize",
                json=mcp_init,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                session_id = result.get('result', {}).get('session_id')
                print(f"✅ Session MCP initialisée: {session_id}")
                return session_id
            else:
                print(f"❌ Erreur initialisation MCP: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau initialisation MCP: {e}")
            return None
    
    def get_mcp_tools(self, session_id):
        """Récupère la liste des outils MCP disponibles"""
        print("🔧 Récupération des outils MCP...")
        
        tools_request = {}
        
        try:
            response = self.session.post(
                f"{self.base_url}/mcp/tools/list",
                json=tools_request,
                headers={'X-Session-ID': session_id},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                tools = result.get('result', {}).get('tools', [])
                print(f"✅ {len(tools)} outils MCP disponibles")
                
                for tool in tools:
                    print(f"   🔧 {tool.get('name')}: {tool.get('description', 'Pas de description')}")
                    print(f"      Input schema: {tool.get('inputSchema', {})}")
                
                return tools
            else:
                print(f"❌ Erreur récupération outils: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau récupération outils: {e}")
            return []
    
    def get_all_devices(self, session_id):
        """Récupère tous les périphériques de Home Assistant"""
        print("📱 Récupération de tous les périphériques...")
        
        # Utiliser l'outil get_entities pour récupérer toutes les entités en format JSON
        call_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_entities",
                "arguments": {
                    "format": "json"  # Demander les données JSON structurées
                }
            }
        }
        
        try:
            print(f"🔍 Envoi de la requête: {call_request}")
            response = self.session.post(
                f"{self.base_url}/mcp/tools/call",
                json=call_request,
                headers={'X-Session-ID': session_id},
                timeout=30
            )
            
            print(f"🔍 Code de réponse: {response.status_code}")
            print(f"🔍 Réponse brute: {response.text[:300]}...")
            
            if response.status_code == 200:
                result = response.json()
                entities_content = result.get('result', {}).get('content', [])
                
                if isinstance(entities_content, list) and entities_content:
                    # Extraire le texte JSON des entités
                    entities_json_text = entities_content[0].get('text', '[]')
                    print(f"🔍 JSON reçu: {str(entities_json_text)[:200]}...")
                    
                    try:
                        # Parser le JSON des entités
                        entities = json.loads(entities_json_text)
                        print(f"✅ {len(entities)} entités parsées avec succès")
                        return entities
                    except json.JSONDecodeError as e:
                        print(f"❌ Erreur parsing JSON entités: {e}")
                        print(f"🔍 Contenu JSON brut: {entities_json_text[:500]}")
                        return []
                    
                    if isinstance(entities_data, str):
                        try:
                            entities_data = json.loads(entities_data)
                        except json.JSONDecodeError as e:
                            print(f"❌ Erreur parsing JSON: {e}")
                            print(f"🔍 Contenu brut: {entities_data}")
                            return []
                    
                    devices = entities_data.get('entities', []) if isinstance(entities_data, dict) else []
                    print(f"✅ {len(devices)} entités trouvées")
                    
                    # Grouper par domaine
                    domains = {}
                    for device in devices:
                        domain = device.get('entity_id', '').split('.')[0]
                        if domain not in domains:
                            domains[domain] = []
                        domains[domain].append(device)
                    
                    print("📊 Répartition par domaine:")
                    for domain, items in domains.items():
                        print(f"   {domain}: {len(items)} entités")
                    
                    return devices
                else:
                    print("⚠️ Aucune entité trouvée dans la réponse")
                    print(f"🔍 Réponse complète: {result}")
                    return []
            else:
                print(f"❌ Erreur récupération entités: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau récupération entités: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Erreur parsing JSON: {e}")
            return []
    
    def calculate_total_consumption(self, session_id, devices):
        """Calcule la consommation totale de la maison"""
        print("⚡ Calcul de la consommation énergétique totale...")
        
        # Rechercher les entités de consommation énergétique avec des critères français/spécifiques
        energy_entities = []
        power_entities = []
        smart_plug_entities = []
        
        # Patterns à rechercher pour identifier les capteurs d'énergie
        energy_patterns = [
            'energie', 'energy', 'kwh', 'wh', 'consommation', 'consumption',
            'kws_306wf', 'energie_totale', 'total_energy', 'compteur'
        ]
        
        power_patterns = [
            'power', 'puissance', 'watt', 'kw', 'instantaneous'
        ]
        
        smart_plug_patterns = [
            'prise', 'plug', 'switch', 'ampli', 'bureau', 'congelateur', 
            'frigidaire', 'plaque', 'tv_switch', 'home_cinema'
        ]
        
        for device in devices:
            entity_id = device.get('entity_id', '').lower()
            friendly_name = device.get('attributes', {}).get('friendly_name', '').lower()
            device_class = device.get('attributes', {}).get('device_class', '').lower()
            unit = device.get('attributes', {}).get('unit_of_measurement', '').lower()
            
            # Debugging: afficher quelques entités pour voir leur structure
            if any(pattern in entity_id or pattern in friendly_name for pattern in energy_patterns + power_patterns + smart_plug_patterns):
                print(f"🔍 Entité détectée: {entity_id}")
                print(f"    Nom: {device.get('attributes', {}).get('friendly_name', 'N/A')}")
                print(f"    État: {device.get('state', 'N/A')}")
                print(f"    Unité: {unit}")
                print(f"    Device class: {device_class}")
            
            # Entités d'énergie (kWh, Wh)
            if (any(pattern in entity_id or pattern in friendly_name for pattern in energy_patterns) or
                'kwh' in unit or 'wh' in unit or 'energy' in device_class):
                energy_entities.append(device)
            
            # Entités de puissance (W, kW)  
            elif (any(pattern in entity_id or pattern in friendly_name for pattern in power_patterns) or
                  unit in ['w', 'kw', 'watt'] or 'power' in device_class):
                power_entities.append(device)
            
            # Prises intelligentes et switches avec énergie
            elif any(pattern in entity_id or pattern in friendly_name for pattern in smart_plug_patterns):
                smart_plug_entities.append(device)
        
        print(f"🔋 Entités d'énergie trouvées: {len(energy_entities)}")
        print(f"⚡ Entités de puissance trouvées: {len(power_entities)}")
        print(f"🔌 Prises/switches intelligents trouvés: {len(smart_plug_entities)}")
        
        total_energy = 0
        total_power = 0
        
        # Traiter directement les entités d'énergie que nous avons trouvées
        for entity in energy_entities:
            entity_id = entity.get('entity_id')
            state = entity.get('state')
            unit = entity.get('attributes', {}).get('unit_of_measurement', '').lower()
            friendly_name = entity.get('attributes', {}).get('friendly_name', entity_id)
            
            if state and state not in ['unknown', 'unavailable', 'None']:
                try:
                    value = float(state)
                    
                    # Convertir en kWh si nécessaire
                    if 'wh' in unit and 'kwh' not in unit:
                        value = value / 1000
                        unit_display = 'kWh'
                    elif 'kwh' in unit:
                        unit_display = 'kWh'
                    else:
                        unit_display = unit
                    
                    total_energy += value
                    print(f"   📊 {friendly_name}: {value:.2f} {unit_display}")
                    
                except ValueError:
                    print(f"   ⚠️ Valeur non numérique pour {friendly_name}: {state}")
        
        # Priorité aux capteurs principaux visibles dans le dashboard
        main_energy_entities = [
            'sensor.kws_306wf_energie_totale',  # Le compteur principal visible
            'sensor.kws_306wf_energy_total',
            'sensor.energie_totale',
            'sensor.total_energy',
            'sensor.energy_consumption',
            'sensor.house_energy',
            'sensor.maison_energie',
            'sensor.distribution_energie'
        ]
        
        # Si nous n'avons pas trouvé d'énergie avec les entités détectées automatiquement,
        # essayons les entités principales connues
        if total_energy == 0:
            for entity_id in main_energy_entities:
                # Chercher dans la liste des entités récupérées
                for entity in devices:
                    if entity.get('entity_id') == entity_id:
                        state = entity.get('state')
                        if state and state not in ['unknown', 'unavailable', 'None']:
                            try:
                                value = float(state)
                                total_energy += value
                                friendly_name = entity.get('attributes', {}).get('friendly_name', entity_id)
                                print(f"   📊 {friendly_name}: {value:.2f} kWh")
                                break
                            except ValueError:
                                continue
        
        print(f"🏠 CONSOMMATION TOTALE DE LA MAISON: {total_energy:.2f} kWh")
        return total_energy
    
    def get_entity_state(self, session_id, entity_id):
        """Récupère l'état d'une entité spécifique"""
        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_state",
                "arguments": {
                    "entity_id": entity_id
                }
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/mcp/tools/call",
                json=call_request,
                headers={'X-Session-ID': session_id},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('result', {}).get('content', [])
                if content and len(content) > 0:
                    state_data = content[0].get('text', '{}')
                    if isinstance(state_data, str):
                        state_data = json.loads(state_data)
                    
                    state_value = state_data.get('state')
                    if state_value and state_value.lower() not in ['unknown', 'unavailable']:
                        try:
                            return float(state_value)
                        except ValueError:
                            return None
            return None
            
        except Exception as e:
            return None

def main():
    """Fonction principale"""
    print("🚀 HOME ASSISTANT MCP BRIDGE - AUTOMATISATION COMPLÈTE")
    print("=" * 60)
    
    # Configuration
    username = "beroute"
    password = "Anna97480"
    ha_url = "http://raspberrypi:8123"  # URL par défaut selon les instructions
    ha_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwOTJjYjIyOTg0YWM0MWY3ODQyZTFjNmEwYzc0OTI2MSIsImlhdCI6MTc1ODM5MzY5MSwiZXhwIjoyMDczNzUzNjkxfQ.CmRkACMTOyMW8dkw6dCCm40nLNSPW66bDNqXWlAsqVU"  # Token Home Assistant
    
    manager = MCPHomeAssistantManager()
    
    try:
        # 1. Vérifier le serveur
        if not manager.check_server_status():
            print("❌ Serveur non accessible. Assurez-vous qu'il est démarré en mode administrateur.")
            return 1
        
        # 2. Tester la connectivité Home Assistant d'abord
        if not manager.test_home_assistant_connectivity(ha_url, ha_token):
            print("❌ Impossible de contacter Home Assistant")
            return 1
        
        # 3. Créer l'utilisateur seulement si nécessaire
        if not manager.create_user_if_needed(username, password):
            print("❌ Impossible de créer ou connecter l'utilisateur")
            return 1
        
        # 4. Se connecter si pas déjà fait
        if not manager.auth_token:
            if not manager.login_user(username, password):
                print("❌ Impossible de se connecter")
                return 1
        
        # 5. Configurer Home Assistant
        if not manager.configure_home_assistant(ha_url, ha_token):
            print("⚠️ Configuration HA échouée, continuons quand même...")
        
        # 6. Initialiser la session MCP
        session_id = manager.initialize_mcp_session()
        if not session_id:
            print("❌ Impossible d'initialiser la session MCP")
            return 1
        
        # 7. Récupérer les outils disponibles
        tools = manager.get_mcp_tools(session_id)
        
        # 8. Récupérer tous les périphériques
        devices = manager.get_all_devices(session_id)
        
        # 9. Calculer la consommation totale
        total_consumption = manager.calculate_total_consumption(session_id, devices)
        
        print("\n" + "=" * 60)
        print("🎉 RÉSUMÉ FINAL:")
        print(f"👤 Utilisateur: {username}")
        print(f"🏠 Home Assistant: {ha_url}")
        print(f"📱 Périphériques trouvés: {len(devices)}")
        print(f"⚡ Consommation totale: {total_consumption:.2f} kWh")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())