# =============================================================================
# Guide Rapide de Migration - Raspberry Pi
# =============================================================================

## 🚀 Étapes Rapides

### Prérequis
- Adresse IP de votre Raspberry Pi
- Accès SSH configuré
- PowerShell ou terminal disponible

### 1. Transférer les scripts de migration

```powershell
# Depuis Windows PowerShell
cd "c:\Users\berou\Desktop\Nouveau dossier (5)\homeassistant-mcp-server"
.\scripts\transfer_to_pi.ps1 -PiIP "VOTRE_IP_PI"
```

### 2. Se connecter au Raspberry Pi et migrer

```bash
# Se connecter au Pi
ssh pi@VOTRE_IP_PI

# Exécuter la migration
./migrate_pi.sh
```

### 3. Transférer le projet complet

```powershell
# Depuis Windows PowerShell
.\scripts\transfer_to_pi.ps1 -PiIP "VOTRE_IP_PI" -FullTransfer
```

### 4. Déployer Phase 3.4

```bash
# Sur le Raspberry Pi
./deploy_pi.sh
```

### 5. Tester l'installation

```bash
# Vérifier le service
sudo systemctl status homeassistant-mcp-v3.4

# Tester l'API
curl http://localhost:3003/health

# Accès web
# Ouvrir http://VOTRE_IP_PI:3003
# Login: admin / Admin123!
```

## 🛠️ Commandes de Diagnostic

```bash
# Logs du service
sudo journalctl -u homeassistant-mcp-v3.4 -f

# Statut du service
sudo systemctl status homeassistant-mcp-v3.4

# Redémarrer si nécessaire
sudo systemctl restart homeassistant-mcp-v3.4
```

## 📞 Support

Si vous rencontrez des problèmes :
1. Consultez les logs : `sudo journalctl -u homeassistant-mcp-v3.4 -n 50`
2. Vérifiez que le port 3003 est libre : `sudo netstat -tlnp | grep :3003`
3. Restaurez depuis la sauvegarde si nécessaire (voir MIGRATION_PI.md)