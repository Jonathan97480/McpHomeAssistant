# 📡 API DOCUMENTATION - HTTP-MCP BRIDGE

## 🌐 **VUE D'ENSEMBLE**

L'API HTTP-MCP Bridge expose le protocole MCP (Model Context Protocol) via des endpoints REST, permettant l'accès réseau aux serveurs MCP locaux avec gestion des files d'attente.

## 🔗 **BASE URL**
```
http://192.168.1.22:3003/mcp/
```

---

## 🛠️ **ENDPOINTS PRINCIPAUX**

### **1. Initialisation de Session**

#### `POST /mcp/initialize`
Initialise une nouvelle session MCP avec le serveur.

**Headers:**
```http
Content-Type: application/json
X-Client-ID: optionnel-client-identifier
```

**Request Body:**
```json
{
    "protocolVersion": "2024-11-05",
    "capabilities": {
        "supports_progress": true,
        "supports_cancellation": false
    },
    "clientInfo": {
        "name": "http-client",
        "version": "1.0.0"
    },
    "session_id": "custom-session-id"  // Optionnel
}
```

**Response (200 OK):**
```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
            "resources": {},
            "prompts": {}
        },
        "serverInfo": {
            "name": "homeassistant-mcp-server",
            "version": "1.0.0"
        },
        "session_id": "generated-or-custom-session-id",
        "expires_at": "2024-09-21T15:30:00Z"
    },
    "bridge_info": {
        "queue_position": 0,
        "estimated_wait_ms": 0
    }
}
```

**Errors:**
```json
// 400 Bad Request
{
    "error": {
        "code": -32602,
        "message": "Invalid protocol version",
        "data": {"supported_versions": ["2024-11-05"]}
    }
}

// 503 Service Unavailable
{
    "error": {
        "code": -32000,
        "message": "No MCP sessions available",
        "data": {"queue_size": 50, "estimated_wait_ms": 5000}
    }
}
```

---

### **2. Liste des Outils**

#### `POST /mcp/tools/list`
Récupère la liste de tous les outils disponibles.

**Headers:**
```http
Content-Type: application/json
X-Session-ID: session-id-from-initialize
X-Cache-Control: max-age=3600  // Optionnel
```

**Request Body:**
```json
{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
}
```

**Response (200 OK):**
```json
{
    "jsonrpc": "2.0",
    "id": 2,
    "result": {
        "tools": [
            {
                "name": "get_entities",
                "description": "Récupère la liste de toutes les entités Home Assistant avec leurs états",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Filtrer par domaine (optionnel): light, switch, sensor, etc."
                        }
                    }
                }
            },
            {
                "name": "call_service",
                "description": "Appelle un service Home Assistant pour contrôler des appareils",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "Domaine du service"},
                        "service": {"type": "string", "description": "Service à appeler"},
                        "entity_id": {"type": "string", "description": "ID de l'entité cible"},
                        "data": {"type": "object", "description": "Données additionnelles"}
                    },
                    "required": ["domain", "service"]
                }
            }
        ]
    },
    "bridge_info": {
        "cached": true,
        "cache_expires": "2024-09-21T15:30:00Z",
        "total_tools": 8
    }
}
```

---

### **3. Exécution d'Outils**

#### `POST /mcp/tools/call`
Exécute un outil MCP spécifique.

**Headers:**
```http
Content-Type: application/json
X-Session-ID: session-id-from-initialize
X-Priority: HIGH|MEDIUM|LOW|BULK  // Optionnel, défaut: MEDIUM
X-Timeout: 30  // Optionnel, timeout en secondes
X-Request-ID: unique-request-id  // Optionnel pour tracking
```

**Request Body:**
```json
{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "get_entities",
        "arguments": {
            "domain": "light"
        }
    }
}
```

**Response (200 OK):**
```json
{
    "jsonrpc": "2.0",
    "id": 3,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Trouvé 5 entités:\n\n{\n  \"total\": 5,\n  \"entities\": [\n    {\n      \"entity_id\": \"light.salon_lamp\",\n      \"state\": \"off\",\n      \"friendly_name\": \"Lampe Salon\",\n      \"last_updated\": \"2024-09-21T14:25:00Z\"\n    }\n  ]\n}"
            }
        ],
        "isError": false
    },
    "bridge_info": {
        "execution_time_ms": 245,
        "queue_wait_ms": 12,
        "session_id": "session-id",
        "cached": false
    }
}
```

**Exemples d'Appels:**

<details>
<summary><strong>Récupérer toutes les entités</strong></summary>

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "get_entities",
        "arguments": {"domain": "all"}
    }
}
```
</details>

<details>
<summary><strong>Contrôler une lumière</strong></summary>

```json
{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "call_service",
        "arguments": {
            "domain": "light",
            "service": "turn_on",
            "entity_id": "light.salon_lamp",
            "data": {"brightness": 180}
        }
    }
}
```
</details>

<details>
<summary><strong>Obtenir l'état d'une entité</strong></summary>

```json
{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
        "name": "get_entity_state",
        "arguments": {
            "entity_id": "sensor.temperature_salon"
        }
    }
}
```
</details>

---

## 📊 **ENDPOINTS DE MONITORING**

### **4. Statut du Bridge**

#### `GET /mcp/status`
Retourne l'état complet du bridge et de ses composants.

**Response (200 OK):**
```json
{
    "bridge": {
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": 86400,
        "started_at": "2024-09-20T14:30:00Z"
    },
    "sessions": {
        "active": 3,
        "total": 5,
        "available": 2,
        "by_status": {
            "healthy": 3,
            "reconnecting": 1,
            "idle": 1
        }
    },
    "queue": {
        "pending": 2,
        "processing": 1,
        "completed_today": 1247,
        "by_priority": {
            "HIGH": 1,
            "MEDIUM": 2,
            "LOW": 0,
            "BULK": 0
        },
        "avg_wait_time_ms": 45
    },
    "cache": {
        "hit_rate": 0.85,
        "size": 150,
        "max_size": 1000,
        "evictions_today": 10
    },
    "performance": {
        "avg_response_time_ms": 250,
        "requests_per_second": 15.5,
        "error_rate": 0.02,
        "p95_response_time_ms": 450
    },
    "home_assistant": {
        "url": "http://192.168.1.22:8123",
        "status": "connected",
        "last_ping_ms": 23,
        "entities_count": 23
    }
}
```

### **5. Health Check**

#### `GET /health`
Endpoint simple pour les health checks des load balancers.

**Response (200 OK):**
```json
{
    "status": "healthy",
    "timestamp": "2024-09-21T14:30:00Z",
    "dependencies": {
        "home_assistant": {
            "status": "ok",
            "response_time_ms": 45
        },
        "mcp_sessions": {
            "status": "ok",
            "healthy_count": 3,
            "total_count": 5
        }
    }
}
```

**Response (503 Service Unavailable):**
```json
{
    "status": "unhealthy",
    "timestamp": "2024-09-21T14:30:00Z",
    "dependencies": {
        "home_assistant": {
            "status": "error",
            "error": "Connection timeout",
            "last_success": "2024-09-21T14:25:00Z"
        },
        "mcp_sessions": {
            "status": "degraded",
            "healthy_count": 1,
            "total_count": 5
        }
    }
}
```

### **6. Métriques Prometheus**

#### `GET /metrics`
Expose les métriques au format Prometheus.

**Response (200 OK):**
```prometheus
# HELP bridge_requests_total Total number of HTTP requests
# TYPE bridge_requests_total counter
bridge_requests_total{method="POST",endpoint="/mcp/tools/call"} 1247

# HELP bridge_request_duration_seconds Request duration in seconds
# TYPE bridge_request_duration_seconds histogram
bridge_request_duration_seconds_bucket{le="0.1"} 45
bridge_request_duration_seconds_bucket{le="0.5"} 156
bridge_request_duration_seconds_bucket{le="1.0"} 234

# HELP bridge_queue_size Current queue size
# TYPE bridge_queue_size gauge
bridge_queue_size 3

# HELP bridge_active_sessions Currently active MCP sessions
# TYPE bridge_active_sessions gauge
bridge_active_sessions 5

# HELP bridge_cache_hits_total Cache hits by level
# TYPE bridge_cache_hits_total counter
bridge_cache_hits_total{level="l1"} 543
```

---

## ⚠️ **GESTION D'ERREURS**

### **Codes d'Erreur Standards**

| Code | Nom | Description |
|------|-----|-------------|
| -32700 | Parse error | JSON invalide |
| -32600 | Invalid Request | Requête JSON-RPC invalide |
| -32601 | Method not found | Méthode inconnue |
| -32602 | Invalid params | Paramètres invalides |
| -32603 | Internal error | Erreur interne du serveur |
| -32000 | Server error | Erreur spécifique au bridge |

### **Codes d'Erreur Bridge**

| Code | Description | Action Recommandée |
|------|-------------|-------------------|
| -32000 | No sessions available | Réessayer plus tard |
| -32001 | Session expired | Ré-initialiser session |
| -32002 | Queue timeout | Réduire timeout ou réessayer |
| -32003 | Rate limit exceeded | Attendre et réessayer |
| -32004 | Home Assistant unavailable | Vérifier connectivité HA |

### **Exemple de Réponse d'Erreur**
```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "error": {
        "code": -32001,
        "message": "Session expired",
        "data": {
            "session_id": "expired-session-id",
            "expired_at": "2024-09-21T14:00:00Z",
            "suggestion": "Call /mcp/initialize to create a new session"
        }
    },
    "bridge_info": {
        "timestamp": "2024-09-21T14:30:00Z",
        "request_id": "req-12345"
    }
}
```

---

## 🔧 **CONFIGURATION CLIENT**

### **Configuration LM Studio**
```json
{
    "mcpServers": {
        "homeassistant-bridge": {
            "command": "curl",
            "args": [
                "-X", "POST",
                "http://192.168.1.22:3003/mcp/tools/call",
                "-H", "Content-Type: application/json",
                "-H", "X-Session-ID: {{session_id}}",
                "-d", "{{request_body}}"
            ]
        }
    }
}
```

### **Configuration n8n**
```javascript
// Node HTTP Request dans n8n
{
    "method": "POST",
    "url": "http://192.168.1.22:3003/mcp/tools/call",
    "headers": {
        "Content-Type": "application/json",
        "X-Session-ID": "{{$node.Initialize.json.result.session_id}}",
        "X-Priority": "HIGH"
    },
    "body": {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_entities",
            "arguments": {"domain": "light"}
        }
    }
}
```

---

## 📚 **EXEMPLES D'UTILISATION**

### **Workflow Complet Python**
```python
import httpx
import json

class MCPBridgeClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session_id = None
        self.client = httpx.AsyncClient()
    
    async def initialize(self):
        """Initialise une session MCP"""
        response = await self.client.post(
            f"{self.base_url}/mcp/initialize",
            json={
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "python-client", "version": "1.0"}
            }
        )
        data = response.json()
        self.session_id = data["result"]["session_id"]
        return data
    
    async def call_tool(self, name: str, arguments: dict, priority: str = "MEDIUM"):
        """Exécute un outil MCP"""
        response = await self.client.post(
            f"{self.base_url}/mcp/tools/call",
            headers={
                "X-Session-ID": self.session_id,
                "X-Priority": priority
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments}
            }
        )
        return response.json()

# Utilisation
async def main():
    client = MCPBridgeClient("http://192.168.1.22:3003")
    
    # Initialiser
    await client.initialize()
    
    # Récupérer les entités
    entities = await client.call_tool("get_entities", {"domain": "light"})
    print(f"Trouvé {len(entities['result']['content'])} entités")
    
    # Contrôler une lumière
    result = await client.call_tool(
        "call_service",
        {
            "domain": "light",
            "service": "turn_on",
            "entity_id": "light.salon_lamp"
        },
        priority="HIGH"
    )
    print("Lumière allumée:", result["result"])
```

---

**Cette API garantit :**
- ✅ **Compatibilité JSON-RPC** : Standard MCP respecté
- ✅ **Gestion de Session** : Sessions persistantes et sécurisées
- ✅ **Files d'Attente** : Prévention des conflits simultanés
- ✅ **Monitoring Complet** : Observabilité et debugging facilités
- ✅ **Robustesse** : Gestion d'erreurs et retry automatique