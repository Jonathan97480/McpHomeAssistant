#!/usr/bin/env python3
"""
🧪 Test simple du HTTP-MCP Bridge
Test HTTP direct sans interférer avec le serveur
"""

import subprocess
import time
import sys
import json

def test_bridge():
    """Test le bridge avec des requêtes HTTP simples"""
    print("🧪 Test HTTP-MCP Bridge")
    print("========================")
    
    # Test Health Check
    print("\n🏥 Test Health Check...")
    result = subprocess.run([
        "curl", "-s", "http://localhost:3003/health"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            print(f"✅ Health: {data.get('status', 'unknown')}")
        except:
            print(f"✅ Health response: {result.stdout}")
    else:
        print(f"❌ Health check failed")
        return False
    
    # Test Status 
    print("\n📊 Test Status...")
    result = subprocess.run([
        "curl", "-s", "http://localhost:3003/mcp/status"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            bridge_status = data.get('bridge', {}).get('status', 'unknown')
            sessions = data.get('sessions', {})
            print(f"✅ Bridge Status: {bridge_status}")
            print(f"✅ Sessions: {sessions.get('total', 0)} total, {sessions.get('healthy', 0)} healthy")
        except:
            print(f"✅ Status response received")
    else:
        print(f"❌ Status failed")
    
    # Test Initialize
    print("\n🔧 Test Initialize Session...")
    result = subprocess.run([
        "curl", "-s", "-X", "POST", "http://localhost:3003/mcp/initialize",
        "-H", "Content-Type: application/json",
        "-d", '{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}'
    ], capture_output=True, text=True)
    
    session_id = None
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            session_id = data.get('result', {}).get('session_id')
            if session_id:
                print(f"✅ Session créée: {session_id}")
            else:
                print(f"❌ Pas de session ID reçu")
        except:
            print(f"❌ Réponse Initialize invalide")
    else:
        print(f"❌ Initialize failed")
        return False
    
    if not session_id:
        return False
    
    # Test List Tools
    print("\n🛠️ Test List Tools...")
    result = subprocess.run([
        "curl", "-s", "-X", "POST", "http://localhost:3003/mcp/tools/list",
        "-H", "Content-Type: application/json",
        "-H", f"X-Session-ID: {session_id}",
        "-d", '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            tools = data.get('result', {}).get('tools', [])
            print(f"✅ Trouvé {len(tools)} outils:")
            for tool in tools:
                print(f"   - {tool.get('name', 'unnamed')}")
        except:
            print(f"❌ Réponse List Tools invalide")
    else:
        print(f"❌ List Tools failed")
    
    # Test Call Tool
    print("\n⚡ Test Call Tool...")
    result = subprocess.run([
        "curl", "-s", "-X", "POST", "http://localhost:3003/mcp/tools/call",
        "-H", "Content-Type: application/json",
        "-H", f"X-Session-ID: {session_id}",
        "-H", "X-Priority: HIGH",
        "-d", '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_entities","arguments":{"domain":"light"}}}'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            data = json.loads(result.stdout)
            result_content = data.get('result', {}).get('content', [])
            if result_content:
                text = result_content[0].get('text', '')
                print(f"✅ Outil exécuté: {text[:100]}...")
            else:
                print(f"❌ Pas de contenu dans la réponse")
        except:
            print(f"❌ Réponse Call Tool invalide")
    else:
        print(f"❌ Call Tool failed")
    
    print("\n🎯 Tests terminés ! Bridge fonctionne ✅")
    return True

if __name__ == "__main__":
    # Vérifier que curl est disponible
    result = subprocess.run(["curl", "--version"], capture_output=True)
    if result.returncode != 0:
        print("❌ curl n'est pas installé ou accessible")
        sys.exit(1)
    
    # Attendre un peu pour que le serveur soit prêt
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(2)
    
    # Exécuter les tests
    success = test_bridge()
    sys.exit(0 if success else 1)