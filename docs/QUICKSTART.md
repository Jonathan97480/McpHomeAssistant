# 🚀 Guide de démarrage rapide

## Étapes pour utiliser votre serveur MCP Home Assistant

### 1. 🔑 Créer un token Home Assistant

1. **Ouvrez votre navigateur** et allez sur : http://192.168.1.22:8123
2. **Connectez-vous** avec vos identifiants Home Assistant
3. **Cliquez sur votre profil** (icône en bas à gauche)
4. **Faites défiler** jusqu'à la section "**Tokens d'accès à long terme**"
5. **Cliquez sur "Créer un token"**
6. **Donnez-lui un nom** : `MCP Server`
7. **Copiez le token** (il ressemble à : `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`)

### 2. 📝 Configurer le serveur

Ouvrez le fichier `.env` et remplacez `your_token_here` par votre vrai token :

```env
HASS_URL=http://192.168.1.22:8123
HASS_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.votre_token_ici...
LOG_LEVEL=INFO
```

### 3. ✅ Tester la connexion

```bash
python test_connection.py
```

Si ça marche, vous verrez :
```
✅ Connexion réussie ! Trouvé XX entités
```

### 4. 🤖 Configurer Claude Desktop

#### Windows
Éditez : `%APPDATA%\Claude\claude_desktop_config.json`

#### macOS  
Éditez : `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "homeassistant-mcp-server",
      "env": {
        "HASS_URL": "http://192.168.1.22:8123",
        "HASS_TOKEN": "votre_vrai_token_ici"
      }
    }
  }
}
```

### 5. 🔄 Redémarrer Claude Desktop

Fermez complètement Claude Desktop et rouvrez-le.

### 6. 🎉 Testez avec Claude !

Demandez à Claude :

```
"Peux-tu me montrer mes lumières allumées ?"
```

```
"Éteins la lumière du salon"
```

```
"Quelle est la température dans ma maison ?"
```

## 🆘 En cas de problème

### ❌ "Token invalide"
- Vérifiez que vous avez bien copié tout le token
- Le token ne doit pas avoir expiré
- Essayez de créer un nouveau token

### ❌ "Connexion impossible"
- Vérifiez que Home Assistant est démarré sur le Raspberry Pi
- Testez l'accès depuis votre navigateur : http://192.168.1.22:8123

### ❌ "Claude ne voit pas le serveur"
- Redémarrez Claude Desktop complètement
- Vérifiez la syntaxe JSON de votre configuration
- Assurez-vous que le chemin du fichier de config est correct

## 💡 Exemples d'utilisation

Une fois configuré, voici ce que vous pouvez demander à Claude :

### 📋 Consultation
- "Montre-moi toutes mes entités"
- "Quels sont mes capteurs de température ?"
- "État de tous mes commutateurs"

### 🎮 Contrôle
- "Allume toutes les lumières"
- "Éteins la lumière de la cuisine"
- "Mets la luminosité à 50% dans le salon"

### 📊 Historique
- "Température du salon aujourd'hui"
- "Historique du capteur d'humidité"
- "Quand la porte d'entrée a-t-elle été ouverte ?"

Amusez-vous bien ! 🏠✨