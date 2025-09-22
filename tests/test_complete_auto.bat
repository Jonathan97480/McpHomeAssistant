@echo off
REM 🧪 Script de Test Automatique Complet - MCP Bridge (Windows Batch)
REM Lance le serveur dans un nouveau terminal et exécute tous les tests

echo 🧪 LANCEMENT DE LA SUITE DE TESTS AUTOMATIQUE
echo ============================================================

REM Configuration
set PROJECT_ROOT=%~dp0..
set SERVER_PORT=8080
set SERVER_URL=http://localhost:%SERVER_PORT%

echo 🔄 Arrêt des serveurs existants...
REM Tuer les processus Python existants qui pourraient être des serveurs
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo table /nh 2^>nul') do (
    echo 🔪 Arrêt du processus Python: %%i
    taskkill /pid %%i /f >nul 2>&1
)

REM Tuer les processus sur le port 8080
for /f "tokens=5" %%i in ('netstat -ano ^| findstr :%SERVER_PORT%') do (
    echo 🔪 Arrêt du processus sur port %SERVER_PORT%: %%i
    taskkill /pid %%i /f >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo 🚀 Démarrage du serveur dans un nouveau terminal...
cd /d "%PROJECT_ROOT%"

REM Vérifier si l'environnement virtuel existe
if exist "venv\Scripts\activate.bat" (
    echo 🐍 Utilisation de l'environnement virtuel...
    start "MCP Bridge Server" cmd /k "venv\Scripts\activate.bat && python src/start_server.py"
) else (
    start "MCP Bridge Server" cmd /k "python src/start_server.py"
)

echo 🖥️ Serveur lancé dans un nouveau terminal
echo ⏳ Attente du démarrage du serveur...

REM Attendre que le serveur démarre (25 tentatives)
set /a attempts=0
:wait_loop
set /a attempts+=1
if %attempts% gtr 25 (
    echo ❌ Timeout: Le serveur n'a pas démarré dans les temps
    echo 💡 Le serveur continue de démarrer dans le terminal séparé
    goto run_tests
)

REM Tester la connectivité (simple avec curl ou PowerShell)
powershell -command "try { Invoke-RestMethod -Uri '%SERVER_URL%/health' -TimeoutSec 2 -ErrorAction Stop; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Serveur démarré et accessible sur %SERVER_URL%
    goto run_tests
)

echo ⏳ Attente du serveur... (%attempts%/25)
timeout /t 1 /nobreak >nul
goto wait_loop

:run_tests
echo.
echo 🎯 DÉMARRAGE DE LA SUITE DE TESTS COMPLÈTE
echo ============================================================

REM Attendre un peu pour que le serveur soit stable
timeout /t 3 /nobreak >nul

set TESTS_PASSED=0
set TESTS_FAILED=0

REM Liste des tests à exécuter
call :run_test "test_database.py" "Base de données"
call :run_test "test_auth.py" "Authentification"
call :run_test "test_cache_circuit_breaker.py" "Cache et Circuit Breaker"
call :run_test "test_ha_config.py" "Configuration Home Assistant"
call :run_test "test_permissions_simple.py" "Permissions"
call :run_test "test_web_interface.py" "Interface Web"
call :run_test "test_complete.py" "Tests Complets"

echo.
echo 📊 RÉSUMÉ DES TESTS
echo ============================================================
echo ✅ Réussis: %TESTS_PASSED%
echo ❌ Échoués: %TESTS_FAILED%

set /a TOTAL=%TESTS_PASSED%+%TESTS_FAILED%
if %TOTAL% gtr 0 (
    set /a PERCENTAGE=%TESTS_PASSED%*100/%TOTAL%
    echo 📊 Taux de réussite: !PERCENTAGE!%%
) else (
    echo 📊 Taux de réussite: 0%%
)

if %TESTS_FAILED% equ 0 (
    if %TESTS_PASSED% gtr 0 (
        echo 🎉 TOUS LES TESTS ONT RÉUSSI !
        set EXIT_CODE=0
    ) else (
        echo ⚠️ Aucun test exécuté
        set EXIT_CODE=1
    )
) else (
    echo 💥 CERTAINS TESTS ONT ÉCHOUÉ
    set EXIT_CODE=1
)

echo.
echo 🏁 Tests terminés
echo 💡 N'oubliez pas de fermer le terminal du serveur manuellement si nécessaire

exit /b %EXIT_CODE%

:run_test
set TEST_FILE=%~1
set TEST_NAME=%~2

echo.
echo 🧪 Exécution du test: %TEST_NAME%
echo ==================================================

if not exist "tests\%TEST_FILE%" (
    echo ⚠️ Test ignoré (fichier non trouvé): %TEST_FILE%
    goto :eof
)

python "tests\%TEST_FILE%"
if %errorlevel% equ 0 (
    echo ✅ Test %TEST_NAME% RÉUSSI
    set /a TESTS_PASSED+=1
) else (
    echo ❌ Test %TEST_NAME% ÉCHOUÉ (code: %errorlevel%)
    set /a TESTS_FAILED+=1
)

timeout /t 2 /nobreak >nul
goto :eof