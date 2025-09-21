# 🏗️ ARCHITECTURE HTTP-MCP BRIDGE AVEC QUEUE

## 📐 **VUE D'ENSEMBLE TECHNIQUE**

Le bridge HTTP-MCP transforme le protocole stdio MCP en API REST avec gestion avancée des files d'attente pour garantir la sécurité des opérations concurrentes.

## 🧩 **COMPOSANTS PRINCIPAUX**

### **1. Queue Manager**
```python
class AsyncRequestQueue:
    """
    File d'attente FIFO thread-safe pour éviter les conflits
    """
    - asyncio.Queue : File d'attente principale
    - Request deduplication : Évite les doublons
    - Priority levels : Support des priorités
    - Timeout handling : Gestion des timeouts
    - Circuit breaker : Protection overload
```

### **2. Session Pool Manager**
```python
class MCPSessionPool:
    """
    Pool de connexions MCP réutilisables
    """
    - Session lifecycle : Création/destruction automatique
    - Health monitoring : Surveillance des sessions
    - Auto-recovery : Reconnexion automatique
    - Load balancing : Répartition des requêtes
```

### **3. HTTP-MCP Bridge Core**
```python
class HTTPMCPBridge:
    """
    Cœur du bridge HTTP ↔ MCP
    """
    - JSON-RPC parsing : Conversion HTTP ↔ JSON-RPC
    - Request routing : Routage vers les handlers
    - Response formatting : Formatage des réponses
    - Error handling : Gestion d'erreurs robuste
```

---

## 🔄 **FLUX DE DONNÉES**

### **Scénario Standard**
```
1. Client HTTP → POST /mcp/tools/call
2. Request Queue ← Ajout requête en file
3. Queue Manager → Traitement FIFO
4. Session Pool → Attribution session MCP disponible
5. MCP Session ← Envoi JSON-RPC via stdio
6. Home Assistant ← Exécution commande
7. MCP Session → Réception réponse
8. HTTP Response ← Formatage et envoi au client
```

### **Scénario Concurrent - GESTION DES CONFLITS**
```
Client A → Request A → Queue [A] → Session 1 → Processing A
Client B → Request B → Queue [A,B] → Wait...
Client C → Request C → Queue [A,B,C] → Wait...

Session 1 free → Queue [B,C] → Session 1 → Processing B
Session 2 available → Queue [C] → Session 2 → Processing C
```

---

## 📊 **GESTION AVANCÉE DES FILES D'ATTENTE**

### **Stratégie Anti-Collision**
```python
class CollisionAvoidance:
    """
    Prévention des conflits de requêtes simultanées
    """
    
    # Méthode 1: Sérialisation par entité
    entity_locks = {
        "light.salon": asyncio.Lock(),
        "switch.cuisine": asyncio.Lock()
    }
    
    # Méthode 2: Queue par domaine
    domain_queues = {
        "light": AsyncQueue(),
        "switch": AsyncQueue(),
        "sensor": AsyncQueue()  # Read-only, pas de lock
    }
    
    # Méthode 3: Session dédiée par client
    client_sessions = {
        "session_id_1": MCPSession(),
        "session_id_2": MCPSession()
    }
```

### **Types de Requêtes & Priorités**
```python
class RequestPriority(Enum):
    CRITICAL = 0  # get_entity_state (monitoring critique)
    HIGH = 1      # get_entities (lecture)
    MEDIUM = 2    # call_service (écriture simple)
    LOW = 3       # create_automation (écriture complexe)
    BULK = 4      # get_history (requêtes lourdes)
    
class RequestType(Enum):
    READ_ONLY = "read"      # Pas de conflit possible
    WRITE_SAFE = "write"    # Écriture sans conflit
    WRITE_CRITICAL = "critical"  # Écriture critique (besoin lock)
```

---

## 🛡️ **SÉCURITÉ & ROBUSTESSE**

### **Protection Contre Surcharge**
```python
class OverloadProtection:
    # Rate limiting par client IP
    rate_limiter = TokenBucket(
        capacity=100,      # 100 requêtes max
        refill_rate=10     # 10 req/sec refill
    )
    
    # Circuit breaker global
    circuit_breaker = CircuitBreaker(
        failure_threshold=5,    # 5 échecs consécutifs = ouverture
        recovery_timeout=30     # 30sec avant retry
    )
    
    # Request timeout configurable
    timeouts = {
        "get_entities": 10,        # 10sec max
        "call_service": 30,        # 30sec max
        "create_automation": 60    # 60sec max
    }
```

### **Gestion d'Erreurs Avancée**
```python
class ErrorHandling:
    # Retry automatique avec backoff exponentiel
    retry_config = {
        "max_attempts": 3,
        "backoff_factor": 2,
        "retry_exceptions": [ConnectionError, TimeoutError, MCPError]
    }
    
    # Fallback responses pour haute disponibilité
    fallback_strategies = {
        "get_entities": "return_cached_or_empty",
        "get_services": "return_cached_or_minimal",
        "call_service": "fail_fast_with_reason"
    }
```

---

## 🚀 **OPTIMISATIONS PERFORMANCE**

### **Cache Strategy Multi-Niveau**
```python
class IntelligentCache:
    # Cache L1 : Mémoire ultra-rapide
    l1_cache = LRUCache(maxsize=1000, ttl=60)
    
    # Cache L2 : Redis optionnel pour cluster
    l2_cache = RedisCache(ttl=300) if REDIS_ENABLED else None
    
    # Configuration par endpoint
    cache_policies = {
        "tools/list": {
            "ttl": 3600,           # 1h - les outils changent rarement
            "level": "l1", 
            "invalidate_on": ["server_restart"]
        },
        "get_entities": {
            "ttl": 60,             # 1min - état change souvent
            "level": "l1",
            "invalidate_on": ["entity_state_change"]
        },
        "get_entity_state": {
            "ttl": 10,             # 10sec - temps réel
            "level": "l1",
            "vary_by": ["entity_id"]
        },
        "call_service": {
            "ttl": 0,              # Jamais de cache pour les actions
            "level": "none"
        }
    }
```

### **Connection Pooling Intelligent**
```python
class SmartConnectionPool:
    # Configuration adaptative
    pool_config = {
        "min_connections": 2,           # Minimum garanti
        "max_connections": 10,          # Maximum autorisé
        "target_connections": 5,        # Cible optimale
        "scale_factor": 1.5,           # Facteur d'adaptation
        "idle_timeout": 300,           # 5min timeout inactivité
        "health_check_interval": 60,   # Check santé 1min
        "auto_scale": True             # Adaptation automatique
    }
    
    # Métriques pour auto-scaling
    def should_scale_up(self) -> bool:
        return (
            self.queue_size > self.active_connections * 2 and
            self.avg_response_time > 1000  # 1sec
        )
```

---

## 📡 **API ENDPOINTS DÉTAILLÉS**

### **Core MCP Bridge**
```http
# Initialisation session
POST /mcp/initialize
Content-Type: application/json
{
    "protocolVersion": "2024-11-05",
    "capabilities": {"supports_progress": true},
    "clientInfo": {"name": "http-client", "version": "1.0"},
    "session_id": "optional-custom-id"
}
Response: {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "protocolVersion": "2024-11-05",
        "capabilities": {...},
        "serverInfo": {...},
        "session_id": "generated-or-custom-id"
    }
}

# Liste des outils avec cache
POST /mcp/tools/list
Headers: {
    "X-Session-ID": "session-id",
    "X-Cache-Control": "max-age=3600"
}
Response: {
    "tools": [...],
    "cached": true,
    "cache_expires": "2024-09-21T15:30:00Z"
}

# Exécution avec priorité
POST /mcp/tools/call
Headers: {
    "X-Session-ID": "session-id",
    "X-Priority": "HIGH",
    "X-Timeout": "30"
}
Body: {
    "name": "get_entities",
    "arguments": {"domain": "light"},
    "request_id": "unique-request-id"
}
```

### **Management & Monitoring Avancé**
```http
# Statut détaillé du bridge
GET /mcp/status
Response: {
    "bridge": {
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": 86400
    },
    "sessions": {
        "active": 3,
        "total": 5,
        "by_status": {"healthy": 3, "reconnecting": 1, "idle": 1}
    },
    "queue": {
        "pending": 2,
        "processing": 1,
        "by_priority": {"HIGH": 1, "MEDIUM": 2, "LOW": 0}
    },
    "cache": {
        "hit_rate": 0.85,
        "size": 150,
        "evictions": 10
    },
    "performance": {
        "avg_response_time_ms": 250,
        "requests_per_second": 15.5,
        "error_rate": 0.02
    }
}

# Métriques Prometheus
GET /metrics
Response: Prometheus format avec métriques custom

# Health check avec dépendances
GET /health
Response: {
    "status": "healthy",
    "timestamp": "2024-09-21T14:30:00Z",
    "dependencies": {
        "home_assistant": {"status": "ok", "response_time_ms": 45},
        "mcp_sessions": {"status": "ok", "healthy_count": 3}
    }
}
```

---

## 🔧 **CONFIGURATION AVANCÉE**

### **Configuration Complète**
```yaml
# config/bridge.yaml
bridge:
  host: "0.0.0.0"
  port: 3003
  workers: 4
  debug: false
  
queue:
  max_size: 1000
  timeout_seconds: 30
  priority_enabled: true
  deduplication_enabled: true
  max_retries: 3
  
session_pool:
  min_connections: 2
  max_connections: 10
  target_connections: 5
  auto_scale: true
  health_check_interval_seconds: 60
  idle_timeout_seconds: 300
  
cache:
  enabled: true
  default_ttl_seconds: 300
  max_size: 1000
  levels:
    l1:
      type: "memory"
      max_size: 1000
    l2:
      type: "redis"
      url: "redis://localhost:6379"
      enabled: false
      
rate_limiting:
  enabled: true
  requests_per_second: 10
  burst_capacity: 100
  
circuit_breaker:
  enabled: true
  failure_threshold: 5
  recovery_timeout_seconds: 30
  
logging:
  level: "INFO"
  format: "json"
  file: "/var/log/mcp-bridge.log"
  structured: true
  
monitoring:
  prometheus_enabled: true
  prometheus_port: 9090
  health_check_path: "/health"
```

---

## 🧪 **TESTS & QUALITÉ AVANCÉS**

### **Stratégie de Tests Complète**
```python
# Tests unitaires
tests/unit/
├── test_queue_manager.py          # File d'attente FIFO
├── test_session_pool.py           # Pool de sessions MCP
├── test_cache_manager.py          # Système de cache multi-niveau
├── test_rate_limiter.py           # Rate limiting
├── test_circuit_breaker.py        # Circuit breaker
└── test_collision_detection.py    # Détection conflits

# Tests d'intégration
tests/integration/
├── test_http_endpoints.py         # API REST complète
├── test_mcp_communication.py      # Communication MCP
├── test_concurrent_requests.py    # Requêtes simultanées
├── test_error_scenarios.py        # Scénarios d'erreur
└── test_failover.py               # Tests de basculement

# Tests de performance
tests/performance/
├── test_load_testing.py           # Tests de charge graduels
├── test_stress_testing.py         # Tests de stress extrême
├── test_memory_usage.py           # Profiling mémoire
└── test_latency_benchmarks.py     # Benchmarks latence

# Tests end-to-end
tests/e2e/
├── test_full_workflow.py          # Workflows complets
├── test_real_world_scenarios.py   # Scénarios réels
└── test_integration_lm_studio.py  # Tests avec LM Studio
```

### **Monitoring & Observabilité**
```python
# Métriques détaillées
metrics = {
    # Performance
    "request_duration_histogram": Histogram(
        "Duration of HTTP requests",
        buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
    ),
    "queue_wait_time": Histogram("Time spent waiting in queue"),
    "mcp_response_time": Histogram("MCP command response time"),
    
    # Throughput
    "requests_total": Counter("Total HTTP requests", ["method", "endpoint"]),
    "requests_per_second": Gauge("Current requests per second"),
    
    # Queue & Sessions
    "queue_size_current": Gauge("Current queue size"),
    "queue_size_max": Gauge("Maximum queue size reached"),
    "active_sessions": Gauge("Active MCP sessions"),
    "session_pool_utilization": Gauge("Session pool utilization %"),
    
    # Cache
    "cache_hits_total": Counter("Cache hits", ["level"]),
    "cache_misses_total": Counter("Cache misses", ["level"]),
    "cache_evictions_total": Counter("Cache evictions", ["reason"]),
    
    # Errors
    "errors_total": Counter("Total errors", ["type", "severity"]),
    "circuit_breaker_state": Gauge("Circuit breaker state (0=closed, 1=open)"),
    "rate_limit_exceeded_total": Counter("Rate limit exceeded events")
}
```

---

## 🚢 **DÉPLOIEMENT & PRODUCTION**

### **Container Strategy**
```dockerfile
# Dockerfile optimisé
FROM python:3.11-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 3003 9090
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:3003/health || exit 1
CMD ["python", "-m", "mcp_bridge"]
```

### **Docker Compose Stack**
```yaml
version: '3.8'
services:
  mcp-bridge:
    build: .
    ports:
      - "3003:3003"
      - "9090:9090"
    environment:
      - HASS_URL=http://homeassistant:8123
      - HASS_TOKEN=${HASS_TOKEN}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
      - homeassistant
    restart: unless-stopped
    
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
    
  prometheus:
    image: prom/prometheus
    ports:
      - "9091:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped
```

---

**Cette architecture garantit :**
- ✅ **Sécurité Maximale** : Files d'attente prévenant tous conflits
- ✅ **Performance Optimale** : Cache intelligent et pooling adaptatif
- ✅ **Robustesse Extrême** : Circuit breakers et fallbacks
- ✅ **Scalabilité Native** : Auto-scaling et load balancing
- ✅ **Observabilité Complète** : Métriques, logs et monitoring
- ✅ **Production Ready** : Containerisation et CI/CD