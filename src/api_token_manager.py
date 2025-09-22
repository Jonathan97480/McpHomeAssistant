#!/usr/bin/env python3
"""
Générateur de tokens API personnalisés pour les utilisateurs MCP Bridge
"""

import secrets
import string
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta

class APITokenManager:
    """Gestionnaire des tokens API personnalisés"""
    
    def __init__(self, db_path="bridge_data.db"):
        self.db_path = db_path
        self.setup_tokens_table()
    
    def setup_tokens_table(self):
        """Crée la table des tokens API si elle n'existe pas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                token_name TEXT,
                permissions TEXT, -- JSON des permissions
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_used TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_token(self, user_id, token_name="LM Studio", expires_days=365):
        """Génère un nouveau token API pour un utilisateur"""
        # Générer un token sécurisé
        alphabet = string.ascii_letters + string.digits
        token = 'mcp_' + ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # Hash du token pour stockage sécurisé
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Date d'expiration
        expires_at = datetime.now() + timedelta(days=expires_days)
        
        # Permissions par défaut
        permissions = {
            "mcp_tools": True,
            "home_assistant": True,
            "read_entities": True,
            "control_devices": True
        }
        
        # Stocker en base
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_tokens (user_id, token_hash, token_name, permissions, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, token_hash, token_name, json.dumps(permissions), expires_at))
        
        token_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "token": token,
            "token_id": token_id,
            "expires_at": expires_at.isoformat(),
            "permissions": permissions
        }
    
    def validate_token(self, token):
        """Valide un token et retourne les infos utilisateur"""
        if not token or not token.startswith('mcp_'):
            return None
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.id, t.user_id, t.permissions, t.expires_at, t.is_active,
                   u.username, u.role
            FROM api_tokens t
            JOIN users u ON t.user_id = u.id
            WHERE t.token_hash = ? AND t.is_active = 1
        ''', (token_hash,))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        token_id, user_id, permissions_json, expires_at, is_active, username, role = result
        
        # Vérifier expiration
        if expires_at:
            expires = datetime.fromisoformat(expires_at.replace('Z', '+00:00').replace('+00:00', ''))
            if datetime.now() > expires:
                conn.close()
                return None
        
        # Mettre à jour last_used
        cursor.execute('''
            UPDATE api_tokens SET last_used = CURRENT_TIMESTAMP WHERE id = ?
        ''', (token_id,))
        
        conn.commit()
        conn.close()
        
        return {
            "token_id": token_id,
            "user_id": user_id,
            "username": username,
            "role": role,
            "permissions": json.loads(permissions_json)
        }
    
    def list_user_tokens(self, user_id):
        """Liste tous les tokens d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, token_name, created_at, expires_at, last_used, is_active
            FROM api_tokens
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        tokens = []
        for row in cursor.fetchall():
            tokens.append({
                "id": row[0],
                "name": row[1],
                "created_at": row[2],
                "expires_at": row[3],
                "last_used": row[4],
                "is_active": bool(row[5])
            })
        
        conn.close()
        return tokens
    
    def revoke_token(self, token_id, user_id):
        """Révoque un token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE api_tokens SET is_active = 0 
            WHERE id = ? AND user_id = ?
        ''', (token_id, user_id))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0

def main():
    """Test du générateur de tokens"""
    manager = APITokenManager()
    
    print("🔐 Générateur de tokens API MCP Bridge")
    print("=" * 50)
    
    # Générer un token pour l'utilisateur beroute (ID 1)
    token_info = manager.generate_token(1, "LM Studio Token", expires_days=365)
    
    print(f"✅ Token généré pour LM Studio:")
    print(f"   Token: {token_info['token']}")
    print(f"   Expire le: {token_info['expires_at']}")
    print(f"   Permissions: {token_info['permissions']}")
    
    # Tester la validation
    validation = manager.validate_token(token_info['token'])
    if validation:
        print(f"\n✅ Token validé:")
        print(f"   Utilisateur: {validation['username']}")
        print(f"   Rôle: {validation['role']}")
        print(f"   Permissions: {validation['permissions']}")
    
    return token_info['token']

if __name__ == "__main__":
    token = main()