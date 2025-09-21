# Script PowerShell de déploiement des corrections d'authentification sur Pi

Write-Host "🚀 Déploiement des corrections d'authentification sur Pi..." -ForegroundColor Green

$PI_USER = "beroute"
$PI_HOST = "192.168.1.22"
$PI_PATH = "/home/beroute/phase3"

try {
    # 1. Transfert du fichier bridge_server.py corrigé
    Write-Host "📤 Transfert de bridge_server.py..." -ForegroundColor Yellow
    scp bridge_server.py "${PI_USER}@${PI_HOST}:${PI_PATH}/"
    
    # 2. Transfert du script de test
    Write-Host "📤 Transfert du script de test..." -ForegroundColor Yellow
    scp test_fix_auth.py "${PI_USER}@${PI_HOST}:${PI_PATH}/"
    
    # 3. Redémarrage du service
    Write-Host "🔄 Redémarrage du service..." -ForegroundColor Yellow
    ssh "${PI_USER}@${PI_HOST}" "sudo systemctl restart bridge-server"
    
    # 4. Attendre que le service démarre
    Write-Host "⏳ Attente du démarrage du service..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # 5. Vérification du statut
    Write-Host "🔍 Vérification du statut..." -ForegroundColor Yellow
    ssh "${PI_USER}@${PI_HOST}" "sudo systemctl status bridge-server --no-pager -l"
    
    Write-Host "✅ Déploiement terminé!" -ForegroundColor Green
    
    # 6. Test des corrections
    Write-Host "🧪 Test des corrections..." -ForegroundColor Yellow
    ssh "${PI_USER}@${PI_HOST}" "cd ${PI_PATH} && python3 test_fix_auth.py"
    
}
catch {
    Write-Host "❌ Erreur lors du déploiement: $($_.Exception.Message)" -ForegroundColor Red
}