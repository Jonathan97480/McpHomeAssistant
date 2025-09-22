#!/usr/bin/env python3
"""
Test script pour vérifier le fonctionnement de l'interface web
"""

import asyncio
import aiohttp
import json

async def test_web_interface():
    """Test de l'interface web du dashboard"""
    base_url = "http://localhost:8080"
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Page principale
        print("[TEST] Test 1: Page principale")
        try:
            async with session.get(f"{base_url}/") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    print("   [OK] Page principale accessible")
                else:
                    print("   [FAIL] Erreur page principale")
        except Exception as e:
            print(f"   [FAIL] Erreur connexion: {e}")
        
        # Test 2: Page de connexion
        print("\n[TEST] Test 2: Page de connexion")
        try:
            async with session.get(f"{base_url}/login") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    print("   [OK] Page de connexion accessible")
                else:
                    print("   [FAIL] Erreur page de connexion")
        except Exception as e:
            print(f"   [FAIL] Erreur connexion: {e}")
        
        # Test 3: Fichiers statiques CSS
        print("\n[TEST] Test 3: Fichiers CSS")
        try:
            async with session.get(f"{base_url}/static/css/main.css") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    print("   [OK] CSS accessible")
                else:
                    print("   [FAIL] Erreur CSS")
        except Exception as e:
            print(f"   [FAIL] Erreur CSS: {e}")
        
        # Test 4: Fichiers statiques JavaScript
        print("\n[TEST] Test 4: Fichiers JavaScript")
        try:
            async with session.get(f"{base_url}/static/js/dashboard.js") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    print("   [OK] JavaScript accessible")
                else:
                    print("   [FAIL] Erreur JavaScript")
        except Exception as e:
            print(f"   [FAIL] Erreur JavaScript: {e}")
        
        # Test 5: API Métriques
        print("\n[TEST] Test 5: API Métriques")
        try:
            async with session.get(f"{base_url}/api/metrics") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("   [OK] API métriques accessible")
                    print(f"   [STATS] Connexions actives: {data.get('active_connections', 0)}")
                    print(f"   [TOOL] Outils MCP: {data.get('total_tools', 0)}")
                else:
                    print("   [FAIL] Erreur API métriques")
        except Exception as e:
            print(f"   [FAIL] Erreur API métriques: {e}")
        
        # Test 6: API Configuration
        print("\n[TEST] Test 6: API Configuration")
        try:
            async with session.get(f"{base_url}/api/config") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("   [OK] API configuration accessible")
                    print(f"   [HOME] Home Assistant: {data.get('homeassistant', {}).get('connected', False)}")
                else:
                    print("   [FAIL] Erreur API configuration")
        except Exception as e:
            print(f"   [FAIL] Erreur API configuration: {e}")
        
        # Test 7: API Outils
        print("\n[TEST] Test 7: API Outils MCP")
        try:
            async with session.get(f"{base_url}/api/tools") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("   [OK] API outils accessible")
                    # data est directement la liste des outils, pas un dictionnaire
                    if isinstance(data, list):
                        print(f"   [TOOL] Nombre d'outils: {len(data)}")
                    elif isinstance(data, dict) and 'tools' in data:
                        print(f"   [TOOL] Nombre d'outils: {len(data['tools'])}")
                    else:
                        print(f"   [TOOL] Données reçues: {type(data)}")
                else:
                    print("   [FAIL] Erreur API outils")
        except Exception as e:
            print(f"   [FAIL] Erreur API outils: {e}")
        
        # Test 8: API Logs
        print("\n[TEST] Test 8: API Logs")
        try:
            async with session.get(f"{base_url}/api/logs?limit=5") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("   [OK] API logs accessible")
                    print(f"   [NOTE] Nombre de logs: {len(data.get('logs', []))}")
                else:
                    print("   [FAIL] Erreur API logs")
        except Exception as e:
            print(f"   [FAIL] Erreur API logs: {e}")
        
        # Test 9: Templates
        print("\n[TEST] Test 9: Templates HTML")
        templates = ["dashboard-overview", "permissions", "config", "tools", "logs", "admin"]
        for template in templates:
            try:
                async with session.get(f"{base_url}/api/templates/{template}") as response:
                    if response.status == 200:
                        print(f"   [OK] Template {template}")
                    else:
                        print(f"   [FAIL] Template {template} - Status: {response.status}")
            except Exception as e:
                print(f"   [FAIL] Template {template} - Erreur: {e}")
        
        print("\n[PARTY] Tests terminés!")

def main():
    """Point d'entrée principal"""
    print("[START] Démarrage des tests de l'interface web")
    print("[LIST] Vérification de tous les composants du dashboard")
    print("=" * 50)
    
    try:
        asyncio.run(test_web_interface())
    except KeyboardInterrupt:
        print("\n⏹[EMOJI]  Tests interrompus")
    except Exception as e:
        print(f"\n[FAIL] Erreur générale: {e}")

if __name__ == "__main__":
    main()