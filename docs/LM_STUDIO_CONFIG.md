# 🤖 Configuration LM Studio pour Home Assistant MCP Server

Ce guide vous explique comment intégrer votre serveur MCP Home Assistant avec LM Studio pour contrôler vos appareils domotiques via l'IA.

## 📋 Prérequis

- LM Studio installé et configuré
- Home Assistant MCP Server déployé (en mode HTTP ou MCP)
- Token Home Assistant valide

## 🔧 Option 1: Mode HTTP (Recommandé pour LM Studio)

LM Studio peut facilement utiliser des API HTTP via des fonctions personnalisées.

### Configuration de fonction personnalisée

1. **Ouvrez LM Studio**
2. **Allez dans l'onglet "Playground"**
3. **Cliquez sur "Functions" dans la barre latérale**
4. **Ajoutez les fonctions suivantes:**

#### Fonction: Obtenir les entités Home Assistant

```json
{
  "name": "get_homeassistant_entities",
  "description": "Récupère la liste de toutes les entités Home Assistant disponibles",
  "parameters": {
    "type": "object",
    "properties": {
      "domain": {
        "type": "string",
        "description": "Filtrer par domaine (light, switch, sensor, etc.)"
      }
    }
  },
  "implementation": {
    "type": "http",
    "method": "GET",
    "url": "http://192.168.1.22:3002/api/entities",
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

#### Fonction: Contrôler les appareils

```json
{
  "name": "control_homeassistant_device",
  "description": "Contrôle un appareil Home Assistant (allumer/éteindre lumières, prises, etc.)",
  "parameters": {
    "type": "object",
    "properties": {
      "domain": {
        "type": "string",
        "description": "Le domaine du service (light, switch, etc.)",
        "required": true
      },
      "service": {
        "type": "string",
        "description": "Le service à appeler (turn_on, turn_off, toggle)",
        "required": true
      },
      "entity_id": {
        "type": "string",
        "description": "L'ID de l'entité à contrôler",
        "required": true
      },
      "data": {
        "type": "object",
        "description": "Données supplémentaires pour le service (brightness, color, etc.)"
      }
    },
    "required": ["domain", "service", "entity_id"]
  },
  "implementation": {
    "type": "http",
    "method": "POST",
    "url": "http://192.168.1.22:3002/api/services/call",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "domain": "{{domain}}",
      "service": "{{service}}",
      "service_data": {
        "entity_id": "{{entity_id}}",
        "{{#if data}}...{{data}}{{/if}}"
      }
    }
  }
}
```

#### Fonction: Obtenir l'historique

```json
{
  "name": "get_homeassistant_history",
  "description": "Récupère l'historique d'une entité Home Assistant",
  "parameters": {
    "type": "object",
    "properties": {
      "entity_id": {
        "type": "string",
        "description": "L'ID de l'entité",
        "required": true
      },
      "hours": {
        "type": "number",
        "description": "Nombre d'heures d'historique à récupérer (défaut: 24)",
        "default": 24
      }
    },
    "required": ["entity_id"]
  },
  "implementation": {
    "type": "http",
    "method": "GET",
    "url": "http://192.168.1.22:3002/api/history?entity_id={{entity_id}}&hours={{hours}}",
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

## 🔧 Option 2: Mode MCP Direct

Si LM Studio supporte les serveurs MCP (vérifiez la documentation de votre version), vous pouvez configurer directement:

### Configuration MCP

1. **Créez un fichier de configuration MCP** (`lm-studio-mcp-config.json`):

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "python",
      "args": [
        "-m", 
        "homeassistant_mcp_server.server"
      ],
      "env": {
        "HASS_URL": "http://192.168.1.22:8123",
        "HASS_TOKEN": "votre_token_ici"
      }
    }
  }
}
```

2. **Ajoutez ce fichier dans LM Studio** selon la procédure de votre version.

## 📝 Prompts d'exemple pour LM Studio

Une fois configuré, vous pouvez utiliser ces prompts avec votre modèle:

### Contrôle basique
```
Allume la lumière du salon
```

### Contrôle avec couleur
```
Mets la lumière de la chambre en bleu à 50% de luminosité
```

### Information sur les appareils
```
Montre-moi l'état de tous mes capteurs de température
```

### Historique
```
Quelle était la température de la cuisine ces 12 dernières heures ?
```

### Automations intelligentes
```
Crée une automation qui allume les lumières du salon à 19h00 tous les jours
```

## 🔧 Configuration avancée

### Variables d'environnement

Assurez-vous que votre serveur HTTP est accessible:

```bash
# Vérifiez que le serveur répond
curl http://192.168.1.22:3002/health

# Testez l'API des entités
curl http://192.168.1.22:3002/api/entities
```

### Sécurité

1. **Utilisez HTTPS en production**
2. **Limitez l'accès réseau** si nécessaire
3. **Utilisez des tokens avec permissions limitées**

### Dépannage

#### Erreur de connexion
- Vérifiez que le serveur HTTP fonctionne: `http://192.168.1.22:3002/health`
- Vérifiez que Home Assistant est accessible
- Contrôlez la validité du token

#### Erreurs de fonction
- Vérifiez la syntaxe JSON des fonctions
- Testez les endpoints avec curl avant de les ajouter à LM Studio
- Consultez les logs du serveur MCP

## 🎯 Exemples d'usage avec LM Studio

### Scénario 1: Assistant maison intelligent
Demandez à votre modèle: "Il fait nuit, peux-tu allumer les lumières principales et fermer les volets ?"

### Scénario 2: Analyse énergétique
"Analyse ma consommation électrique de la semaine dernière et donne-moi des conseils d'économie"

### Scénario 3: Automation intelligente
"Crée une automation qui ajuste automatiquement le chauffage selon la météo extérieure"

## 📚 Ressources

- [Documentation Home Assistant API](https://developers.home-assistant.io/docs/api/rest/)
- [Guide d'installation Raspberry Pi](RASPBERRY_PI_INSTALL.md)
- [Documentation MCP](https://modelcontextprotocol.io/)
- [LM Studio Documentation](https://lmstudio.ai/docs)

---

💡 **Astuce**: Commencez par tester les fonctions HTTP manuellement avec curl ou Postman avant de les configurer dans LM Studio pour vous assurer qu'elles fonctionnent correctement.