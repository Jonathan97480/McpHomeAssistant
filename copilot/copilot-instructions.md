# Instructions pour GitHub Copilot

## RÈGLE FONDAMENTALE
**À CHAQUE REQUÊTE DE L'UTILISATEUR, JE DOIS :**
1. **RELIRE ENTIÈREMENT** ces instructions copilot-instructions.md
2. **APPLIQUER SYSTÉMATIQUEMENT** toutes les bonnes pratiques listées ci-dessous
3. **LANCER LE SERVEUR EN MODE ADMINISTRATEUR** si nécessaire avec `Start-Process PowerShell -Verb RunAs`

## Contexte du projet
Ce projet est un serveur MCP (Model Context Protocol) pour Home Assistant qui permet de faire le pont entre des clients MCP et l'API Home Assistant.

## Architecture
- **Bridge Server** : Serveur FastAPI qui expose une API HTTP pour communiquer avec Home Assistant
- **Base de données** : SQLite pour stocker les configurations utilisateur et les tokens
- **Interface Web** : Templates HTML avec JavaScript pour la configuration
- **Authentification** : Système de gestion des utilisateurs et tokens Home Assistant

## Composants principaux
- `bridge_server.py` : Serveur principal FastAPI
- `database.py` : Gestionnaire de base de données SQLite
- `ha_config_manager.py` : Gestionnaire de configuration Home Assistant
- `web/templates/` : Interface web pour la configuration

## Corrections récentes appliquées
1. **Configuration prioritaire base de données** : Le système charge maintenant la configuration depuis la base de données en priorité
2. **Correction SQLite** : Utilisation de l'indexation tuple (result[0], result[1]) au lieu de l'accès dict
3. **Correction JavaScript DOM** : Ajout de vérifications d'existence des éléments DOM avant manipulation
4. **Déploiement Raspberry Pi** : Serveur fonctionnel sur http://192.168.1.22:8080

## Bonnes pratiques à suivre
- **Environnement virtuel** : TOUJOURS utiliser un environnement virtuel Python local au projet (`python -m venv venv`)
- **Activation environnement** : Activer l'environnement avant toute exécution (`venv\Scripts\activate` sur Windows, `source venv/bin/activate` sur Linux/Mac)
- **Installation dépendances** : Installer les dépendances dans l'environnement virtuel (`pip install -r requirements.txt`)
- **Exclusion Git** : L'environnement virtuel `venv/` est exclu du Git via .gitignore
- **Serveur en mode administrateur** : TOUJOURS lancer le serveur avec `Start-Process PowerShell -Verb RunAs` pour les privilèges élevés
- Toujours vérifier l'existence des éléments DOM avant manipulation en JavaScript
- Utiliser la base de données comme source de vérité pour les configurations
- Gérer les erreurs SQLite avec des try/catch appropriés
- Maintenir la compatibilité entre les versions locales et de production
- Pour chaque nouveau script, les mettre dans un dossier approprié (`src/`, `tests/`, `docs/`, `scripts/`)
- Documenter chaque fonctionnalité dans le dossier `docs/`
- Utiliser des variables d'environnement pour les configurations sensibles (tokens, URLs)
- Ne jamais avoir de fichiers temporaires dans le dépôt Git (utiliser `.gitignore`) ou les supprimer avant commit 
- Toujours tester les modifications localement avant de pousser vers GitHub
- Ne jamais avoir deux fonctions ou routes qui se chevauchent (ex: `/mcp/status` et `/status`)
- Toujours utiliser des messages de commit clairs et descriptifs
- Toujours valider que tous les tests passent avant de pousser
- Supprimer les fichiers temporaires et de cache avant de faire un commit (`__pycache__/`, `*.pyc`, `*.log`, `bridge_data.db`)
- Supprimer les fichiers Test temporaires avant commit (`test_temp_*.py`)
- Ne pas avoir deux fonctions qui font la même chose (ex: `insert_error()` et `log_error()`)
- Toujours utiliser les fonctions existantes au lieu d'en créer de nouvelles qui font la même chose
- Toujours vérifier les logs complets pour comprendre les erreurs avant de les corriger
- Toujours utiliser des scripts pour automatiser les tâches répétitives (transfert, déploiement, tests)
- Toujours utiliser sudo pour les commandes nécessitant des privilèges élevés ou pour lancer le serveur http en local
- on développe pour linux et windows prendre en compte les différences de chemin et de commandes
- Toujours utiliser des scripts bash pour linux/mac et powershell pour windows
- Toujours vérifier la connectivité SSH avant de lancer un transfert
- Toujours valider la complétude du projet avant transfert (fichiers critiques, dépendances)
- Toujours vérifier la structure du projet après transfert
- Toujours utiliser des scripts pour vérifier la complétude du projet avant transfert
## URLs et ports
- **Développement** : http://localhost:8080
- **Production Raspberry Pi** : http://192.168.1.22:8080
- **Home Assistant** : http://raspberrypi:8123
- **User raspberry pi** : `beroute`
- **Password raspberry pi** : `Anna97480`

## Utilisateur principal
- **Username** : beroute
- **Configuration** : Stockée en base de données avec chiffrement Base64