#!/usr/bin/env python3
"""
Test simple des endpoints de configuration Home Assistant
"""

import requests
import json

print('🧪 Test des endpoints de configuration Home Assistant')

# Test d'abord l'authentification pour obtenir un token
auth_data = {
    'username': 'admin',
    'password': 'Admin123!'
}

try:
    # Login
    print('🔑 Test login...')
    login_response = requests.post('http://localhost:8080/auth/login', 
                                 json=auth_data, timeout=5)
    print(f'Login: {login_response.status_code}')
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        print('✅ Authentification réussie')
        
        # Lister les configurations (devrait être vide au début)
        print('\n📋 Test liste configurations...')
        list_response = requests.get('http://localhost:8080/config/homeassistant',
                                   headers=headers, timeout=5)
        print(f'List Configs: {list_response.status_code}')
        if list_response.status_code == 200:
            configs = list_response.json()
            print(f'✅ Trouvé {len(configs.get("configs", []))} configurations')
        
        # Test de configuration HA directe (sans sauvegarder)
        print('\n🏠 Test configuration HA directe...')
        ha_test_data = {
            'name': 'Test HA Local',
            'url': 'http://localhost:8123',
            'token': 'llat_test_token_very_long_example_12345678901234567890'
        }
        
        test_response = requests.post('http://localhost:8080/config/homeassistant/test',
                                    json=ha_test_data, headers=headers, timeout=10)
        print(f'Test HA Direct: {test_response.status_code}')
        if test_response.status_code == 200:
            test_result = test_response.json()
            print(f'✅ Test completed!')
            print(f'   Success: {test_result.get("success", False)}')
            print(f'   Status: {test_result.get("status", "unknown")}')
            print(f'   Message: {test_result.get("message", "No message")}')
            if test_result.get("response_time_ms"):
                print(f'   Response time: {test_result["response_time_ms"]}ms')
        else:
            print(f'❌ Test Error: {test_response.text[:200]}...')
        
        print('\n🎯 Tests API HA terminés')
        
    else:
        print(f'❌ Login failed: {login_response.text[:100]}...')
        
except requests.exceptions.ConnectionError:
    print('❌ Serveur non accessible - Assurez-vous qu\'il tourne sur port 8080')
except Exception as e:
    print(f'❌ Test failed: {e}')