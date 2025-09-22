#!/usr/bin/env python3
"""
🔑 Générateur rapide de token API pour l'utilisateur beroute
"""

import sys
import os
import asyncio

# Ajouter le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from api_token_manager import APITokenManager
from database import setup_database

async def generate_beroute_api_token():
    """Génère un token API pour l'utilisateur beroute"""
    
    print("🔑 Générateur de token API pour l'utilisateur beroute")
    print("=" * 55)
    
    try:
        # S'assurer que la base de données est configurée
        await setup_database()
        
        # Créer le gestionnaire de tokens
        manager = APITokenManager()
        
        # Générer un token pour l'utilisateur beroute (ID 1)
        print("⏳ Génération du token API...")
        token_info = manager.generate_token(
            user_id=1,  # ID de l'utilisateur beroute
            token_name="LM Studio API Token",
            expires_days=365
        )
        
        print(f"✅ Token API généré avec succès!")
        print(f"   Token: {token_info['token']}")
        print(f"   ID: {token_info['token_id']}")
        print(f"   Expire le: {token_info['expires_at']}")
        print(f"   Permissions: {token_info['permissions']}")
        
        # Tester la validation du token
        print("\n🔍 Test de validation du token...")
        validation = manager.validate_token(token_info['token'])
        
        if validation:
            print(f"✅ Token validé:")
            print(f"   Utilisateur: {validation['username']}")
            print(f"   Rôle: {validation['role']}")
            print(f"   Permissions: {validation['permissions']}")
        else:
            print("❌ Erreur de validation du token")
            return None
        
        # Afficher les instructions d'utilisation
        print("\n📋 Instructions d'utilisation:")
        print("   1. Copiez ce token dans votre configuration LM Studio")
        print("   2. Remplacez le HASS_TOKEN par ce token dans l'Authorization header")
        print("   3. Utilisez 'Bearer <token>' dans les requêtes HTTP")
        
        print(f"\n🔗 Configuration LM Studio:")
        print(f'   "Authorization": "Bearer {token_info["token"]}"')
        
        # Sauvegarder dans un fichier pour référence
        token_file = "configs/api-token-beroute.txt"
        os.makedirs(os.path.dirname(token_file), exist_ok=True)
        
        with open(token_file, 'w') as f:
            f.write(f"Token API pour utilisateur beroute\n")
            f.write(f"Généré le: {token_info['expires_at']}\n")
            f.write(f"Token: {token_info['token']}\n")
            f.write(f"ID: {token_info['token_id']}\n")
        
        print(f"\n💾 Token sauvegardé dans: {token_file}")
        
        return token_info['token']
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Point d'entrée principal"""
    try:
        return asyncio.run(generate_beroute_api_token())
    except KeyboardInterrupt:
        print("\n⚠️  Génération interrompue par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    token = main()
    if token:
        print(f"\n🎉 Success! Token: {token}")
    else:
        print("\n😞 Échec de la génération du token")
        sys.exit(1)