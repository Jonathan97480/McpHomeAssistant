#!/usr/bin/env python3
"""
🔐 Tests pour le système de permissions granulaires MCP
Tests unitaires et d'intégration pour les permissions par outil
"""

import asyncio
import pytest
import aiohttp
import json
from typing import Dict, Any, List
import time

# URL de base du serveur de test
BASE_URL = "http://localhost:8080"

class PermissionsTestSuite:
    """Suite de tests pour le système de permissions"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.user_token = None
        self.admin_user_id = None
        self.test_user_id = None
        
    async def setup_test_users(self):
        """Initialise les utilisateurs de test"""
        print("🔧 Configuration des utilisateurs de test...")
        
        async with aiohttp.ClientSession() as session:
            # Login admin par défaut
            admin_login = {
                "username": "admin",
                "password": "Admin123!"
            }
            
            try:
                async with session.post(f"{self.base_url}/auth/login", json=admin_login) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.admin_token = data['access_token']
                        print("✅ Admin connecté")
                    else:
                        print("❌ Échec connexion admin")
                        return False
            except Exception as e:
                print(f"❌ Erreur connexion admin: {e}")
                return False
            
            # Créer un utilisateur de test
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            test_user = {
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "TestPass123!"
            }
            
            try:
                async with session.post(f"{self.base_url}/auth/register", json=test_user, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.test_user_id = data['id']
                        print("✅ Utilisateur de test créé")
                    else:
                        print("❌ Échec création utilisateur de test")
                        return False
            except Exception as e:
                print(f"❌ Erreur création utilisateur: {e}")
                return False
            
            # Login utilisateur de test
            user_login = {
                "username": "testuser",
                "password": "TestPass123!"
            }
            
            try:
                async with session.post(f"{self.base_url}/auth/login", json=user_login) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.user_token = data['access_token']
                        print("✅ Utilisateur de test connecté")
                        return True
                    else:
                        print("❌ Échec connexion utilisateur de test")
                        return False
            except Exception as e:
                print(f"❌ Erreur connexion utilisateur de test: {e}")
                return False

    async def test_permission_validation(self):
        """Test de validation des permissions individuelles"""
        print("\n🔍 Test: Validation des permissions individuelles")
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test permission refusée (pas de permissions par défaut)
            permission_request = {
                "tool_name": "homeassistant.get_state",
                "permission_type": "READ"
            }
            
            async with session.post(f"{self.base_url}/permissions/validate", json=permission_request, headers=headers) as resp:
                data = await resp.json()
                if resp.status == 403:
                    print("✅ Permission correctement refusée")
                    return True
                else:
                    print(f"❌ Statut inattendu: {resp.status}, data: {data}")
                    return False

    async def test_default_permissions(self):
        """Test de gestion des permissions par défaut"""
        print("\n🔧 Test: Gestion des permissions par défaut")
        
        async with aiohttp.ClientSession() as session:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Définir une permission par défaut
            default_permission = {
                "tool_name": "homeassistant.get_state",
                "can_read": True,
                "can_write": False,
                "can_execute": False
            }
            
            async with session.put(f"{self.base_url}/permissions/defaults", json=default_permission, headers=admin_headers) as resp:
                if resp.status == 200:
                    print("✅ Permission par défaut définie")
                else:
                    data = await resp.json()
                    print(f"❌ Échec définition permission par défaut: {resp.status}, {data}")
                    return False
            
            # Vérifier que l'utilisateur hérite de la permission
            time.sleep(1)  # Laisser le temps au cache de se rafraîchir
            
            user_headers = {"Authorization": f"Bearer {self.user_token}"}
            permission_request = {
                "tool_name": "homeassistant.get_state",
                "permission_type": "READ"
            }
            
            async with session.post(f"{self.base_url}/permissions/validate", json=permission_request, headers=user_headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('granted'):
                        print("✅ Utilisateur hérite correctement de la permission par défaut")
                        return True
                    else:
                        print("❌ Permission refusée malgré héritage")
                        return False
                else:
                    data = await resp.json()
                    print(f"❌ Échec validation héritage: {resp.status}, {data}")
                    return False

    async def test_user_specific_permissions(self):
        """Test de permissions spécifiques utilisateur"""
        print("\n👤 Test: Permissions spécifiques utilisateur")
        
        async with aiohttp.ClientSession() as session:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Donner une permission spécifique à l'utilisateur
            user_permission = {
                "tool_name": "homeassistant.call_service",
                "can_read": False,
                "can_write": True,
                "can_execute": True
            }
            
            async with session.put(f"{self.base_url}/permissions/user/{self.test_user_id}", json=user_permission, headers=admin_headers) as resp:
                if resp.status == 200:
                    print("✅ Permission utilisateur définie")
                else:
                    data = await resp.json()
                    print(f"❌ Échec définition permission utilisateur: {resp.status}, {data}")
                    return False
            
            # Vérifier la permission WRITE
            time.sleep(1)
            
            user_headers = {"Authorization": f"Bearer {self.user_token}"}
            permission_request = {
                "tool_name": "homeassistant.call_service",
                "permission_type": "WRITE"
            }
            
            async with session.post(f"{self.base_url}/permissions/validate", json=permission_request, headers=user_headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('granted'):
                        print("✅ Permission utilisateur WRITE accordée")
                    else:
                        print("❌ Permission WRITE refusée")
                        return False
                else:
                    data = await resp.json()
                    print(f"❌ Échec validation permission utilisateur: {resp.status}, {data}")
                    return False
            
            # Vérifier que READ est refusée
            permission_request['permission_type'] = 'READ'
            
            async with session.post(f"{self.base_url}/permissions/validate", json=permission_request, headers=user_headers) as resp:
                if resp.status == 403:
                    print("✅ Permission utilisateur READ correctement refusée")
                    return True
                else:
                    data = await resp.json()
                    print(f"❌ Permission READ accordée à tort: {resp.status}, {data}")
                    return False

    async def test_bulk_permissions(self):
        """Test de validation en lot des permissions"""
        print("\n📦 Test: Validation en lot des permissions")
        
        async with aiohttp.ClientSession() as session:
            user_headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Test plusieurs permissions à la fois
            bulk_request = {
                "permissions": [
                    {"tool_name": "homeassistant.get_state", "permission_type": "READ"},
                    {"tool_name": "homeassistant.call_service", "permission_type": "WRITE"},
                    {"tool_name": "homeassistant.unknown_tool", "permission_type": "READ"}
                ]
            }
            
            async with session.post(f"{self.base_url}/permissions/validate/bulk", json=bulk_request, headers=user_headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get('results', [])
                    if len(results) == 2:  # unknown_tool devrait être ignoré s'il n'a pas de permissions
                        print("✅ Validation en lot réussie")
                        return True
                    else:
                        print(f"❌ Résultats inattendus: {results}")
                        return False
                elif resp.status == 403:
                    print("✅ Au moins une permission refusée en lot (comportement attendu)")
                    return True
                else:
                    data = await resp.json()
                    print(f"❌ Échec validation en lot: {resp.status}, {data}")
                    return False

    async def test_permissions_summary(self):
        """Test de résumé des permissions utilisateur"""
        print("\n📊 Test: Résumé des permissions utilisateur")
        
        async with aiohttp.ClientSession() as session:
            user_headers = {"Authorization": f"Bearer {self.user_token}"}
            
            async with session.get(f"{self.base_url}/permissions/me", headers=user_headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    summary = data.get('data', {})
                    tools = summary.get('tools', {})
                    
                    # Vérifier les outils configurés
                    expected_tools = ['homeassistant.get_state', 'homeassistant.call_service']
                    found_tools = list(tools.keys())
                    
                    if all(tool in found_tools for tool in expected_tools):
                        print("✅ Résumé des permissions correct")
                        print(f"   📋 Outils trouvés: {found_tools}")
                        return True
                    else:
                        print(f"❌ Outils manquants: attendus {expected_tools}, trouvés {found_tools}")
                        return False
                else:
                    data = await resp.json()
                    print(f"❌ Échec obtention résumé: {resp.status}, {data}")
                    return False

    async def test_admin_permissions_management(self):
        """Test de gestion des permissions par admin"""
        print("\n🔑 Test: Gestion des permissions par admin")
        
        async with aiohttp.ClientSession() as session:
            admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Consulter les permissions d'un utilisateur
            async with session.get(f"{self.base_url}/permissions/user/{self.test_user_id}", headers=admin_headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ Admin peut consulter les permissions utilisateur")
                else:
                    data = await resp.json()
                    print(f"❌ Échec consultation permissions: {resp.status}, {data}")
                    return False
            
            # Consulter les permissions par défaut
            async with session.get(f"{self.base_url}/permissions/defaults", headers=admin_headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ Admin peut consulter les permissions par défaut")
                    return True
                else:
                    data = await resp.json()
                    print(f"❌ Échec consultation permissions par défaut: {resp.status}, {data}")
                    return False

    async def run_all_tests(self):
        """Lance tous les tests de permissions"""
        print("🧪 Démarrage de la suite de tests des permissions\n")
        
        # Configuration
        if not await self.setup_test_users():
            print("❌ Échec de configuration des utilisateurs de test")
            return False
        
        # Tests
        tests = [
            ("Validation permissions individuelles", self.test_permission_validation),
            ("Permissions par défaut", self.test_default_permissions),
            ("Permissions spécifiques utilisateur", self.test_user_specific_permissions),
            ("Validation en lot", self.test_bulk_permissions),
            ("Résumé permissions", self.test_permissions_summary),
            ("Gestion admin", self.test_admin_permissions_management)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
                    print(f"✅ {test_name}: PASSÉ")
                else:
                    print(f"❌ {test_name}: ÉCHOUÉ")
            except Exception as e:
                print(f"❌ {test_name}: ERREUR - {e}")
        
        print(f"\n📊 Résultats: {passed}/{total} tests passés")
        return passed == total

async def main():
    """Fonction principale"""
    test_suite = PermissionsTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        print("🎉 Tous les tests de permissions ont réussi!")
        return 0
    else:
        print("💥 Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    import sys
    result = asyncio.run(main())
    sys.exit(result)