#!/usr/bin/env python3
"""
Script de test pour le système d'authentification - Version corrigée avec emails uniques
"""

import asyncio
import aiohttp
import json
import logging
import sys
import time
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
        # Générer un timestamp unique pour les tests
        self.timestamp = int(time.time())
        self.unique_username = f"testuser_{self.timestamp}"
        self.unique_email = f"test_{self.timestamp}@example.com"
    
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
            logger.error(f"❌ Unauthorized access error: {e}")
            return False
    
    async def test_invalid_credentials(self):
        """Test avec des identifiants invalides"""
        logger.info("🚫 Testing invalid credentials...")
        
        login_data = {
            "username": "invalid_user",
            "password": "wrong_password"
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
                    data = await response.json()
                    logger.error(f"❌ Expected 401, got {response.status}: {data}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Invalid credentials error: {e}")
            return False
    
    async def test_register(self, username=None, password="TestPass123!", email=None):
        """Test d'inscription avec email unique"""
        username = username or self.unique_username
        email = email or self.unique_email
        
        logger.info(f"📝 Testing user registration: {username}")
        
        user_data = {
            "username": username,
            "password": password,
            "email": email,
            "full_name": "Test User"
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
    
    async def test_login(self, username=None, password="TestPass123!"):
        """Test de connexion"""
        username = username or self.unique_username
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
                    logger.info(f"✅ Login successful")
                    return True
                else:
                    logger.error(f"❌ Login failed ({response.status}): {data}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    async def test_user_info(self):
        """Test d'obtention des informations utilisateur"""
        logger.info("👤 Testing user info endpoint...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            async with self.session.get(
                f"{BASE_URL}/auth/me",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ User info retrieved: {data}")
                    return True
                else:
                    data = await response.json()
                    logger.error(f"❌ User info failed ({response.status}): {data}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ User info error: {e}")
            return False
    
    async def test_user_sessions(self):
        """Test d'obtention des sessions utilisateur"""
        logger.info("📋 Testing user sessions endpoint...")
        
        if not self.access_token:
            logger.error("❌ No access token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            async with self.session.get(
                f"{BASE_URL}/auth/sessions",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ User sessions retrieved: {len(data)} sessions")
                    return True
                else:
                    data = await response.json()
                    logger.error(f"❌ User sessions failed ({response.status}): {data}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ User sessions error: {e}")
            return False
    
    async def test_token_refresh(self):
        """Test de rafraîchissement du token"""
        logger.info("🔄 Testing token refresh...")
        
        if not self.refresh_token:
            logger.error("❌ No refresh token available")
            return False
        
        refresh_data = {"refresh_token": self.refresh_token}
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/refresh",
                json=refresh_data
            ) as response:
                
                data = await response.json()
                
                if response.status == 200:
                    # Mettre à jour les tokens
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    logger.info(f"✅ Token refresh successful")
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
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            async with self.session.post(
                f"{BASE_URL}/auth/logout",
                headers=headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Logout successful: {data}")
                    return True
                else:
                    data = await response.json()
                    logger.error(f"❌ Logout failed ({response.status}): {data}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Logout error: {e}")
            return False

async def run_tests():
    """Exécute tous les tests d'authentification"""
    logger.info("🧪 Starting authentication tests...")
    
    # Compteurs des résultats
    passed = 0
    failed = 0
    results = []
    
    async with AuthTester() as tester:
        
        # Test 1: Health Check
        if await tester.test_health():
            passed += 1
            results.append("✅ PASS     Health Check")
        else:
            failed += 1
            results.append("❌ FAIL     Health Check")
        
        # Test 2: Unauthorized Access
        if await tester.test_unauthorized_access():
            passed += 1
            results.append("✅ PASS     Unauthorized Access")
        else:
            failed += 1
            results.append("❌ FAIL     Unauthorized Access")
        
        # Test 3: Invalid Credentials
        if await tester.test_invalid_credentials():
            passed += 1
            results.append("✅ PASS     Invalid Credentials")
        else:
            failed += 1
            results.append("❌ FAIL     Invalid Credentials")
        
        # Test 4: Registration
        if await tester.test_register():
            passed += 1
            results.append("✅ PASS     Registration")
        else:
            failed += 1
            results.append("❌ FAIL     Registration")
        
        # Test 5: Login
        if await tester.test_login():
            passed += 1
            results.append("✅ PASS     Login")
        else:
            failed += 1
            results.append("❌ FAIL     Login")
        
        # Test 6: User Info
        if await tester.test_user_info():
            passed += 1
            results.append("✅ PASS     User Info")
        else:
            failed += 1
            results.append("❌ FAIL     User Info")
        
        # Test 7: User Sessions
        if await tester.test_user_sessions():
            passed += 1
            results.append("✅ PASS     User Sessions")
        else:
            failed += 1
            results.append("❌ FAIL     User Sessions")
        
        # Test 8: Token Refresh
        if await tester.test_token_refresh():
            passed += 1
            results.append("✅ PASS     Token Refresh")
        else:
            failed += 1
            results.append("❌ FAIL     Token Refresh")
        
        # Test 9: User Info (après refresh)
        if await tester.test_user_info():
            passed += 1
            results.append("✅ PASS     User Info (after refresh)")
        else:
            failed += 1
            results.append("❌ FAIL     User Info (after refresh)")
        
        # Test 10: Logout
        if await tester.test_logout():
            passed += 1
            results.append("✅ PASS     Logout")
        else:
            failed += 1
            results.append("❌ FAIL     Logout")
    
    # Affichage des résultats
    logger.info("")
    logger.info("==================================================")
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("==================================================")
    
    for result in results:
        logger.info(result)
    
    logger.info("==================================================")
    total = passed + failed
    percentage = (passed / total) * 100 if total > 0 else 0
    logger.info(f"📈 Results: {passed}/{total} tests passed ({percentage:.1f}%)")
    
    if failed > 0:
        logger.error(f"⚠️ {failed} tests failed")
        return False
    else:
        logger.info("🎉 All tests passed!")
        return True

if __name__ == "__main__":
    print("🧪 HTTP-MCP Bridge Authentication Test Suite")
    print("==================================================")
    print("Make sure the server is running on http://localhost:8080")
    print("==================================================")
    print()
    
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)