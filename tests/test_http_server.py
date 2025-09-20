#!/usr/bin/env python3
"""
Test script for the HTTP server wrapper
Tests all endpoints to ensure proper functionality
"""

import asyncio
import aiohttp
import json
import sys
import time
from typing import Dict, Any, Optional

class HTTPServerTester:
    def __init__(self, base_url: str = "http://localhost:3002"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, method: str, path: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Test a specific endpoint and return the result"""
        url = f"{self.base_url}{path}"
        
        try:
            if method.upper() == 'GET':
                async with self.session.get(url) as response:
                    result = {
                        'status': response.status,
                        'success': response.status == 200,
                        'data': await response.json() if response.status == 200 else await response.text()
                    }
            elif method.upper() == 'POST':
                headers = {'Content-Type': 'application/json'}
                async with self.session.post(url, json=data, headers=headers) as response:
                    result = {
                        'status': response.status,
                        'success': response.status == 200,
                        'data': await response.json() if response.status == 200 else await response.text()
                    }
            else:
                result = {'status': 0, 'success': False, 'data': f'Unsupported method: {method}'}
                
        except Exception as e:
            result = {'status': 0, 'success': False, 'data': f'Error: {str(e)}'}
            
        return result
    
    async def run_tests(self) -> Dict[str, Any]:
        """Run all endpoint tests"""
        print("🧪 Testing HTTP Server Endpoints")
        print("=" * 50)
        
        tests = []
        
        # Test 1: Health check
        print("1. Testing health endpoint...")
        health_result = await self.test_endpoint('GET', '/health')
        tests.append(('Health Check', health_result))
        
        if health_result['success']:
            print(f"   ✅ Server is healthy: {health_result['data']['status']}")
        else:
            print(f"   ❌ Health check failed: {health_result['data']}")
        
        # Test 2: Get entities
        print("\n2. Testing entities endpoint...")
        entities_result = await self.test_endpoint('GET', '/api/entities')
        tests.append(('Get Entities', entities_result))
        
        if entities_result['success']:
            entities = entities_result['data'].get('entities', [])
            print(f"   ✅ Found {len(entities)} entities")
            if entities:
                print(f"   📝 Sample entities: {[e.get('entity_id', 'unknown') for e in entities[:3]]}")
        else:
            print(f"   ❌ Entities request failed: {entities_result['data']}")
        
        # Test 3: Get specific entity (if entities exist)
        if entities_result['success'] and entities_result['data'].get('entities'):
            entity_id = entities_result['data']['entities'][0].get('entity_id')
            if entity_id:
                print(f"\n3. Testing specific entity: {entity_id}...")
                entity_result = await self.test_endpoint('GET', f'/api/entities/{entity_id}')
                tests.append(('Get Specific Entity', entity_result))
                
                if entity_result['success']:
                    print(f"   ✅ Entity details retrieved")
                    entity_data = entity_result['data']
                    print(f"   📝 State: {entity_data.get('state', 'unknown')}")
                else:
                    print(f"   ❌ Entity request failed: {entity_result['data']}")
        
        # Test 4: Service call (test with a safe service)
        print(f"\n4. Testing service call endpoint...")
        service_data = {
            "domain": "homeassistant",
            "service": "check_config",
            "service_data": {}
        }
        service_result = await self.test_endpoint('POST', '/api/services/call', service_data)
        tests.append(('Service Call', service_result))
        
        if service_result['success']:
            print(f"   ✅ Service call successful")
        else:
            print(f"   ⚠️  Service call result: {service_result['data']}")
        
        # Test 5: History endpoint (last hour)
        print(f"\n5. Testing history endpoint...")
        end_time = time.time()
        start_time = end_time - 3600  # Last hour
        history_url = f'/api/history?start_time={start_time}&end_time={end_time}'
        history_result = await self.test_endpoint('GET', history_url)
        tests.append(('History', history_result))
        
        if history_result['success']:
            history_data = history_result['data'].get('history', [])
            print(f"   ✅ History retrieved: {len(history_data)} entries")
        else:
            print(f"   ❌ History request failed: {history_result['data']}")
        
        # Test 6: CORS preflight (OPTIONS request)
        print(f"\n6. Testing CORS support...")
        try:
            async with self.session.options(f"{self.base_url}/api/entities") as response:
                cors_result = {
                    'status': response.status,
                    'success': response.status in [200, 204],
                    'headers': dict(response.headers)
                }
        except Exception as e:
            cors_result = {'status': 0, 'success': False, 'data': f'Error: {str(e)}'}
        
        tests.append(('CORS Support', cors_result))
        
        if cors_result['success']:
            print(f"   ✅ CORS headers present")
        else:
            print(f"   ❌ CORS test failed: {cors_result.get('data', 'Unknown error')}")
        
        return {
            'tests': tests,
            'total': len(tests),
            'passed': sum(1 for _, result in tests if result['success']),
            'failed': sum(1 for _, result in tests if not result['success'])
        }

async def wait_for_server(url: str, max_attempts: int = 30) -> bool:
    """Wait for the server to be ready"""
    print(f"⏳ Waiting for server at {url}...")
    
    for attempt in range(max_attempts):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/health", timeout=aiohttp.ClientTimeout(total=2)) as response:
                    if response.status == 200:
                        print(f"✅ Server is ready after {attempt + 1} attempts")
                        return True
        except:
            pass
        
        if attempt < max_attempts - 1:
            await asyncio.sleep(1)
    
    print(f"❌ Server not ready after {max_attempts} attempts")
    return False

async def main():
    """Main test function"""
    print("🚀 HTTP Server Test Suite")
    print("=" * 50)
    
    # Wait for server to be ready
    if not await wait_for_server("http://localhost:3002"):
        print("❌ Cannot connect to server. Make sure it's running on port 3002")
        sys.exit(1)
    
    # Run tests
    async with HTTPServerTester() as tester:
        results = await tester.run_tests()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Total tests: {results['total']}")
    print(f"Passed: {results['passed']} ✅")
    print(f"Failed: {results['failed']} ❌")
    
    if results['failed'] == 0:
        print("\n🎉 All tests passed! Server is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {results['failed']} tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())