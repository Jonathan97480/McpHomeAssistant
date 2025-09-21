@echo off
echo 🧪 Test HTTP-MCP Bridge avec curl
echo ================================

echo.
echo 🏥 Test Health Check...
curl -s http://localhost:3003/health | jq .

echo.
echo 📊 Test Status...
curl -s http://localhost:3003/mcp/status | jq .bridge.status

echo.
echo 🔧 Test Initialize Session...
curl -s -X POST http://localhost:3003/mcp/initialize ^
  -H "Content-Type: application/json" ^
  -d "{\"protocolVersion\":\"2024-11-05\",\"capabilities\":{},\"clientInfo\":{\"name\":\"test\",\"version\":\"1.0\"}}" > session_response.json

echo Session créée. ID de session:
type session_response.json | jq -r .result.session_id > session_id.txt
type session_id.txt

echo.
echo 🛠️ Test List Tools...
set /p SESSION_ID=<session_id.txt
curl -s -X POST http://localhost:3003/mcp/tools/list ^
  -H "Content-Type: application/json" ^
  -H "X-Session-ID: %SESSION_ID%" ^
  -d "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\",\"params\":{}}" | jq .result.tools[].name

echo.
echo ⚡ Test Call Tool (get_entities)...
curl -s -X POST http://localhost:3003/mcp/tools/call ^
  -H "Content-Type: application/json" ^
  -H "X-Session-ID: %SESSION_ID%" ^
  -H "X-Priority: HIGH" ^
  -d "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/call\",\"params\":{\"name\":\"get_entities\",\"arguments\":{\"domain\":\"light\"}}}" | jq .result.content[0].text

echo.
echo 🎯 Tests terminés !

del session_response.json session_id.txt 2>nul