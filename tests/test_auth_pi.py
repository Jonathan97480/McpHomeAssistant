#!/usr/bin/env python3
"""
Script de test pour le système d'authentification sur Raspberry Pi
"""

import asyncio
import aiohttp
import json
import logging
import sys
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration du serveur Pi
BASE_URL = "http://192.168.1.22:8080"


class AuthTester:
    """Testeur pour l'API d'authentification"""
    
    def __init__(self):
        self.session = None
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health(self):
        """Test du health check"""
        logger.info("🏥 Testing health endpoint...")
        
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Health check OK: {data}")
                    return True
                else:
                    logger.error(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return False
    
    async def test_register(self, username="testuser", password="TestPass123", email="test@example.com"):
        """Test d'inscription"""
        logger.info(f"📝 Testing user registration: {username}")
        
        user_data = {
            "username": username,
            "password": password,
            "email": email,
            "full_name": f"Test User {username}"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/register",
                json=user_data
            ) as response:
                
                # Lire la réponse en tant que texte d'abord
                response_text = await response.text()
                logger.info(f"Registration response ({response.status}): {response_text}")
                
                try:
                    data = json.loads(response_text)
                except json.JSONDecodeError:
                    logger.error(f"❌ Invalid JSON response: {response_text}")
                    return False
                
                if response.status == 200:
                    self.user_id = data.get("id")
                    logger.info(f"✅ Registration successful: {data}")
                    return True
                else:
                    logger.error(f"❌ Registration failed ({response.status}): {data}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            return False
    
    async def test_unauthorized_access(self):
        """Test d'accès non autorisé"""
        logger.info("🛡️ Testing unauthorized access...")
        
        try:
            async with self.session.get(f"{BASE_URL}/auth/me") as response:
                
                if response.status == 401:
                    logger.info("✅ Unauthorized access correctly blocked")
                    return True
                else:
                    logger.error(f"❌ Expected 401, got {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Unauthorized access test error: {e}")
            return False


async def run_simple_auth_tests():
    """Lance quelques tests d'authentification de base"""
    logger.info("🧪 Starting simple authentication tests...")
    
    async with AuthTester() as tester:
        results = []
        
        # Test du health check
        results.append(("Health Check", await tester.test_health()))
        
        # Test d'accès non autorisé
        results.append(("Unauthorized Access", await tester.test_unauthorized_access()))
        
        # Test d'inscription
        username = f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        results.append(("Registration", await tester.test_register(username=username)))
        
        # Résumé des résultats
        logger.info("\n" + "="*50)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("="*50)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{status:10} {test_name}")
            if success:
                passed += 1
        
        logger.info("="*50)
        logger.info(f"📈 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        return passed == total


if __name__ == "__main__":
    print("🧪 HTTP-MCP Bridge Authentication Test Suite (Pi)")
    print("=" * 50)
    print("Testing against Raspberry Pi on http://192.168.1.22:8080")
    print("=" * 50)
    
    try:
        success = asyncio.run(run_simple_auth_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)