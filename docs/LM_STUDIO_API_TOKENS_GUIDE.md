# 🔑 GUIDE CONFIGURATION LM STUDIO AVEC TOKENS API PERSONNALISÉS

## 📋 Vue d'ensemble

Ce guide explique comment configurer LM Studio pour utiliser notre serveur MCP Bridge avec un système de **tokens API personnalisés** au lieu des tokens Home Assistant directs. Cette approche renforce la sécurité et permet une gestion multi-utilisateurs.

## 🔐 Avantages des tokens API personnalisés

### ✅ **Sécurité renforcée**
- Les tokens Home Assistant restent **sécurisés sur le serveur**
- Chaque utilisateur a ses **propres tokens API** 
- Révocation facile des tokens compromis
- Suivi des utilisations par token

### ✅ **Multi-utilisateurs**
- Chaque utilisateur peut avoir **sa propre configuration HA**
- Permissions granulaires par token
- Gestion centralisée des accès

### ✅ **Simplicité LM Studio**
- Configuration plus simple dans LM Studio
- Un seul token par utilisateur
- Pas besoin de gérer les tokens HA complexes

---

## 🚀 ÉTAPE 1 : Génération du token API

### Option A : Via l'interface web (Recommandé)

1. **Connectez-vous au dashboard MCP Bridge**
   ```
   http://localhost:8080/dashboard
   ```

2. **Accédez à votre profil**
   - Cliquez sur "Profil" dans le menu
   - Ou allez directement à : `http://localhost:8080/profile`

3. **Onglet "Tokens API"**
   - Cliquez sur "Générer un nouveau token"
   - Nom : `LM Studio`
   - Durée : `1 an` (365 jours)
   - Cliquez sur "Générer"

4. **Copiez le token**
   - ⚠️ **IMPORTANT** : Le token n'est affiché qu'une seule fois
   - Cliquez sur "Copier" pour le sauvegarder
   - Format : `mcp_XxxxXxxxXxxxXxxxXxxxXxxxXxxx`

### Option B : Via script (Pour développeurs)

```bash
cd "c:\Users\berou\Desktop\Nouveau dossier (5)\homeassistant-mcp-server"
python scripts/generate_api_token.py
```

---

## 🛠️ ÉTAPE 2 : Configuration LM Studio

### Configuration recommandée

Créez ou modifiez votre fichier de configuration LM Studio :

```json
{
  "mcpServers": {
    "homeassistant-bridge": {
      "name": "Home Assistant MCP Bridge Server",
      "command": "node",
      "args": ["-e", "console.log('MCP Bridge Server')"],
      "description": "Bridge HTTP vers Home Assistant avec token API personnalisé",
      "env": {
        "BRIDGE_URL": "http://localhost:8080",
        "HASS_URL": "http://raspberrypi:8123",
        "API_TOKEN": "VOTRE_TOKEN_API_ICI"
      },
      "timeout": 30,
      "autoStart": false
    }
  }
}
```

### 🔧 Paramètres de configuration

| Paramètre | Description | Valeur |
|-----------|-------------|---------|
| `BRIDGE_URL` | URL du serveur MCP Bridge | `http://localhost:8080` |
| `HASS_URL` | URL de votre Home Assistant | `http://raspberrypi:8123` |
| `API_TOKEN` | **Votre token API personnalisé** | `mcp_XxxxXxxx...` |

### ⚠️ Important : Remplacement des anciens tokens

Si vous utilisiez l'ancienne configuration avec `HASS_TOKEN`, **remplacez-la** par :
```json
"API_TOKEN": "mcp_VotreNouveauTokenAPI"
```

---

## 🧪 ÉTAPE 3 : Test de la configuration

### Test 1 : Vérification du token

1. **Ouvrez LM Studio**
2. **Testez une requête simple** :
   ```
   "Montre-moi mes entités Home Assistant"
   ```

3. **Vérifiez la réponse** :
   - Liste des entités doit s'afficher
   - Pas d'erreur d'authentification

### Test 2 : Commandes Home Assistant

```
"Quelle est ma consommation énergétique totale ?"
```

```
"Allume les lumières du salon"
```

```
"Montre-moi l'état de tous mes capteurs"
```

### 🔍 Debugging

Si vous avez des erreurs :

1. **Vérifiez les logs du serveur MCP Bridge** :
   ```
   http://localhost:8080/logs
   ```

2. **Vérifiez votre token dans le profil** :
   ```
   http://localhost:8080/profile
   ```

3. **Testez directement l'API** :
   ```bash
   curl -H "Authorization: Bearer mcp_VotreToken" http://localhost:8080/mcp/status
   ```

---

## 📊 ÉTAPE 4 : Gestion des tokens

### Interface de gestion

Dans votre profil (`http://localhost:8080/profile`), onglet "Tokens API" :

- **Voir tous vos tokens** actifs
- **Révoquer des tokens** compromis
- **Générer de nouveaux tokens**
- **Voir les statistiques d'utilisation**

### Bonnes pratiques

✅ **Nommage des tokens**
- Utilisez des noms descriptifs : "LM Studio Desktop", "LM Studio Portable"
- Un token par installation/appareil

✅ **Rotation des tokens**
- Changez vos tokens tous les 6-12 mois
- Révoquez immédiatement les tokens compromis

✅ **Surveillance**
- Vérifiez régulièrement les "dernières utilisations"
- Révoquez les tokens non utilisés

---

## 🔒 SÉCURITÉ

### Ce qui est sécurisé
- ✅ Tokens API hachés en base (SHA256)
- ✅ Tokens HA restent sur le serveur
- ✅ Expiration automatique des tokens
- ✅ Suivi des utilisations

### Ce qui reste à faire
- [ ] Rate limiting par token
- [ ] Restriction IP par token
- [ ] 2FA sur génération de tokens
- [ ] Alertes sécurité

---

## 📞 SUPPORT

### Problèmes courants

**Token invalide** :
- Vérifiez que le token commence par `mcp_`
- Vérifiez qu'il n'a pas expiré
- Générez un nouveau token si nécessaire

**Pas d'entités** :
- Vérifiez que votre config HA est correcte
- Testez la connexion HA depuis le dashboard

**Erreurs de permissions** :
- Vérifiez vos permissions dans l'onglet "Permissions"
- Contactez un administrateur si nécessaire

### Logs utiles

```bash
# Logs en temps réel
tail -f logs/bridge_2025-09-22.log

# Test d'authentification
curl -H "Authorization: Bearer mcp_VotreToken" http://localhost:8080/user/me
```

---

## 🎉 CONFIGURATION TERMINÉE !

Votre LM Studio est maintenant configuré avec un **token API personnalisé sécurisé** ! 

### Prochaines étapes :
1. ✅ Testez quelques commandes Home Assistant
2. ✅ Explorez les fonctionnalités dans le dashboard
3. ✅ Configurez d'autres appareils si nécessaire
4. ✅ Partagez cette configuration avec d'autres utilisateurs

### Ressources utiles :
- 📊 [Dashboard MCP Bridge](http://localhost:8080/dashboard)
- 👤 [Votre profil](http://localhost:8080/profile)  
- 📝 [Logs système](http://localhost:8080/logs)
- ⚙️ [Configuration HA](http://localhost:8080/config)

**Bonne utilisation ! 🚀**