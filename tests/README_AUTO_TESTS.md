# 🧪 Scripts de Test Automatique Complet

Ces scripts lancent automatiquement le serveur MCP Bridge dans un nouveau terminal et exécutent tous les tests de validation. Le serveur reste ouvert dans son propre terminal, ce qui évite les conflits pendant l'exécution des tests.

## 📋 Scripts Disponibles

### Windows

#### PowerShell (Recommandé)
```powershell
.\tests\test_complete_auto.ps1
```

#### Batch
```cmd
.\tests\test_complete_auto.bat
```

#### Python
```cmd
python tests\test_complete_auto.py
```

### Linux/Mac

#### Bash
```bash
chmod +x tests/test_complete_auto.sh
./tests/test_complete_auto.sh
```

#### Python
```bash
python tests/test_complete_auto.py
```

## 🚀 Fonctionnalités

### Gestion Automatique du Serveur
- ✅ Arrêt des serveurs existants sur le port 8080
- ✅ Lancement du serveur dans un **nouveau terminal séparé**
- ✅ Vérification de la connectivité avant les tests
- ✅ Gestion de l'environnement virtuel automatique

### Suite de Tests Complète
- ✅ **Base de données** - `test_database.py`
- ✅ **Authentification** - `test_auth.py`
- ✅ **Cache et Circuit Breaker** - `test_cache_circuit_breaker.py`
- ✅ **Configuration Home Assistant** - `test_ha_config.py`
- ✅ **Permissions** - `test_permissions_simple.py`
- ✅ **Interface Web** - `test_web_interface.py`
- ✅ **Tests Complets** - `test_complete.py`

### Rapport Détaillé
- 📊 Résumé des tests avec statistiques
- ✅ Taux de réussite en pourcentage
- 🎯 Identification des tests échoués
- ⏱️ Exécution séquentielle avec pauses

## 🎯 Avantages

### Terminal Séparé
- Le serveur s'exécute dans son propre terminal
- Les tests ne peuvent pas accidentellement fermer le serveur
- Visibilité des logs serveur en temps réel
- Contrôle manuel possible du serveur

### Gestion Intelligente
- Détection automatique de l'environnement virtuel
- Nettoyage des processus existants
- Vérification de connectivité robuste
- Gestion d'erreurs complète

### Flexibilité
- Support Windows, Linux et Mac
- Multiples formats de scripts (PowerShell, Batch, Bash, Python)
- Paramètres configurables
- Arrêt propre en cas d'interruption

## 📝 Options PowerShell

```powershell
# Exécution standard
.\tests\test_complete_auto.ps1

# Mode verbose
.\tests\test_complete_auto.ps1 -Verbose

# Filtrer les tests
.\tests\test_complete_auto.ps1 -TestFilter "auth"
```

## 🔧 Configuration

### Variables Modifiables
- **Port du serveur** : `8080` (modifiable dans les scripts)
- **Timeout de démarrage** : `25 secondes`
- **Pause entre tests** : `2 secondes`
- **URL de santé** : `/health`

### Prérequis
- Python 3.8+
- Dépendances installées (`pip install -r requirements.txt`)
- Accès au port 8080
- Terminal graphique (pour Linux/Mac)

## 🎉 Exemple de Sortie

```
🧪 LANCEMENT DE LA SUITE DE TESTS AUTOMATIQUE
============================================================
🔄 Arrêt des serveurs existants...
✅ Serveurs existants arrêtés
🚀 Démarrage du serveur dans un nouveau terminal...
🖥️ Serveur lancé dans le terminal PID: 12345
✅ Serveur démarré et accessible sur http://localhost:8080

🎯 DÉMARRAGE DE LA SUITE DE TESTS COMPLÈTE
============================================================

🧪 Exécution du test: Base de données
==================================================
✅ Test Base de données RÉUSSI

🧪 Exécution du test: Authentification
==================================================
✅ Test Authentification RÉUSSI

[... autres tests ...]

📊 RÉSUMÉ DES TESTS
============================================================
✅ Réussis: 7
❌ Échoués: 0
📊 Taux de réussite: 100%
🎉 TOUS LES TESTS ONT RÉUSSI !

🏁 Tests terminés
💡 N'oubliez pas de fermer le terminal du serveur manuellement si nécessaire
```

## 🛠️ Dépannage

### Le serveur ne démarre pas
- Vérifiez que le port 8080 est libre
- Vérifiez les dépendances Python
- Consultez les logs dans le terminal du serveur

### Tests échouent
- Vérifiez la connectivité réseau
- Vérifiez la configuration Home Assistant
- Consultez les détails des erreurs dans la sortie

### Terminal ne s'ouvre pas (Linux)
- Installez un terminal graphique : `sudo apt install gnome-terminal`
- Ou utilisez la version Python qui fonctionne en arrière-plan

## 📚 Scripts Individuels

Pour des tests spécifiques, vous pouvez toujours utiliser :
```bash
# Tests individuels (nécessite un serveur en cours)
python tests/test_auth.py
python tests/test_database.py
# etc...
```

---

✨ **Ces scripts automatisent complètement le processus de test et garantissent un environnement propre pour chaque exécution !**