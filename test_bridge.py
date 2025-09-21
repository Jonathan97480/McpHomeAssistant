#!/usr/bin/env python3
"""
🧪 Test du HTTP-MCP Bridge
Script de test pour valider le fonctionnement du bridge
"""

import asyncio
import httpx
import json
from datetime import datetime

class BridgeTestClient:
    def __init__(self, base_url: str = "http://localhost:3003"):
        self.base_url = base_url
        self.session_id = None
        
    async def test_health(self):
        """Test du health check"""
        print("🏥 Test Health Check...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            return response.status_code == 200
    
    async def test_initialize(self):
        """Test de l'initialisation de session"""
        print("\n🔧 Test Initialize Session...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp/initialize",
                json={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0"}
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["result"]["session_id"]
                print(f"   Session ID: {self.session_id}")
                print(f"   Protocol Version: {data['result']['protocolVersion']}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
    
    async def test_list_tools(self):
        """Test de la liste des outils"""
        print("\n🛠️ Test List Tools...")
        if not self.session_id:
            print("   ❌ No session ID - run initialize first")
            return False
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp/tools/list",
                headers={"X-Session-ID": self.session_id},
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                tools = data["result"]["tools"]
                print(f"   Found {len(tools)} tools:")
                for tool in tools:
                    print(f"     - {tool['name']}: {tool['description']}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
    
    async def test_call_tool(self):
        """Test d'appel d'outil"""
        print("\n⚡ Test Call Tool (get_entities)...")
        if not self.session_id:
            print("   ❌ No session ID - run initialize first")
            return False
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp/tools/call",
                headers={
                    "X-Session-ID": self.session_id,
                    "X-Priority": "HIGH"
                },
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "get_entities",
                        "arguments": {"domain": "light"}
                    }
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                result = data["result"]
                print(f"   Execution time: {data.get('bridge_info', {}).get('execution_time_ms', 'N/A')}ms")
                print(f"   Result content: {result['content'][0]['text'][:100]}...")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
    
    async def test_call_service(self):
        """Test d'appel de service"""
        print("\n🎛️ Test Call Service (turn_on light)...")
        if not self.session_id:
            print("   ❌ No session ID - run initialize first")
            return False
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp/tools/call",
                headers={
                    "X-Session-ID": self.session_id,
                    "X-Priority": "MEDIUM"
                },
                json={
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "call_service",
                        "arguments": {
                            "domain": "light",
                            "service": "turn_on",
                            "entity_id": "light.salon_lamp",
                            "data": {"brightness": 180}
                        }
                    }
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                result = data["result"]
                print(f"   Execution time: {data.get('bridge_info', {}).get('execution_time_ms', 'N/A')}ms")
                print(f"   Result: {result['content'][0]['text']}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
    
    async def test_status(self):
        """Test du statut du bridge"""
        print("\n📊 Test Bridge Status...")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/mcp/status")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Bridge Status: {data['bridge']['status']}")
                print(f"   Sessions: {data['sessions']['total']} total, {data['sessions']['healthy']} healthy")
                print(f"   Queue: {data['queue']['pending']} pending, {data['queue']['processing']} processing")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
    
    async def test_concurrent_requests(self):
        """Test de requêtes simultanées pour valider la queue"""
        print("\n🔄 Test Concurrent Requests (Queue Management)...")
        if not self.session_id:
            print("   ❌ No session ID - run initialize first")
            return False
        
        # Créer plusieurs requêtes simultanées
        tasks = []
        async with httpx.AsyncClient() as client:
            for i in range(5):
                task = client.post(
                    f"{self.base_url}/mcp/tools/call",
                    headers={
                        "X-Session-ID": self.session_id,
                        "X-Priority": "MEDIUM"
                    },
                    json={
                        "jsonrpc": "2.0",
                        "id": 10 + i,
                        "method": "tools/call",
                        "params": {
                            "name": "get_entities",
                            "arguments": {"domain": f"test_{i}"}
                        }
                    }
                )
                tasks.append(task)
            
            # Exécuter toutes les requêtes en parallèle
            start_time = datetime.now()
            responses = await asyncio.gather(*tasks)
            end_time = datetime.now()
            
            print(f"   Executed {len(responses)} concurrent requests")
            print(f"   Total time: {(end_time - start_time).total_seconds():.3f}s")
            
            success_count = sum(1 for r in responses if r.status_code == 200)
            print(f"   Success rate: {success_count}/{len(responses)} ({success_count/len(responses)*100:.1f}%)")
            
            return success_count == len(responses)


async def main():
    """Exécute tous les tests du bridge"""
    print("🚀 Démarrage des tests HTTP-MCP Bridge")
    print("=" * 50)
    
    client = BridgeTestClient()
    results = []
    
    # Tests séquentiels
    tests = [
        ("Health Check", client.test_health),
        ("Initialize Session", client.test_initialize),
        ("List Tools", client.test_list_tools),
        ("Call Tool (get_entities)", client.test_call_tool),
        ("Call Service", client.test_call_service),
        ("Bridge Status", client.test_status),
        ("Concurrent Requests", client.test_concurrent_requests)
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    success_count = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            success_count += 1
    
    print(f"\n🎯 Résultat global: {success_count}/{len(results)} tests réussis ({success_count/len(results)*100:.1f}%)")
    
    if success_count == len(results):
        print("🎉 Tous les tests sont passés ! Le HTTP-MCP Bridge fonctionne correctement.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les logs ci-dessus.")


if __name__ == "__main__":
    asyncio.run(main())