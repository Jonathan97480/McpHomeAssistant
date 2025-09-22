#!/usr/bin/env python3
"""
Script pour vérifier la structure de la table ha_configs
"""

import sqlite3
import os

def check_table_structure():
    """Vérifie la structure de la table ha_configs"""
    
    db_path = "src/bridge_data.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de données introuvable")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier la structure de la table ha_configs
        cursor.execute("PRAGMA table_info(ha_configs)")
        columns = cursor.fetchall()
        
        print("📊 Structure de la table ha_configs:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'} {'PK' if col[5] else ''}")
        
        # Afficher quelques données
        cursor.execute("SELECT * FROM ha_configs LIMIT 3")
        rows = cursor.fetchall()
        
        print(f"\n📋 Données existantes ({len(rows)}):")
        for row in rows:
            print(f"   {row}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔍 STRUCTURE TABLE HA_CONFIGS")
    print("=" * 40)
    check_table_structure()