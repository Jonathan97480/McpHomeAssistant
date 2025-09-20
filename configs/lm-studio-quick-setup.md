# Configuration rapide LM Studio

## 🚀 Installation en 3 étapes

### 1. Vérifiez que votre serveur fonctionne
```bash
curl http://192.168.1.22:3002/health
```

### 2. Importez les fonctions dans LM Studio

Copiez ces fonctions dans LM Studio (Playground > Functions):

#### Fonction: Contrôler les lumières
```json
{
  "name": "controler_lumiere",
  "description": "Allume, éteint ou ajuste une lumière",
  "parameters": {
    "type": "object",
    "properties": {
      "entity_id": {
        "type": "string",
        "description": "ID de la lumière (ex: light.salon)"
      },
      "action": {
        "type": "string",
        "enum": ["turn_on", "turn_off", "toggle"]
      },
      "brightness": {
        "type": "number",
        "minimum": 0,
        "maximum": 255
      }
    },
    "required": ["entity_id", "action"]
  }
}
```

**URL**: `http://192.168.1.22:3002/api/services/call`
**Méthode**: POST
**Body**:
```json
{
  "domain": "light",
  "service": "{{action}}",
  "service_data": {
    "entity_id": "{{entity_id}}",
    "brightness": "{{brightness}}"
  }
}
```

#### Fonction: Lister les appareils
```json
{
  "name": "lister_appareils", 
  "description": "Liste tous les appareils disponibles",
  "parameters": {
    "type": "object",
    "properties": {
      "domain": {
        "type": "string",
        "description": "Type d'appareil (light, switch, sensor)"
      }
    }
  }
}
```

**URL**: `http://192.168.1.22:3002/api/entities`
**Méthode**: GET

### 3. Testez avec ces commandes

- "Allume la lumière du salon"
- "Éteins toutes les lumières" 
- "Montre-moi tous mes capteurs"
- "Règle la chambre à 50% de luminosité"

## ✅ Vérification rapide

1. Le serveur répond: ✓ `curl http://192.168.1.22:3002/health`
2. Les fonctions sont importées: ✓ 
3. LM Studio peut appeler les fonctions: ✓

🎉 **Votre assistant domotique est prêt !**