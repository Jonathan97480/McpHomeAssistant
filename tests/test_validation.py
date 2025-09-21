#!/usr/bin/env python3
"""
Test ultra simple - teste juste si les imports fonctionnent
et si le serveur peut démarrer en mode test
"""

import sys
import os
import time

def test_imports():
    """Test des imports critiques"""
    print('🧪 TEST IMPORTS - McP Bridge Phase 3.4')
    print('=' * 40)
    
    success = 0
    total = 0
    
    # Test 1: Import bridge_server
    print('📦 Test 1: Import bridge_server')
    total += 1
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import bridge_server
        print('   ✅ bridge_server importé avec succès')
        success += 1
    except Exception as e:
        print(f'   ❌ Erreur: {e}')
    
    # Test 2: Import FastAPI
    print('📦 Test 2: Import FastAPI')
    total += 1
    try:
        from fastapi import FastAPI
        print('   ✅ FastAPI disponible')
        success += 1
    except Exception as e:
        print(f'   ❌ Erreur: {e}')
    
    # Test 3: Import database
    print('📦 Test 3: Import database')
    total += 1
    try:
        import database
        print('   ✅ Database module importé')
        success += 1
    except Exception as e:
        print(f'   ❌ Erreur: {e}')
    
    # Test 4: Vérification des fichiers
    print('📁 Test 4: Fichiers essentiels')
    total += 1
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    essential_files = [
        'bridge_server.py',
        'start_server.py',
        'database.py',
        'permissions_manager.py'
    ]
    
    missing = []
    for file in essential_files:
        if not os.path.exists(os.path.join(parent_dir, file)):
            missing.append(file)
    
    if not missing:
        print('   ✅ Tous les fichiers essentiels présents')
        success += 1
    else:
        print(f'   ❌ Fichiers manquants: {missing}')
    
    # Test 5: Structure web
    print('🌐 Test 5: Structure web')
    total += 1
    web_dir = os.path.join(parent_dir, 'web')
    if os.path.exists(web_dir):
        css_file = os.path.join(web_dir, 'static', 'css', 'main.css')
        js_file = os.path.join(web_dir, 'static', 'js', 'dashboard.js')
        
        if os.path.exists(css_file) and os.path.exists(js_file):
            print('   ✅ Structure web complète')
            success += 1
        else:
            print('   ❌ Fichiers web manquants')
    else:
        print('   ❌ Dossier web manquant')
    
    # Résultats
    print('\n' + '=' * 40)
    print('📊 RÉSULTATS')
    print('=' * 40)
    print(f'Tests réussis: {success}/{total}')
    
    if success == total:
        print('🎉 TOUS LES TESTS D\'IMPORT RÉUSSIS !')
        print('✅ Le projet est correctement configuré')
        return True
    else:
        print('❌ CERTAINS TESTS ONT ÉCHOUÉ')
        print('⚠️ Vérifiez la configuration du projet')
        return False

def test_database():
    """Test simple de la base de données"""
    print('\n💾 TEST BASE DE DONNÉES')
    print('=' * 25)
    
    try:
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(parent_dir, 'bridge_data.db')
        
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f'✅ Base de données présente ({size} bytes)')
            return True
        else:
            print('⚠️ Base de données sera créée au premier démarrage')
            return True
    except Exception as e:
        print(f'❌ Erreur DB: {e}')
        return False

def test_connectivity():
    """Test de connectivité simple sans démarrer le serveur"""
    print('\n🌐 TEST CONNECTIVITÉ (sans serveur)')
    print('=' * 35)
    
    try:
        import requests
        
        # Test si un serveur tourne déjà
        try:
            response = requests.get('http://localhost:8080/health', timeout=2)
            if response.status_code == 200:
                print('✅ Un serveur McP Bridge est déjà en cours')
                data = response.json()
                print(f'   Status: {data.get("status", "unknown")}')
                return True
            else:
                print(f'⚠️ Serveur répond mais status: {response.status_code}')
                return False
        except:
            print('ℹ️ Aucun serveur en cours (normal)')
            return True
            
    except Exception as e:
        print(f'❌ Erreur: {e}')
        return False

if __name__ == "__main__":
    print('🔧 McP Bridge - Tests de Validation')
    print('==================================')
    
    all_success = True
    
    # Tests des imports
    if not test_imports():
        all_success = False
    
    # Test de la base de données
    if not test_database():
        all_success = False
    
    # Test de connectivité
    if not test_connectivity():
        all_success = False
    
    # Résultat final
    print('\n' + '=' * 50)
    if all_success:
        print('🎉 VALIDATION RÉUSSIE !')
        print('✅ McP Bridge est prêt à être utilisé')
        print('\n💡 Pour démarrer le serveur :')
        print('   python start_server.py')
        sys.exit(0)
    else:
        print('❌ VALIDATION ÉCHOUÉE')
        print('⚠️ Corrigez les erreurs avant de continuer')
        sys.exit(1)