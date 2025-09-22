# 🧪 Script de Test Automatique Complet - MCP Bridge
# Gestion automatique du serveur et exécution de tous les tests
# PowerShell version pour Windows

param(
    [switch]$Verbose,
    [string]$TestFilter = ""
)

# Configuration
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ServerPort = 8080
$ServerUrl = "http://localhost:$ServerPort"

Write-Host "🧪 LANCEMENT DE LA SUITE DE TESTS AUTOMATIQUE" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

function Stop-ExistingServers {
    Write-Host "🔄 Arrêt des serveurs existants..." -ForegroundColor Yellow
    
    try {
        # Arrêter les processus Python qui peuvent être des serveurs
        Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -like "*start_server*" -or $_.CommandLine -like "*bridge_server*"
        } | ForEach-Object {
            Write-Host "🔪 Arrêt du processus Python: $($_.Id)" -ForegroundColor Red
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
        
        # Vérifier les processus sur le port 8080
        $netstat = netstat -ano | Select-String ":$ServerPort "
        foreach ($line in $netstat) {
            if ($line -match "LISTENING\s+(\d+)") {
                $processId = $matches[1]
                Write-Host "🔪 Arrêt du processus sur port ${ServerPort}: $processId" -ForegroundColor Red
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            }
        }
        
        Start-Sleep -Seconds 2
        Write-Host "✅ Serveurs existants arrêtés" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Erreur lors de l'arrêt des serveurs: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

function Start-TestServer {
    Write-Host "🚀 Démarrage du serveur dans un nouveau terminal..." -ForegroundColor Yellow
    
    try {
        # Préparer la commande pour le nouveau terminal
        $venvPath = Join-Path $ProjectRoot "venv\Scripts\activate.ps1"
        
        if (Test-Path $venvPath) {
            Write-Host "🐍 Utilisation de l'environnement virtuel..." -ForegroundColor Blue
            $serverCommand = "cd '$ProjectRoot'; & '$venvPath'; python src/start_server.py; Read-Host 'Appuyez sur Entrée pour fermer'"
        }
        else {
            $serverCommand = "cd '$ProjectRoot'; python src/start_server.py; Read-Host 'Appuyez sur Entrée pour fermer'"
        }
        
        # Lancer le serveur dans un nouveau terminal PowerShell
        $serverProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", $serverCommand -PassThru
        Write-Host "🖥️ Serveur lancé dans le terminal PID: $($serverProcess.Id)" -ForegroundColor Blue
        
        # Attendre que le serveur démarre
        $maxWait = 25
        for ($i = 1; $i -le $maxWait; $i++) {
            try {
                $null = Invoke-RestMethod -Uri "$ServerUrl/health" -TimeoutSec 2 -ErrorAction Stop
                Write-Host "✅ Serveur démarré et accessible sur $ServerUrl" -ForegroundColor Green
                return $serverProcess
            }
            catch {
                # Vérifier si le processus existe encore
                if ($serverProcess.HasExited) {
                    Write-Host "❌ Le processus serveur s'est arrêté prématurément" -ForegroundColor Red
                    return $null
                }
            }
            
            Write-Host "⏳ Attente du serveur... ($i/$maxWait)" -ForegroundColor Yellow
            Start-Sleep -Seconds 1
        }
        
        Write-Host "❌ Timeout: Le serveur n'a pas démarré dans les temps" -ForegroundColor Red
        Write-Host "💡 Le serveur continue de démarrer dans le terminal séparé" -ForegroundColor Yellow
        return $serverProcess
    }
    catch {
        Write-Host "❌ Erreur de démarrage du serveur: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

function Stop-TestServer {
    param($ServerProcess)
    
    Write-Host "🛑 Arrêt du serveur..." -ForegroundColor Yellow
    
    try {
        # 1. D'abord, essayer d'arrêter le serveur proprement via l'API
        try {
            Write-Host "📡 Tentative d'arrêt propre via l'API..." -ForegroundColor Blue
            $null = Invoke-RestMethod -Uri "$ServerUrl/shutdown" -Method POST -TimeoutSec 3 -ErrorAction Stop
            Write-Host "✅ Serveur arrêté proprement via l'API" -ForegroundColor Green
            Start-Sleep -Seconds 2
        }
        catch {
            Write-Host "⚠️ Arrêt API échoué, utilisation de la méthode forcée" -ForegroundColor Yellow
        }
        
        # 2. Arrêter tous les processus Python serveurs
        Write-Host "� Arrêt des processus Python serveurs..." -ForegroundColor Blue
        Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -like "*start_server*" -or $_.CommandLine -like "*bridge_server*"
        } | ForEach-Object {
            Write-Host "   Arrêt du processus Python: $($_.Id)" -ForegroundColor Gray
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
        
        # 3. Vérifier et arrêter les processus sur le port 8080
        Write-Host "🔍 Vérification du port $ServerPort..." -ForegroundColor Blue
        $netstat = netstat -ano | Select-String ":$ServerPort "
        foreach ($line in $netstat) {
            if ($line -match "LISTENING\s+(\d+)") {
                $processId = $matches[1]
                Write-Host "   Arrêt du processus sur port ${ServerPort}: $processId" -ForegroundColor Gray
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            }
        }
        
        # 4. Arrêter le terminal PowerShell si nécessaire
        if ($ServerProcess -and -not $ServerProcess.HasExited) {
            Write-Host "🖥️ Fermeture du terminal serveur (PID: $($ServerProcess.Id))..." -ForegroundColor Blue
            $ServerProcess.Kill()
            $ServerProcess.WaitForExit(3000)  # Attendre 3 secondes
        }
        
        # 5. Vérification finale
        Start-Sleep -Seconds 1
        $remainingProcesses = netstat -ano | Select-String ":$ServerPort.*LISTENING"
        if ($remainingProcesses) {
            Write-Host "⚠️ Des processus utilisent encore le port $ServerPort" -ForegroundColor Yellow
        }
        else {
            Write-Host "✅ Port $ServerPort libéré" -ForegroundColor Green
        }
        
        Write-Host "✅ Arrêt du serveur terminé" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Erreur lors de l'arrêt: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "💡 Vérifiez manuellement qu'aucun processus n'utilise le port $ServerPort" -ForegroundColor Yellow
    }
}

function Invoke-TestFile {
    param(
        [string]$TestFile,
        [string]$TestName
    )
    
    Write-Host "🧪 Exécution du test: $TestName" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Gray
    
    try {
        $testPath = Join-Path $ProjectRoot "tests\$TestFile"
        
        if (-not (Test-Path $testPath)) {
            Write-Host "❌ Fichier de test non trouvé: $testPath" -ForegroundColor Red
            return $false
        }
        
        # Exécuter le test
        $result = & python $testPath 2>&1
        
        # Afficher la sortie
        $result | ForEach-Object { Write-Host $_ }
        
        $success = $LASTEXITCODE -eq 0
        
        if ($success) {
            Write-Host "✅ Test $TestName RÉUSSI" -ForegroundColor Green
        }
        else {
            Write-Host "❌ Test $TestName ÉCHOUÉ (code: $LASTEXITCODE)" -ForegroundColor Red
        }
        
        return $success
    }
    catch {
        Write-Host "❌ Erreur lors de l'exécution du test ${TestName}: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-AllTests {
    Write-Host "🎯 DÉMARRAGE DE LA SUITE DE TESTS COMPLÈTE" -ForegroundColor Magenta
    Write-Host "=" * 60 -ForegroundColor Gray
    
    # Liste des tests à exécuter
    $tests = @(
        @{File = "test_database.py"; Name = "Base de données" },
        @{File = "test_auth.py"; Name = "Authentification" },
        @{File = "test_cache_circuit_breaker.py"; Name = "Cache et Circuit Breaker" },
        @{File = "test_ha_config.py"; Name = "Configuration Home Assistant" },
        @{File = "test_permissions_simple.py"; Name = "Permissions" },
        @{File = "test_web_interface.py"; Name = "Interface Web" },
        @{File = "test_complete.py"; Name = "Tests Complets" }
    )
    
    $results = @{}
    
    foreach ($test in $tests) {
        # Filtrage optionnel
        if ($TestFilter -and $test.Name -notlike "*$TestFilter*") {
            continue
        }
        
        $testPath = Join-Path $ProjectRoot "tests\$($test.File)"
        if (Test-Path $testPath) {
            $success = Invoke-TestFile -TestFile $test.File -TestName $test.Name
            $results[$test.Name] = $success
            Write-Host ""  # Ligne vide pour la lisibilité
            Start-Sleep -Seconds 2  # Pause entre les tests
        }
        else {
            Write-Host "⚠️ Test ignoré (fichier non trouvé): $($test.File)" -ForegroundColor Yellow
            $results[$test.Name] = $null
        }
    }
    
    return $results
}

function Show-TestSummary {
    param($Results)
    
    Write-Host "📊 RÉSUMÉ DES TESTS" -ForegroundColor Magenta
    Write-Host "=" * 60 -ForegroundColor Gray
    
    $passed = 0
    $failed = 0
    $skipped = 0
    
    foreach ($result in $Results.GetEnumerator()) {
        $testName = $result.Key
        $testResult = $result.Value
        
        if ($testResult -eq $true) {
            Write-Host "✅ $($testName.PadRight(30)) RÉUSSI" -ForegroundColor Green
            $passed++
        }
        elseif ($testResult -eq $false) {
            Write-Host "❌ $($testName.PadRight(30)) ÉCHOUÉ" -ForegroundColor Red
            $failed++
        }
        else {
            Write-Host "⚠️ $($testName.PadRight(30)) IGNORÉ" -ForegroundColor Yellow
            $skipped++
        }
    }
    
    $total = $passed + $failed
    $percentage = if ($total -gt 0) { ($passed / $total) * 100 } else { 0 }
    
    Write-Host "=" * 60 -ForegroundColor Gray
    Write-Host "📈 RÉSULTATS FINAUX:" -ForegroundColor Magenta
    Write-Host "   ✅ Réussis: $passed" -ForegroundColor Green
    Write-Host "   ❌ Échoués: $failed" -ForegroundColor Red
    Write-Host "   ⚠️ Ignorés: $skipped" -ForegroundColor Yellow
    Write-Host "   📊 Taux de réussite: $($percentage.ToString('F1'))%" -ForegroundColor Cyan
    
    if ($failed -eq 0 -and $passed -gt 0) {
        Write-Host "🎉 TOUS LES TESTS ONT RÉUSSI !" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "💥 CERTAINS TESTS ONT ÉCHOUÉ" -ForegroundColor Red
        return $false
    }
}

# Fonction principale
try {
    # 1. Arrêter les serveurs existants
    Stop-ExistingServers
    
    # 2. Démarrer le serveur dans un nouveau terminal
    $serverProcess = Start-TestServer
    if (-not $serverProcess) {
        Write-Host "❌ Impossible de démarrer le serveur, arrêt des tests" -ForegroundColor Red
        exit 1
    }
    
    # 3. Attendre un peu pour que le serveur soit stable
    Start-Sleep -Seconds 3
    
    # 4. Lancer tous les tests
    $results = Invoke-AllTests
    
    # 5. Afficher le résumé
    $success = Show-TestSummary -Results $results
    
    exit $(if ($success) { 0 } else { 1 })
}
catch {
    Write-Host "❌ Erreur critique: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
finally {
    # 6. Arrêter le serveur
    Stop-TestServer -ServerProcess $serverProcess
    Write-Host "🏁 Tests terminés" -ForegroundColor Cyan
}