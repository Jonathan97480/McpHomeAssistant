#!/usr/bin/env python3
"""
Script de démarrage du serveur bridge MCP avec interface web
Version simplifiée pour les tests
"""

import uvicorn
import asyncio
import os
import sys
from pathlib import Path

# Ajouter le répertoire du projet au path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Démarre le serveur avec l'interface web"""
    print("🌉 Démarrage du serveur MCP Bridge avec interface web")
    print("📊 Dashboard disponible sur: http://localhost:8080")
    print("🔧 Configuration dans l'interface web")
    print("=" * 60)
    
    # Configuration par défaut pour les tests
    os.environ.setdefault("HOMEASSISTANT_URL", "")
    os.environ.setdefault("HOMEASSISTANT_TOKEN", "")
    
    try:
        # Démarrage du serveur
        uvicorn.run(
            "bridge_server:app",
            host="0.0.0.0",
            port=8080,
            reload=False,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n⏹️  Serveur arrêté")
    except Exception as e:
        print(f"\n❌ Erreur de démarrage: {e}")

if __name__ == "__main__":
    main()