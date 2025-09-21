# Tests - McP Bridge Phase 3.4

Ce dossier contient tous les tests pour McP Bridge avec interface web complète.

## 🧪 Types de Tests

### Tests Fonctionnels Principaux
- **`test_simple.py`** - Tests rapides de base (connectivité, santé)
- **`test_complete.py`** - Suite de tests complète 
- **`test_web_interface.py`** - Tests interface web et SPA
- **`test_bridge.py`** - Tests serveur bridge MCP

### Tests Unitaires
- **`test_auth.py`** - Tests système d'authentification JWT
- **`test_database.py`** - Tests base de données SQLite
- **`test_permissions.py`** - Tests système de permissions granulaire
- **`test_cache_circuit_breaker.py`** - Tests cache et circuit breaker

### Tests d'Intégration Home Assistant
- **`test_ha_endpoints.py`** - Tests endpoints API Home Assistant
- **`test_ha_config.py`** - Tests configuration multi-instances HA
- **`test_permissions_simple.py`** - Tests permissions simplifiés

### Tests Legacy (Compatibilité)
- **`test_connection.py`** - Test de connexion Home Assistant (legacy)
- **`test_mcp_tools.py`** - Test outils MCP (legacy)
- **`test_automations.py`** - Test automatisations (legacy)

### Scripts Utilitaires
- **`simple_test.py`** - Test simple de connectivité
- **`test_bridge.bat`** - Script batch Windows
- **`analyze_energy.py`** - Analyse capteurs énergie
- **`analyze_smart_plugs.py`** - Analyse prises connectées
- **`show_sensors.py`** - Affichage capteurs
- **`explore_automation_api.py`** - Exploration API automatisations
- **`demo_automations.py`** - Démonstrations automatisations YAML

## 🚀 Exécution des Tests

### Tests Prioritaires (Phase 3.4)
```bash
# Test rapide de l'installation
python tests/test_simple.py

# Tests complets interface web
python tests/test_complete.py

# Tests interface web détaillés
python tests/test_web_interface.py

# Tests authentification
python tests/test_auth.py
```

### Tests Système Complet
```bash
# Tous les tests dans l'ordre recommandé
python tests/test_simple.py
python tests/test_auth.py
python tests/test_database.py
python tests/test_permissions.py
python tests/test_web_interface.py
python tests/test_complete.py
```

### Tests Home Assistant (Legacy)
```bash
# Tests connexion HA (si HA disponible)
python tests/test_connection.py
python tests/test_mcp_tools.py
python tests/analyze_energy.py
```

## 📊 Couverture de Tests Phase 3.4

Les tests couvrent maintenant :
- ✅ **Interface Web Complète** (9 pages HTML)
- ✅ **API REST** (25+ endpoints)
- ✅ **Authentification JWT** sécurisée
- ✅ **Système de Permissions** granulaire
- ✅ **Base de Données** SQLite avec migrations
- ✅ **Configuration Multi-instances** Home Assistant
- ✅ **Cache et Circuit Breaker** pour la performance
- ✅ **Tests de Charge** et validation production

## ⚙️ Configuration

Assurez-vous que le fichier `.env` est configuré dans la racine du projet :

```env
HASS_URL=http://votre_ip:8123
HASS_TOKEN=votre_token_home_assistant
```

## 📊 Résultats Attendus

Les scripts d'analyse vous donneront des informations sur :
- État de vos 23 entités Home Assistant
- Consommation énergétique (capteur KWS-306WF)
- 9 prises connectées et leur état
- Automatisations YAML prêtes à utiliser