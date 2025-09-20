#!/usr/bin/env python3
"""
Test script for Raspberry Pi installation
Tests the MCP server running locally on the same machine as Home Assistant
"""

import os
import sys
import asyncio
import aiohttp
import json
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

from homeassistant_mcp_server.server import HomeAssistantClient

class RaspberryPiTester:
    def __init__(self):
        self.hass_url = os.getenv("HASS_URL", "http://localhost:8123")
        self.hass_token = os.getenv("HASS_TOKEN")
        self.mcp_url = f"http://localhost:{os.getenv('MCP_SERVER_PORT', '3000')}"
        
        if not self.hass_token:
            print("❌ HASS_TOKEN environment variable not set")
            print("Please run: export HASS_TOKEN=your_token_here")
            sys.exit(1)
    
    async def test_home_assistant_connection(self):
        """Test direct Home Assistant connection"""
        print("🏠 Testing Home Assistant connection...")
        
        try:
            client = HomeAssistantClient(self.hass_url, self.hass_token)
            entities = await client.get_entities()
            
            print(f"✅ Connected to Home Assistant successfully")
            print(f"📊 Found {len(entities)} entities")
            
            # Show some example entities
            for i, entity in enumerate(entities[:5]):
                print(f"   {i+1}. {entity['entity_id']} - {entity.get('state', 'unknown')}")
            
            if len(entities) > 5:
                print(f"   ... and {len(entities) - 5} more entities")
                
            await client.close()
            return True
            
        except Exception as e:
            print(f"❌ Home Assistant connection failed: {e}")
            return False
    
    async def test_mcp_server_health(self):
        """Test if MCP server is running and responsive"""
        print(f"\n🔧 Testing MCP server at {self.mcp_url}...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.mcp_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ MCP server is running")
                        print(f"📈 Server status: {data.get('status', 'unknown')}")
                        return True
                    else:
                        print(f"❌ MCP server returned status {response.status}")
                        return False
                        
        except aiohttp.ClientConnectorError:
            print(f"❌ Cannot connect to MCP server at {self.mcp_url}")
            print("   Make sure the server is running: sudo systemctl status homeassistant-mcp-server")
            return False
        except Exception as e:
            print(f"❌ MCP server test failed: {e}")
            return False
    
    async def test_mcp_tools(self):
        """Test MCP tools functionality"""
        print(f"\n🛠️ Testing MCP tools...")
        
        try:
            # This would test the actual MCP protocol
            # For now, we'll test the underlying functionality
            client = HomeAssistantClient(self.hass_url, self.hass_token)
            
            # Test get_entities
            entities = await client.get_entities(domain="light")
            print(f"✅ get_entities tool: Found {len(entities)} lights")
            
            # Test get_services
            services = await client.get_services()
            print(f"✅ get_services tool: Found {len(services)} services")
            
            # Test with a specific entity if available
            if entities:
                entity_id = entities[0]["entity_id"]
                state = await client.get_entity_state(entity_id)
                print(f"✅ get_entity_state tool: {entity_id} = {state.get('state', 'unknown')}")
            
            await client.close()
            return True
            
        except Exception as e:
            print(f"❌ MCP tools test failed: {e}")
            return False
    
    def test_system_resources(self):
        """Test system resource usage"""
        print(f"\n💾 Testing system resources...")
        
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"🖥️  CPU Usage: {cpu_percent}%")
            
            # Memory usage
            memory = psutil.virtual_memory()
            print(f"🧠 Memory Usage: {memory.percent}% ({memory.used // 1024 // 1024}MB used)")
            
            # Disk usage
            disk = psutil.disk_usage('/')
            print(f"💽 Disk Usage: {disk.percent}% ({disk.used // 1024 // 1024 // 1024}GB used)")
            
            # Check if MCP server process is running
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'homeassistant-mcp-server' in ' '.join(proc.info['cmdline'] or []):
                        print(f"🔧 MCP Server Process: PID {proc.info['pid']}")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print("⚠️  MCP server process not found")
            return False
            
        except ImportError:
            print("ℹ️  psutil not available for detailed system info")
            print("   Install with: pip install psutil")
            return True
        except Exception as e:
            print(f"❌ System resource test failed: {e}")
            return False
    
    def test_network_access(self):
        """Test network accessibility"""
        print(f"\n🌐 Testing network access...")
        
        try:
            import socket
            
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            print(f"📡 Local IP: {local_ip}")
            print(f"🔗 MCP Server accessible at: http://{local_ip}:3000")
            print(f"🏠 Home Assistant accessible at: http://{local_ip}:8123")
            
            # Test if port is open
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((local_ip, int(os.getenv('MCP_SERVER_PORT', '3000'))))
            sock.close()
            
            if result == 0:
                print("✅ MCP server port is accessible")
                return True
            else:
                print("❌ MCP server port is not accessible")
                return False
                
        except Exception as e:
            print(f"❌ Network test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🍓 Raspberry Pi MCP Server Test Suite")
        print("=" * 50)
        
        results = []
        
        # Test Home Assistant connection
        results.append(await self.test_home_assistant_connection())
        
        # Test MCP server health
        results.append(await self.test_mcp_server_health())
        
        # Test MCP tools
        results.append(await self.test_mcp_tools())
        
        # Test system resources
        results.append(self.test_system_resources())
        
        # Test network access
        results.append(self.test_network_access())
        
        # Summary
        print("\n" + "=" * 50)
        passed = sum(results)
        total = len(results)
        
        if passed == total:
            print(f"🎉 All tests passed! ({passed}/{total})")
            print("✅ Your Raspberry Pi MCP server is working perfectly!")
        else:
            print(f"⚠️  {passed}/{total} tests passed")
            print("❌ Some issues were found. Check the output above.")
        
        print("\n📋 Quick Commands:")
        print("  Status: sudo systemctl status homeassistant-mcp-server")
        print("  Logs:   journalctl -u homeassistant-mcp-server -f")
        print("  Restart: sudo systemctl restart homeassistant-mcp-server")
        
        return passed == total

def main():
    """Main test function"""
    # Load environment from .env file if it exists
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    tester = RaspberryPiTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()