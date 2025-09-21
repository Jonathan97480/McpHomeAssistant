# =============================================================================
# Script de Transfert vers Raspberry Pi - Phase 3.4
# =============================================================================
# Ce script PowerShell facilite le transfert des fichiers vers le Raspberry Pi
# UTILISATION: .\transfer_to_pi.ps1 -PiIP "192.168.1.100"
# =============================================================================

param(
    [Parameter(Mandatory = $true)]
    [string]$PiIP,
    [string]$PiUser = "pi",
    [switch]$SkipScripts = $false,
    [switch]$FullTransfer = $false
)

# Configuration
$ProjectDir = Get-Location
$ScriptsDir = Join-Path $ProjectDir "scripts"

Write-Host "=== Transfert vers Raspberry Pi - Phase 3.4 ===" -ForegroundColor Blue
Write-Host "IP Raspberry Pi: $PiIP" -ForegroundColor Green
Write-Host "Utilisateur: $PiUser" -ForegroundColor Green
Write-Host ""

# Vérifier que pscp est disponible (PuTTY) ou utiliser scp si disponible
$scpCommand = $null
if (Get-Command pscp -ErrorAction SilentlyContinue) {
    $scpCommand = "pscp"
    Write-Host "✅ Utilisation de pscp (PuTTY)" -ForegroundColor Green
}
elseif (Get-Command scp -ErrorAction SilentlyContinue) {
    $scpCommand = "scp"
    Write-Host "✅ Utilisation de scp" -ForegroundColor Green
}
else {
    Write-Host "❌ Erreur: Ni pscp ni scp ne sont disponibles" -ForegroundColor Red
    Write-Host "Installez PuTTY ou OpenSSH pour continuer" -ForegroundColor Yellow
    exit 1
}

if (-not $SkipScripts) {
    # =============================================================================
    # 1. TRANSFERT DES SCRIPTS DE MIGRATION
    # =============================================================================
    Write-Host "📦 1. Transfert des scripts de migration..." -ForegroundColor Yellow
    
    $scriptsToTransfer = @(
        "migrate_pi.sh",
        "deploy_pi.sh"
    )
    
    foreach ($script in $scriptsToTransfer) {
        $scriptPath = Join-Path $ScriptsDir $script
        if (Test-Path $scriptPath) {
            Write-Host "📄 Transfert de $script..." -ForegroundColor Cyan
            
            if ($scpCommand -eq "pscp") {
                & pscp -batch $scriptPath "${PiUser}@${PiIP}:/home/pi/"
            }
            else {
                & scp $scriptPath "${PiUser}@${PiIP}:/home/pi/"
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ $script transféré" -ForegroundColor Green
            }
            else {
                Write-Host "   ❌ Échec du transfert de $script" -ForegroundColor Red
                exit 1
            }
        }
        else {
            Write-Host "   ⚠️  Script $script introuvable" -ForegroundColor Yellow
        }
    }
    
    # Rendre les scripts exécutables sur le Pi
    Write-Host "🔧 Rendre les scripts exécutables..." -ForegroundColor Cyan
    if (Get-Command plink -ErrorAction SilentlyContinue) {
        & plink -batch "${PiUser}@${PiIP}" "chmod +x /home/pi/migrate_pi.sh /home/pi/deploy_pi.sh"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Scripts rendus exécutables" -ForegroundColor Green
        }
    }
    else {
        Write-Host "   ⚠️  Utilisez ssh pour rendre les scripts exécutables:" -ForegroundColor Yellow
        Write-Host "   ssh ${PiUser}@${PiIP} 'chmod +x /home/pi/*.sh'" -ForegroundColor Gray
    }
}

if ($FullTransfer) {
    # =============================================================================
    # 2. TRANSFERT COMPLET DU PROJET PHASE 3.4
    # =============================================================================
    Write-Host "`n📦 2. Transfert complet du projet Phase 3.4..." -ForegroundColor Yellow
    
    # Créer le répertoire de destination sur le Pi
    Write-Host "📁 Création du répertoire de destination..." -ForegroundColor Cyan
    if (Get-Command plink -ErrorAction SilentlyContinue) {
        & plink -batch "${PiUser}@${PiIP}" "mkdir -p /home/pi/homeassistant-mcp-server-v3.4"
    }
    
    # Fichiers et dossiers à exclure du transfert
    $excludePatterns = @(
        ".git",
        "scripts",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        "node_modules"
    )
    
    # Utiliser robocopy pour préparer les fichiers (Windows)
    $tempDir = Join-Path $env:TEMP "pi_transfer"
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    New-Item -Path $tempDir -ItemType Directory | Out-Null
    
    Write-Host "📋 Préparation des fichiers..." -ForegroundColor Cyan
    robocopy $ProjectDir $tempDir /E /XD .git scripts __pycache__ .pytest_cache node_modules /XF *.pyc | Out-Null
    
    # Transfert avec scp/pscp
    Write-Host "🚀 Transfert des fichiers vers le Pi..." -ForegroundColor Cyan
    if ($scpCommand -eq "pscp") {
        & pscp -batch -r "$tempDir\*" "${PiUser}@${PiIP}:/home/pi/homeassistant-mcp-server-v3.4/"
    }
    else {
        & scp -r "$tempDir/*" "${PiUser}@${PiIP}:/home/pi/homeassistant-mcp-server-v3.4/"
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Projet Phase 3.4 transféré" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ Échec du transfert du projet" -ForegroundColor Red
    }
    
    # Nettoyage
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}

# =============================================================================
# 3. INSTRUCTIONS POUR LA SUITE
# =============================================================================
Write-Host "`n🎯 PROCHAINES ÉTAPES:" -ForegroundColor Blue

Write-Host "`n1️⃣  Se connecter au Raspberry Pi:" -ForegroundColor Yellow
Write-Host "   ssh $PiUser@$PiIP" -ForegroundColor Gray

Write-Host "`n2️⃣  Exécuter la migration:" -ForegroundColor Yellow
Write-Host "   ./migrate_pi.sh" -ForegroundColor Gray
Write-Host "   (Ceci va arrêter l'ancienne version et sauvegarder les données)" -ForegroundColor Cyan

if (-not $FullTransfer) {
    Write-Host "`n3️⃣  Transférer le projet complet:" -ForegroundColor Yellow
    Write-Host "   Depuis ce PC, exécutez:" -ForegroundColor Cyan
    Write-Host "   .\transfer_to_pi.ps1 -PiIP $PiIP -FullTransfer" -ForegroundColor Gray
}

Write-Host "`n4️⃣  Déployer Phase 3.4:" -ForegroundColor Yellow
Write-Host "   ./deploy_pi.sh" -ForegroundColor Gray
Write-Host "   (Ceci va installer et configurer la nouvelle version)" -ForegroundColor Cyan

Write-Host "`n5️⃣  Tester l'installation:" -ForegroundColor Yellow
Write-Host "   curl http://localhost:3003/health" -ForegroundColor Gray
Write-Host "   Ou ouvrir: http://$PiIP:3003" -ForegroundColor Cyan

Write-Host "`n✅ Scripts transférés avec succès!" -ForegroundColor Green
Write-Host "📚 Consultez docs\MIGRATION_PI.md pour plus de détails" -ForegroundColor Blue