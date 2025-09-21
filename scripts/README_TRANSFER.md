# 🚀 Scripts de Transfert et Migration - Phase 3.4

Ce dossier contient les scripts pour transférer et migrer le projet Phase 3.4 vers un Raspberry Pi.

## 📁 Scripts Disponibles

### 1. `transfer_complete_to_pi.sh` (Linux/macOS)
Script bash pour transférer TOUS les fichiers du projet vers le Pi.

**Utilisation :**
```bash
# Avec paramètres par défaut (192.168.1.22, utilisateur beroute)
./scripts/transfer_complete_to_pi.sh

# Avec paramètres personnalisés
./scripts/transfer_complete_to_pi.sh 192.168.1.100 pi
```

### 2. `transfer_complete_to_pi.ps1` (Windows)
Script PowerShell pour transférer TOUS les fichiers du projet vers le Pi.

**Utilisation :**
```powershell
# Avec paramètres par défaut
.\scripts\transfer_complete_to_pi.ps1

# Avec paramètres personnalisés
.\scripts\transfer_complete_to_pi.ps1 -PiIP "192.168.1.100" -PiUser "pi"
```

### 3. `check_project_completeness.py`
Vérifie que tous les fichiers nécessaires sont présents avant transfert.

**Utilisation :**
```bash
python scripts/check_project_completeness.py
```

### 4. `migrate_pi.sh`
Script de migration complète sur le Pi (à exécuter SUR le Pi).

### 5. `deploy_pi.sh`
Script de déploiement Phase 3.4 (à exécuter SUR le Pi).

## 🔄 Processus de Migration Complet

### Étape 1: Vérification Locale
```bash
# Vérifier que le projet est complet
python scripts/check_project_completeness.py
```

### Étape 2: Transfert vers Pi
```bash
# Linux/macOS
./scripts/transfer_complete_to_pi.sh 192.168.1.22 beroute

# Windows
.\scripts\transfer_complete_to_pi.ps1 -PiIP "192.168.1.22" -PiUser "beroute"
```

### Étape 3: Migration sur Pi
```bash
# Se connecter au Pi
ssh beroute@192.168.1.22

# Exécuter la migration
cd /home/beroute/homeassistant-mcp-server-v3.4
chmod +x scripts/migrate_pi.sh
./scripts/migrate_pi.sh
```

### Étape 4: Déploiement sur Pi
```bash
# Déployer Phase 3.4
chmod +x scripts/deploy_pi.sh
./scripts/deploy_pi.sh
```

## ✅ Ce qui est Transféré

### Fichiers Inclus:
- ✅ Tous les fichiers Python (*.py)
- ✅ Structure web complète (templates/, static/)
- ✅ Scripts de migration et déploiement
- ✅ Tests unitaires
- ✅ Documentation
- ✅ Configuration d'exemple (.env.example)
- ✅ Requirements.txt complet

### Fichiers Exclus:
- ❌ Cache Python (__pycache__/, *.pyc)
- ❌ Dossier .git/
- ❌ Logs (*.log, logs/)
- ❌ Configuration locale (.env)
- ❌ Base de données locale (bridge_data.db)
- ❌ Fichiers temporaires (*.tmp)
- ❌ Dossiers IDE (.vscode/, .idea/)

## 🔍 Vérifications Automatiques

Les scripts effectuent automatiquement :

1. **Pré-transfert:**
   - ✅ Complétude du projet local (27 fichiers critiques)
   - ✅ Connectivité SSH vers le Pi
   - ✅ Validation des dépendances

2. **Post-transfert:**
   - ✅ Présence des fichiers critiques sur le Pi
   - ✅ Structure web complète (8+ templates)
   - ✅ Taille et nombre de fichiers transférés

## 📊 Exemple de Sortie

```
=== Transfert Complet Phase 3.4 vers Raspberry Pi ===
🔗 Destination: beroute@192.168.1.22
📁 Projet local: /path/to/homeassistant-mcp-server
📁 Destination: /home/beroute/homeassistant-mcp-server-v3.4

🔍 1. VÉRIFICATIONS PRÉALABLES
✅ Vérification de la complétude du projet local...
✅ Connectivité OK

📦 2. PRÉPARATION DU TRANSFERT
📁 Création du répertoire de destination...

🚀 3. TRANSFERT DES FICHIERS
📂 Transfert du projet complet...
✅ Transfert terminé

🔍 4. VÉRIFICATION POST-TRANSFERT
✅ Tous les fichiers critiques sont présents
✅ Structure web complète (8 templates trouvés)

📊 5. STATISTIQUES DE TRANSFERT
📁 Taille transférée: 2.1M
📄 Nombre de fichiers: 54

🎉 TRANSFERT RÉUSSI !
```

## 🛠️ Dépannage

### Problème: Connexion SSH échoue
**Solution:** Vérifier les clés SSH et la connectivité réseau
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
ssh-copy-id beroute@192.168.1.22
```

### Problème: rsync non trouvé (Windows)
**Solution:** Le script utilise automatiquement scp comme alternative

### Problème: Fichiers manquants après transfert
**Solution:** Relancer le script, il détectera et transférera les fichiers manquants

## 🎯 Avantages des Nouveaux Scripts

1. **Complétude:** Transfère TOUS les fichiers nécessaires
2. **Sécurité:** Vérifie avant et après transfert
3. **Efficacité:** Utilise rsync pour les transferts incrémentaux
4. **Portabilité:** Scripts pour Linux/macOS ET Windows
5. **Intelligence:** Exclut automatiquement les fichiers inutiles
6. **Documentation:** Rapport détaillé des opérations

---
*Ces scripts résolvent définitivement le problème des fichiers manquants lors des migrations !*