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
        print("🧪 Test 1: Page principale")
        try:
            async with session.get(f"{base_url}/") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    print("   ✅ Page principale accessible")
                else:
                    print("   ❌ Erreur page principale")
        except Exception as e:
            print(f"   ❌ Erreur connexion: {e}")
        
        # Test 2: Page de connexion
        print("\n🧪 Test 2: Page de connexion")
        try:
            async with session.get(f"{base_url}/login") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    print("   ✅ Page de connexion accessible")
                else:
                    print("   ❌ Erreur page de connexion")
        except Exception as e:
            print(f"   ❌ Erreur connexion: {e}")
        
        # Test 3: Fichiers statiques CSS
        print("\n🧪 Test 3: Fichiers CSS")
        try:
            async with session.get(f"{base_url}/static/css/main.css") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    print("   ✅ CSS accessible")
                else:
                    print("   ❌ Erreur CSS")
        except Exception as e:
            print(f"   ❌ Erreur CSS: {e}")
        
        # Test 4: Fichiers statiques JavaScript
        print("\n🧪 Test 4: Fichiers JavaScript")
        try:
            async with session.get(f"{base_url}/static/js/dashboard.js") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    print("   ✅ JavaScript accessible")
                else:
                    print("   ❌ Erreur JavaScript")
        except Exception as e:
            print(f"   ❌ Erreur JavaScript: {e}")
        
        # Test 5: API Métriques
        print("\n🧪 Test 5: API Métriques")
        try:
            async with session.get(f"{base_url}/api/metrics") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("   ✅ API métriques accessible")
                    print(f"   📊 Connexions actives: {data.get('active_connections', 0)}")
                    print(f"   🔧 Outils MCP: {data.get('total_tools', 0)}")
                else:
                    print("   ❌ Erreur API métriques")
        except Exception as e:
            print(f"   ❌ Erreur API métriques: {e}")
        
        # Test 6: API Configuration
        print("\n🧪 Test 6: API Configuration")
        try:
            async with session.get(f"{base_url}/api/config") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("   ✅ API configuration accessible")
                    print(f"   🏠 Home Assistant: {data.get('homeassistant', {}).get('connected', False)}")
                else:
                    print("   ❌ Erreur API configuration")
        except Exception as e:
            print(f"   ❌ Erreur API configuration: {e}")
        
        # Test 7: API Outils
        print("\n🧪 Test 7: API Outils MCP")
        try:
            async with session.get(f"{base_url}/api/tools") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("   ✅ API outils accessible")
                    print(f"   🔧 Nombre d'outils: {len(data.get('tools', []))}")
                else:
                    print("   ❌ Erreur API outils")
        except Exception as e:
            print(f"   ❌ Erreur API outils: {e}")
        
        # Test 8: API Logs
        print("\n🧪 Test 8: API Logs")
        try:
            async with session.get(f"{base_url}/api/logs?limit=5") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print("   ✅ API logs accessible")
                    print(f"   📝 Nombre de logs: {len(data.get('logs', []))}")
                else:
                    print("   ❌ Erreur API logs")
        except Exception as e:
            print(f"   ❌ Erreur API logs: {e}")
        
        # Test 9: Templates
        print("\n🧪 Test 9: Templates HTML")
        templates = ["dashboard-overview", "permissions", "config", "tools", "logs", "admin"]
        for template in templates:
            try:
                async with session.get(f"{base_url}/api/templates/{template}") as response:
                    if response.status == 200:
                        print(f"   ✅ Template {template}")
                    else:
                        print(f"   ❌ Template {template} - Status: {response.status}")
            except Exception as e:
                print(f"   ❌ Template {template} - Erreur: {e}")
        
        print("\n🎉 Tests terminés!")

def main():
    """Point d'entrée principal"""
    print("🚀 Démarrage des tests de l'interface web")
    print("📋 Vérification de tous les composants du dashboard")
    print("=" * 50)
    
    try:
        asyncio.run(test_web_interface())
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrompus")
    except Exception as e:
        print(f"\n❌ Erreur générale: {e}")

if __name__ == "__main__":
    main()