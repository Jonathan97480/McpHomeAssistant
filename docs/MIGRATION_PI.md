# =============================================================================
# Guide de Migration Raspberry Pi - Phase 3.4
# =============================================================================
# Guide étape par étape pour migrer l'ancienne version vers Phase 3.4

## 📋 Vue d'ensemble

Ce guide vous accompagne pour migrer proprement de l'ancienne version 
vers la nouvelle Phase 3.4 sur votre Raspberry Pi.

## ⚠️ IMPORTANT - À lire avant de commencer

1. **Sauvegarde automatique** : Les scripts créent automatiquement une sauvegarde
2. **Arrêt des services** : Tous les anciens processus seront arrêtés
3. **Migration des données** : Vos configurations et base de données seront préservées
4. **Service systemd** : Un nouveau service sera créé pour Phase 3.4

## 🎯 Étapes de Migration

### Étape 1: Préparation sur votre ordinateur

```bash
# Rendre les scripts exécutables
chmod +x scripts/migrate_pi.sh
chmod +x scripts/deploy_pi.sh

# Transférer les scripts vers le Raspberry Pi
scp scripts/migrate_pi.sh pi@[IP_RASPBERRY]:/home/pi/
scp scripts/deploy_pi.sh pi@[IP_RASPBERRY]:/home/pi/
```

### Étape 2: Migration sur le Raspberry Pi

```bash
# Se connecter au Raspberry Pi
ssh pi@[IP_RASPBERRY]

# Exécuter la migration (arrêt + sauvegarde + nettoyage)
./migrate_pi.sh
```

**Ce que fait migrate_pi.sh :**
- ✅ Audite l'installation actuelle
- ✅ Arrête tous les services en cours
- ✅ Sauvegarde vos données importantes
- ✅ Nettoie l'ancienne installation
- ✅ Prépare l'environnement pour Phase 3.4

### Étape 3: Transfert de la nouvelle version

```bash
# Depuis votre ordinateur, transférer tous les fichiers Phase 3.4
scp -r * pi@[IP_RASPBERRY]:/home/pi/homeassistant-mcp-server-v3.4/

# Ou utiliser rsync pour un transfert plus efficace
rsync -avz --exclude='.git' --exclude='scripts' ./ pi@[IP_RASPBERRY]:/home/pi/homeassistant-mcp-server-v3.4/
```

### Étape 4: Déploiement de Phase 3.4

```bash
# Sur le Raspberry Pi, exécuter le déploiement
./deploy_pi.sh
```

**Ce que fait deploy_pi.sh :**
- ✅ Vérifie que tous les fichiers sont présents
- ✅ Installe toutes les dépendances Python
- ✅ Restaure vos configurations sauvegardées
- ✅ Configure un service systemd
- ✅ Démarre et teste la nouvelle version

## 📊 Vérification du Déploiement

### Tests automatiques après déploiement

```bash
# Vérifier le service
sudo systemctl status homeassistant-mcp-v3.4

# Tester l'API
curl http://localhost:3003/health

# Voir les logs en temps réel
sudo journalctl -u homeassistant-mcp-v3.4 -f
```

### Tests manuels

1. **Dashboard Web** : http://[IP_RASPBERRY]:3003
2. **Connexion** : admin / Admin123!
3. **API Status** : http://[IP_RASPBERRY]:3003/mcp/status

## 🔧 Gestion du Service

```bash
# Démarrer
sudo systemctl start homeassistant-mcp-v3.4

# Arrêter
sudo systemctl stop homeassistant-mcp-v3.4

# Redémarrer
sudo systemctl restart homeassistant-mcp-v3.4

# Statut
sudo systemctl status homeassistant-mcp-v3.4

# Logs
sudo journalctl -u homeassistant-mcp-v3.4 -n 50
```

## 📂 Structure après Migration

```
/home/pi/
├── homeassistant-mcp-server-v3.4/    # Nouvelle installation Phase 3.4
│   ├── bridge_server.py               # Serveur principal
│   ├── auth_manager.py               # Authentification
│   ├── venv/                         # Environnement virtuel
│   └── ...                          # Tous les fichiers Phase 3.4
├── backup-YYYYMMDD-HHMMSS/           # Sauvegarde automatique
│   ├── bridge_data.db               # Base de données sauvegardée
│   ├── config.json                  # Configurations
│   └── old_installation.tar.gz      # Archive complète
├── migrate_pi.sh                     # Script de migration
├── deploy_pi.sh                      # Script de déploiement
└── migration.log                     # Log de migration
```

## 🛟 Récupération en cas de Problème

### Restaurer l'ancienne version

```bash
# Arrêter la nouvelle version
sudo systemctl stop homeassistant-mcp-v3.4
sudo systemctl disable homeassistant-mcp-v3.4

# Restaurer depuis la sauvegarde
cd /home/pi/backup-*/
tar -xzf old_installation.tar.gz
mv homeassistant-mcp-server /home/pi/

# Redémarrer l'ancienne version manuellement
cd /home/pi/homeassistant-mcp-server
python3 bridge_server.py
```

### Diagnostics

```bash
# Vérifier les ports
sudo netstat -tlnp | grep :3003

# Vérifier les processus
ps aux | grep python

# Logs détaillés
sudo journalctl -u homeassistant-mcp-v3.4 --no-pager -n 100
```

## ✅ Checklist de Migration

- [ ] Scripts transférés sur le Pi
- [ ] Migration exécutée (migrate_pi.sh)
- [ ] Sauvegarde créée
- [ ] Ancienne version arrêtée
- [ ] Fichiers Phase 3.4 transférés
- [ ] Déploiement exécuté (deploy_pi.sh)
- [ ] Service systemd configuré
- [ ] Tests de connectivité réussis
- [ ] Dashboard accessible
- [ ] Authentification fonctionnelle

## 🎉 Avantages de Phase 3.4

Après migration, vous bénéficierez de :

- ✅ **Interface web complète** avec 9 pages responsive
- ✅ **Authentification sécurisée** JWT
- ✅ **Dashboard administrateur** moderne
- ✅ **API REST complète** documentée
- ✅ **Gestion automatique** via systemd
- ✅ **Logs centralisés** via journald
- ✅ **Tests automatisés** de validation
- ✅ **Architecture robuste** et maintenable