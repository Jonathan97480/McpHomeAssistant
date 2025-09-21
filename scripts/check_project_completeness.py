#!/usr/bin/env python3
"""
🔍 Script de Vérification de Complétude du Projet Phase 3.4
=============================================================
Vérifie que tous les fichiers critiques sont présents et complets.
"""

import os
import sys
from datetime import datetime

class ProjectValidator:
    def __init__(self):
        self.critical_files = {
            # Fichiers Python principaux
            'bridge_server.py': {'min_size': 15000, 'type': 'Serveur principal'},
            'auth_manager.py': {'min_size': 8000, 'type': 'Authentification'},
            'database.py': {'min_size': 10000, 'type': 'Base de données'},
            'cache_manager.py': {'min_size': 5000, 'type': 'Cache'},
            'permissions_manager.py': {'min_size': 3000, 'type': 'Permissions'},
            'permissions_middleware.py': {'min_size': 2000, 'type': 'Middleware'},
            'ha_config_manager.py': {'min_size': 3000, 'type': 'Config HA'},
            'start_server.py': {'min_size': 1000, 'type': 'Démarrage'},
            
            # Interface Web
            'web/templates/login.html': {'min_size': 5000, 'type': 'Template Login'},
            'web/templates/dashboard.html': {'min_size': 8000, 'type': 'Template Dashboard'},
            'web/templates/admin.html': {'min_size': 5000, 'type': 'Template Admin'},
            'web/templates/config.html': {'min_size': 5000, 'type': 'Template Config'},
            'web/templates/logs.html': {'min_size': 5000, 'type': 'Template Logs'},
            'web/templates/tools.html': {'min_size': 5000, 'type': 'Template Tools'},
            'web/templates/permissions.html': {'min_size': 5000, 'type': 'Template Permissions'},
            'web/templates/dashboard_overview.html': {'min_size': 3000, 'type': 'Template Overview'},
            'web/static/css/main.css': {'min_size': 10000, 'type': 'CSS Principal'},
            'web/static/js/dashboard.js': {'min_size': 20000, 'type': 'JavaScript Dashboard'},
            
            # Tests
            'tests/test_quick.py': {'min_size': 2000, 'type': 'Test Rapide'},
            'tests/test_auth.py': {'min_size': 3000, 'type': 'Test Auth'},
            'tests/test_web_interface.py': {'min_size': 3000, 'type': 'Test Web'},
            'tests/test_validation.py': {'min_size': 2000, 'type': 'Test Validation'},
            'tests/test_complete.py': {'min_size': 4000, 'type': 'Test Complet'},
            
            # Scripts
            'scripts/migrate_pi.sh': {'min_size': 1000, 'type': 'Migration Pi'},
            'scripts/deploy_pi.sh': {'min_size': 1000, 'type': 'Déploiement Pi'},
            
            # Configuration
            'requirements.txt': {'min_size': 500, 'type': 'Dépendances'},
            '.env.example': {'min_size': 200, 'type': 'Config exemple'},
        }
        
        self.required_dependencies = [
            'fastapi', 'uvicorn', 'jinja2', 'bcrypt', 'python-jose',
            'passlib', 'email-validator', 'cryptography', 'httpx',
            'requests', 'psutil', 'aiohttp', 'python-dotenv'
        ]
        
    def check_file_exists_and_size(self, file_path, min_size):
        """Vérifie l'existence et la taille d'un fichier"""
        if not os.path.exists(file_path):
            return False, 0, "MANQUANT"
        
        actual_size = os.path.getsize(file_path)
        if actual_size < min_size:
            return True, actual_size, "TROP PETIT"
        
        return True, actual_size, "OK"
    
    def check_requirements(self):
        """Vérifie le fichier requirements.txt"""
        if not os.path.exists('requirements.txt'):
            return False, []
        
        with open('requirements.txt', 'r') as f:
            content = f.read().lower()
        
        missing_deps = []
        for dep in self.required_dependencies:
            if dep.lower() not in content:
                missing_deps.append(dep)
        
        return len(missing_deps) == 0, missing_deps
    
    def run_validation(self):
        """Lance la validation complète"""
        print("🔍 VALIDATION DU PROJET PHASE 3.4")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Vérification des fichiers
        issues = []
        total_files = len(self.critical_files)
        valid_files = 0
        
        print("📁 VÉRIFICATION DES FICHIERS:")
        print("-" * 40)
        
        for file_path, config in self.critical_files.items():
            exists, size, status = self.check_file_exists_and_size(
                file_path, config['min_size']
            )
            
            if status == "OK":
                print(f"✅ {file_path}")
                print(f"   📊 {size:,} bytes | Type: {config['type']}")
                valid_files += 1
            elif status == "TROP PETIT":
                print(f"⚠️  {file_path}")
                print(f"   📊 {size:,} bytes (min: {config['min_size']:,}) | Type: {config['type']}")
                issues.append(f"Fichier trop petit: {file_path}")
            else:
                print(f"❌ {file_path}")
                print(f"   📊 MANQUANT | Type: {config['type']}")
                issues.append(f"Fichier manquant: {file_path}")
            print()
        
        # Vérification des dépendances
        print("📦 VÉRIFICATION DES DÉPENDANCES:")
        print("-" * 40)
        
        deps_ok, missing_deps = self.check_requirements()
        if deps_ok:
            print("✅ Toutes les dépendances sont présentes")
        else:
            print("❌ Dépendances manquantes:")
            for dep in missing_deps:
                print(f"   - {dep}")
                issues.append(f"Dépendance manquante: {dep}")
        
        # Résultats
        print()
        print("=" * 60)
        print("📊 RÉSULTATS DE LA VALIDATION")
        print("=" * 60)
        
        print(f"📁 Fichiers: {valid_files}/{total_files} valides")
        print(f"📦 Dépendances: {'✅ OK' if deps_ok else '❌ Problèmes'}")
        
        if issues:
            print(f"🚨 {len(issues)} problème(s) détecté(s):")
            for issue in issues:
                print(f"   • {issue}")
            print()
            print("🔧 ACTIONS RECOMMANDÉES:")
            if missing_deps:
                print("   1. Mettre à jour requirements.txt avec les dépendances manquantes")
            if any("manquant" in issue.lower() for issue in issues):
                print("   2. Récupérer les fichiers manquants depuis Git")
            if any("trop petit" in issue.lower() for issue in issues):
                print("   3. Vérifier l'intégrité des fichiers trop petits")
            return False
        else:
            print("🎉 PROJET COMPLET ET PRÊT POUR LA MIGRATION!")
            return True

def main():
    """Fonction principale"""
    validator = ProjectValidator()
    success = validator.run_validation()
    
    if success:
        print("\n✅ Validation réussie - Le projet peut être migré en toute sécurité")
        sys.exit(0)
    else:
        print("\n❌ Validation échouée - Corriger les problèmes avant migration")
        sys.exit(1)

if __name__ == "__main__":
    main()