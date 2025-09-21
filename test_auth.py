#!/usr/bin/env python3
"""
Script de test pour le système d'authentification
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

# Configuration du serveur
BASE_URL = "http://localhost:8080"


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
                
                data = await response.json()
                
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
    
    async def test_login(self, username="testuser", password="TestPass123"):
        """Test de connexion"""
        logger.info(f"🔑 Testing user login: {username}")
        
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/login",
                json=login_data
            ) as response:
                
                data = await response.json()
                
                if response.status == 200:
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    logger.info("✅ Login successful")
                    logger.info(f"   Token type: {data.get('token_type')}")
                    logger.info(f"   Expires in: {data.get('expires_in')} seconds")
                    return True
                else:
                    logger.error(f"❌ Login failed ({response.status}): {data}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    async def test_me(self):
        """Test de récupération des infos utilisateur"""
        logger.info("👤 Testing user info endpoint...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            async with self.session.get(
                f"{BASE_URL}/auth/me",
                headers=headers
            ) as response:
                
                data = await response.json()
                
                if response.status == 200:
                    logger.info(f"✅ User info retrieved: {data}")
                    return True
                else:
                    logger.error(f"❌ User info failed ({response.status}): {data}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ User info error: {e}")
            return False
    
    async def test_sessions(self):
        """Test de récupération des sessions"""
        logger.info("📋 Testing user sessions endpoint...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            async with self.session.get(
                f"{BASE_URL}/auth/sessions",
                headers=headers
            ) as response:
                
                data = await response.json()
                
                if response.status == 200:
                    sessions = data.get("sessions", [])
                    logger.info(f"✅ Sessions retrieved: {len(sessions)} active sessions")
                    for session in sessions:
                        logger.info(f"   Session: {session.get('id')} - {session.get('ip_address')}")
                    return True
                else:
                    logger.error(f"❌ Sessions failed ({response.status}): {data}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Sessions error: {e}")
            return False
    
    async def test_refresh_token(self):
        """Test de rafraîchissement du token"""
        logger.info("🔄 Testing token refresh...")
        
        if not self.refresh_token:
            logger.error("❌ No refresh token available")
            return False
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/refresh",
                params={"refresh_token": self.refresh_token}
            ) as response:
                
                data = await response.json()
                
                if response.status == 200:
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    logger.info("✅ Token refresh successful")
                    return True
                else:
                    logger.error(f"❌ Token refresh failed ({response.status}): {data}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Token refresh error: {e}")
            return False
    
    async def test_logout(self):
        """Test de déconnexion"""
        logger.info("🚪 Testing user logout...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/logout",
                headers=headers
            ) as response:
                
                data = await response.json()
                
                if response.status == 200:
                    logger.info("✅ Logout successful")
                    self.access_token = None
                    self.refresh_token = None
                    return True
                else:
                    logger.error(f"❌ Logout failed ({response.status}): {data}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Logout error: {e}")
            return False
    
    async def test_invalid_credentials(self):
        """Test avec des identifiants invalides"""
        logger.info("🚫 Testing invalid credentials...")
        
        login_data = {
            "username": "invaliduser",
            "password": "wrongpassword"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/login",
                json=login_data
            ) as response:
                
                if response.status == 401:
                    logger.info("✅ Invalid credentials correctly rejected")
                    return True
                else:
                    logger.error(f"❌ Expected 401, got {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Invalid credentials test error: {e}")
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


async def run_auth_tests():
    """Lance tous les tests d'authentification"""
    logger.info("🧪 Starting authentication tests...")
    
    async with AuthTester() as tester:
        results = []
        
        # Test du health check
        results.append(("Health Check", await tester.test_health()))
        
        # Test d'accès non autorisé
        results.append(("Unauthorized Access", await tester.test_unauthorized_access()))
        
        # Test avec identifiants invalides
        results.append(("Invalid Credentials", await tester.test_invalid_credentials()))
        
        # Test d'inscription
        username = f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        results.append(("Registration", await tester.test_register(username=username)))
        
        # Test de connexion
        results.append(("Login", await tester.test_login(username=username)))
        
        # Test des infos utilisateur
        results.append(("User Info", await tester.test_me()))
        
        # Test des sessions
        results.append(("User Sessions", await tester.test_sessions()))
        
        # Test du refresh token
        results.append(("Token Refresh", await tester.test_refresh_token()))
        
        # Test des infos utilisateur avec nouveau token
        results.append(("User Info (after refresh)", await tester.test_me()))
        
        # Test de déconnexion
        results.append(("Logout", await tester.test_logout()))
        
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
        
        if passed == total:
            logger.info("🎉 All authentication tests passed!")
            return True
        else:
            logger.error(f"⚠️ {total-passed} tests failed")
            return False


if __name__ == "__main__":
    print("🧪 HTTP-MCP Bridge Authentication Test Suite")
    print("=" * 50)
    print("Make sure the server is running on http://localhost:8000")
    print("=" * 50)
    
    try:
        success = asyncio.run(run_auth_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)