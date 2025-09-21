# =============================================================================
# Script de Transfert Complet - Phase 3.4 vers Raspberry Pi (PowerShell)
# =============================================================================
# Transfère TOUS les fichiers du projet local vers le Raspberry Pi
# UTILISATION: .\transfer_complete_to_pi.ps1 [-PiIP "192.168.1.22"] [-PiUser "beroute"]
# =============================================================================

param(
    [string]$PiIP = "192.168.1.22",
    [string]$PiUser = "beroute",
    [switch]$Force = $false
)

# Configuration
$LocalProjectDir = Split-Path -Parent $PSScriptRoot
$RemoteProjectDir = "/home/$PiUser/homeassistant-mcp-server-v3.4"

Write-Host "=== Transfert Complet Phase 3.4 vers Raspberry Pi ===" -ForegroundColor Blue
Write-Host "🔗 Destination: $PiUser@$PiIP" -ForegroundColor Cyan
Write-Host "📁 Projet local: $LocalProjectDir" -ForegroundColor Cyan
Write-Host "📁 Destination: $RemoteProjectDir" -ForegroundColor Cyan
Write-Host ""

# =============================================================================
# 1. VÉRIFICATIONS PRÉALABLES
# =============================================================================
Write-Host "🔍 1. VÉRIFICATIONS PRÉALABLES" -ForegroundColor Yellow

# Vérifier le projet local
if (-not (Test-Path "$LocalProjectDir\bridge_server.py")) {
    Write-Host "❌ Ce script doit être exécuté depuis le répertoire du projet" -ForegroundColor Red
    exit 1
}

# Vérifier la complétude du projet local
Write-Host "✅ Vérification de la complétude du projet local..." -ForegroundColor Green
try {
    $result = & python "$LocalProjectDir\scripts\check_project_completeness.py"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Le projet local n'est pas complet" -ForegroundColor Red
        Write-Host "Corrigez les problèmes avant le transfert" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Projet local complet" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Impossible de vérifier la complétude (script Python non trouvé)" -ForegroundColor Yellow
}

# Test de connectivité SSH
Write-Host "🔗 Test de connectivité vers $PiUser@$PiIP..." -ForegroundColor Cyan
try {
    $null = ssh -o ConnectTimeout=10 -o BatchMode=yes "$PiUser@$PiIP" "exit" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Connexion échouée"
    }
    Write-Host "✅ Connectivité OK" -ForegroundColor Green
}
catch {
    Write-Host "❌ Impossible de se connecter au Raspberry Pi" -ForegroundColor Red
    Write-Host "Vérifiez l'IP, l'utilisateur et les clés SSH" -ForegroundColor Red
    exit 1
}

# =============================================================================
# 2. PRÉPARATION DU TRANSFERT
# =============================================================================
Write-Host ""
Write-Host "📦 2. PRÉPARATION DU TRANSFERT" -ForegroundColor Yellow

# Créer le répertoire de destination
Write-Host "📁 Création du répertoire de destination..." -ForegroundColor Cyan
ssh "$PiUser@$PiIP" "mkdir -p $RemoteProjectDir"

# =============================================================================
# 3. TRANSFERT DES FICHIERS
# =============================================================================
Write-Host ""
Write-Host "🚀 3. TRANSFERT DES FICHIERS" -ForegroundColor Yellow

# Fichiers et dossiers à exclure
$ExcludePatterns = @(
    "__pycache__/",
    ".git/",
    "*.pyc",
    ".pytest_cache/",
    "*.log",
    "logs/",
    ".env",
    "bridge_data.db",
    "*.tmp",
    ".vscode/",
    ".idea/"
)

Write-Host "📂 Transfert du projet complet..." -ForegroundColor Cyan
Write-Host "   Exclusions: $($ExcludePatterns -join ', ')" -ForegroundColor Gray

# Construire les options d'exclusion pour scp
$ExcludeOpts = ""
foreach ($pattern in $ExcludePatterns) {
    $ExcludeOpts += " --exclude='$pattern'"
}

# Utiliser rsync si disponible, sinon scp avec filtrage manuel
$HasRsync = $false
try {
    $null = Get-Command rsync -ErrorAction Stop
    $HasRsync = $true
}
catch {
    Write-Host "⚠️ rsync non trouvé, utilisation de scp" -ForegroundColor Yellow
}

if ($HasRsync) {
    # Transfert avec rsync
    $rsyncCmd = "rsync -avz --progress --delete $ExcludeOpts '$LocalProjectDir/' '$PiUser@$PiIP`:$RemoteProjectDir/'"
    Write-Host "Commande: $rsyncCmd" -ForegroundColor Gray
    Invoke-Expression $rsyncCmd
}
else {
    # Transfert avec scp (méthode alternative)
    Write-Host "📄 Transfert des fichiers critiques avec scp..." -ForegroundColor Cyan
    
    # Liste des fichiers/dossiers importants à transférer
    $ImportantItems = @(
        "*.py",
        "requirements.txt",
        ".env.example",
        "web/",
        "scripts/",
        "tests/",
        "docs/",
        "configs/",
        "README.md",
        "DEVELOPMENT_RULES.md",
        "CORRECTIFS_MIGRATION.md"
    )
    
    foreach ($item in $ImportantItems) {
        if (Test-Path "$LocalProjectDir\$item") {
            Write-Host "   Transfert: $item" -ForegroundColor Gray
            scp -r "$LocalProjectDir\$item" "$PiUser@$PiIP`:$RemoteProjectDir/"
        }
    }
}

Write-Host "✅ Transfert terminé" -ForegroundColor Green

# =============================================================================
# 4. VÉRIFICATION POST-TRANSFERT
# =============================================================================
Write-Host ""
Write-Host "🔍 4. VÉRIFICATION POST-TRANSFERT" -ForegroundColor Yellow

# Vérifier les fichiers critiques
$CriticalFiles = @(
    "bridge_server.py",
    "auth_manager.py", 
    "database.py",
    "requirements.txt",
    "web/templates/login.html",
    "web/static/css/main.css",
    "web/static/js/dashboard.js",
    "scripts/deploy_pi.sh"
)

Write-Host "📋 Vérification des fichiers critiques sur le Pi..." -ForegroundColor Cyan
$MissingFiles = @()
foreach ($file in $CriticalFiles) {
    $checkResult = ssh "$PiUser@$PiIP" "[ -f $RemoteProjectDir/$file ] && echo 'OK' || echo 'MISSING'"
    if ($checkResult -eq "MISSING") {
        $MissingFiles += $file
    }
}

if ($MissingFiles.Count -eq 0) {
    Write-Host "✅ Tous les fichiers critiques sont présents" -ForegroundColor Green
}
else {
    Write-Host "❌ Fichiers manquants:" -ForegroundColor Red
    foreach ($file in $MissingFiles) {
        Write-Host "   - $file" -ForegroundColor Red
    }
    exit 1
}

# Vérifier la structure web
Write-Host "🌐 Vérification de la structure web..." -ForegroundColor Cyan
$WebCheck = ssh "$PiUser@$PiIP" "cd $RemoteProjectDir && find web/ -name '*.html' 2>/dev/null | wc -l"
$WebCount = [int]$WebCheck

if ($WebCount -ge 8) {
    Write-Host "✅ Structure web complète ($WebCount templates trouvés)" -ForegroundColor Green
}
else {
    Write-Host "❌ Structure web incomplète (seulement $WebCount templates)" -ForegroundColor Red
    exit 1
}

# =============================================================================
# 5. STATISTIQUES DE TRANSFERT
# =============================================================================
Write-Host ""
Write-Host "📊 5. STATISTIQUES DE TRANSFERT" -ForegroundColor Yellow

# Taille du projet transféré
$RemoteSize = ssh "$PiUser@$PiIP" "du -sh $RemoteProjectDir" | ForEach-Object { $_.Split()[0] }
$RemoteFiles = ssh "$PiUser@$PiIP" "find $RemoteProjectDir -type f | wc -l"

Write-Host "📁 Taille transférée: $RemoteSize" -ForegroundColor Cyan
Write-Host "📄 Nombre de fichiers: $RemoteFiles" -ForegroundColor Cyan

# =============================================================================
# 6. INSTRUCTIONS SUIVANTES
# =============================================================================
Write-Host ""
Write-Host "🎉 TRANSFERT RÉUSSI !" -ForegroundColor Green
Write-Host ""
Write-Host "📋 ÉTAPES SUIVANTES:" -ForegroundColor Blue
Write-Host "1. Se connecter au Pi:" -ForegroundColor White
Write-Host "   ssh $PiUser@$PiIP" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Exécuter le déploiement:" -ForegroundColor White
Write-Host "   cd $RemoteProjectDir" -ForegroundColor Gray
Write-Host "   chmod +x scripts/deploy_pi.sh" -ForegroundColor Gray
Write-Host "   ./scripts/deploy_pi.sh" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Ou utiliser le script de migration complet:" -ForegroundColor White
Write-Host "   chmod +x scripts/migrate_pi.sh" -ForegroundColor Gray
Write-Host "   ./scripts/migrate_pi.sh" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 CONSEIL: Le projet est maintenant complet sur le Pi avec TOUS les fichiers" -ForegroundColor Yellow
Write-Host "   incluant la structure web/, les templates et les fichiers statiques." -ForegroundColor Yellow