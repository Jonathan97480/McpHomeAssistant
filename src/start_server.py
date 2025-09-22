#!/usr/bin/env python3
"""
Script de démarrage du serveur web avec gestion d'erreurs
"""

import sys
import os
import traceback
import uvicorn

def start_server():
    """Démarre le serveur avec gestion d'erreurs"""
    try:
        print("🚀 Démarrage du serveur MCP Bridge...")
        print("📍 URL: http://localhost:8080")
        print("🔧 Mode: Développement")
        print("=" * 50)
        
        # Importer le module bridge_server
        import bridge_server
        
        # Démarrer uvicorn
        uvicorn.run(
            "bridge_server:app",
            host="0.0.0.0",
            port=8080,
            reload=False,  # Pas de reload pour éviter les conflits
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("🔧 Vérifiez que tous les modules requis sont installés")
        return 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Serveur arrêté par l'utilisateur")
        return 0
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        print("📋 Trace complète:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = start_server()
    sys.exit(exit_code)