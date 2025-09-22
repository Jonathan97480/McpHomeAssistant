# Configuration LM Studio pour Home Assistant MCP Bridge

## 📋 Configuration Functions pour LM Studio

Voici la configuration des fonctions à utiliser dans LM Studio pour communiquer avec votre serveur MCP Bridge Home Assistant.

### 🔧 Configuration générale

- **Serveur**: http://localhost:8080
- **Utilisateur**: beroute
- **Mot de passe**: Anna97480
- **Home Assistant**: http://raspberrypi:8123

### 📱 Fonctions disponibles

#### 1. Récupérer les entités Home Assistant

**Nom**: `get_homeassistant_entities`
**Description**: Récupère toutes les entités de votre installation Home Assistant
**Méthode**: POST
**URL**: `http://localhost:8080/mcp/tools/call`
**Headers**:
```json
{
  "Content-Type": "application/json",
  "X-Session-ID": "session-lm-studio"
}
```
**Body**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_entities",
    "arguments": {
      "format": "json"
    }
  }
}
```

#### 2. Obtenir l'état d'une entité spécifique

**Nom**: `get_entity_state`
**Description**: Récupère l'état détaillé d'une entité
**Méthode**: POST
**URL**: `http://localhost:8080/mcp/tools/call`
**Headers**:
```json
{
  "Content-Type": "application/json",
  "X-Session-ID": "session-lm-studio"
}
```
**Body**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_state",
    "arguments": {
      "entity_id": "{{entity_id}}"
    }
  }
}
```

#### 3. Contrôler un service Home Assistant

**Nom**: `call_homeassistant_service`
**Description**: Appelle un service Home Assistant (allumer lumière, etc.)
**Méthode**: POST
**URL**: `http://localhost:8080/mcp/tools/call`
**Headers**:
```json
{
  "Content-Type": "application/json",
  "X-Session-ID": "session-lm-studio"
}
```
**Body**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "call_service",
    "arguments": {
      "domain": "{{domain}}",
      "service": "{{service}}",
      "entity_id": "{{entity_id}}",
      "data": {{service_data}}
    }
  }
}
```

### 🔄 Configuration des fonctions dans LM Studio

1. **Ouvrez LM Studio**
2. **Allez dans Playground > Functions**
3. **Ajoutez ces 3 fonctions** avec les paramètres ci-dessus
4. **Testez avec votre modèle**

### 📋 Paramètres des fonctions pour LM Studio

#### Fonction 1: Récupérer les entités
```json
{
  "name": "get_homeassistant_entities",
  "description": "Récupère toutes les entités Home Assistant disponibles",
  "parameters": {
    "type": "object",
    "properties": {
      "domain": {
        "type": "string",
        "description": "Filtrer par domaine (optionnel): light, switch, sensor, etc."
      }
    }
  }
}
```

#### Fonction 2: État d'une entité
```json
{
  "name": "get_entity_state", 
  "description": "Récupère l'état d'une entité spécifique",
  "parameters": {
    "type": "object",
    "properties": {
      "entity_id": {
        "type": "string",
        "description": "ID de l'entité (ex: sensor.kws_306wf_energie_totale)"
      }
    },
    "required": ["entity_id"]
  }
}
```

#### Fonction 3: Contrôler un service
```json
{
  "name": "call_homeassistant_service",
  "description": "Contrôle un service Home Assistant",
  "parameters": {
    "type": "object", 
    "properties": {
      "domain": {
        "type": "string",
        "description": "Domaine du service (light, switch, etc.)"
      },
      "service": {
        "type": "string", 
        "description": "Service à appeler (turn_on, turn_off, toggle)"
      },
      "entity_id": {
        "type": "string",
        "description": "ID de l'entité à contrôler"
      },
      "service_data": {
        "type": "object",
        "description": "Données supplémentaires pour le service"
      }
    },
    "required": ["domain", "service"]
  }
}
```

### ✅ Test de fonctionnement

Pour tester, demandez à votre IA dans LM Studio :
- "Peux-tu me montrer toutes les entités de ma maison ?"
- "Quelle est la consommation électrique totale ?"
- "Allume la lumière du salon"
- "Éteins la prise de l'ampli"

### 🔧 Entités principales disponibles

- **Énergie totale**: `sensor.kws_306wf_energie_totale` (708.48 kWh)
- **Prises intelligentes**: 
  - `switch.ampli_home_cinema_et_lecteur_blu_ray_prise`
  - `switch.bureau_prise_1`
  - `switch.frigidaire_micro_ondes_prise_1`
  - `switch.plaque_electrique_prise_1`
  - `switch.congelateur_prise_1`
- **Media Players**: `media_player.salle_cinema`
- **Personne**: `person.jonathan_gauvin`