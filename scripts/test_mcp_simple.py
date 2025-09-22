#!/usr/bin/env python3
"""
Script de test simple pour vérifier les outils MCP
"""

import requests
import json

def test_mcp_tools():
    """Test simple des outils MCP"""
    
    base_url = "http://localhost:8080"
    session = requests.Session()
    
    print("🧪 TEST SIMPLE DES OUTILS MCP")
    print("=" * 40)
    
    # 1. Se connecter
    login_data = {
        "username": "beroute",
        "password": "Anna97480"
    }
    
    auth_response = session.post(f"{base_url}/auth/login", json=login_data)
    if auth_response.status_code != 200:
        print(f"❌ Erreur de connexion: {auth_response.status_code}")
        return
    
    result = auth_response.json()
    token = result.get('access_token')
    session.headers.update({'Authorization': f'Bearer {token}'})
    print("✅ Connecté")
    
    # 2. Initialiser MCP
    mcp_init = {
        "serverName": "home-assistant",
        "client_info": {
            "name": "home-assistant-bridge",
            "version": "1.0.0"
        }
    }
    
    mcp_response = session.post(f"{base_url}/mcp/initialize", json=mcp_init)
    if mcp_response.status_code != 200:
        print(f"❌ Erreur MCP init: {mcp_response.status_code}")
        return
    
    session_id = mcp_response.json().get('result', {}).get('session_id')
    print(f"✅ Session MCP: {session_id}")
    
    # 3. Test de l'outil get_entities avec debug maximum
    print("\n🔧 Test de l'outil get_entities:")
    
    call_request = {
        "name": "get_entities",
        "params": {}
    }
    
    print(f"📤 Requête: {json.dumps(call_request, indent=2)}")
    
    response = session.post(
        f"{base_url}/mcp/tools/call",
        json=call_request,
        headers={'X-Session-ID': session_id},
        timeout=30
    )
    
    print(f"📥 Status: {response.status_code}")
    print(f"📥 Headers: {dict(response.headers)}")
    print(f"📥 Réponse complète:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_mcp_tools()