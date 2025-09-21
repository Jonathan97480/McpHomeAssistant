#!/usr/bin/env python3
"""
🧪 Tests pour le système de configuration Home Assistant
Tests unitaires pour la validation, le chiffrement et la connexion HA
"""

import pytest
import asyncio
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

# Import des modules à tester
from ha_config_manager import (
    HAConfigManager, HAConfigCreate, HAConfigUpdate, 
    HAConnectionStatus, HATestResult, HAConfig
)
from database import DatabaseManager

class TestHAConfigManager:
    """Tests pour le gestionnaire de configuration HA"""
    
    @pytest.fixture
    async def ha_manager(self):
        """Fixture pour créer un gestionnaire HA avec BDD temporaire"""
        # Créer une BDD temporaire
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        # Configurer la base temporaire
        from database import db_manager
        db_manager.db_path = temp_db.name
        await db_manager.initialize()
        
        # Créer le gestionnaire HA
        manager = HAConfigManager()
        
        yield manager
        
        # Nettoyage
        await manager.close_session()
        try:
            os.unlink(temp_db.name)
        except:
            pass
    
    @pytest.fixture
    def sample_config_data(self):
        """Données de configuration HA pour les tests"""
        return HAConfigCreate(
            name="Test HA",
            url="http://localhost:8123",
            token="llat_test_token_very_long_example_12345678901234567890"
        )
    
    def test_config_validation_valid(self, sample_config_data):
        """Test validation d'une configuration valide"""
        # Doit passer sans exception
        assert sample_config_data.name == "Test HA"
        assert sample_config_data.url == "http://localhost:8123"
        assert len(sample_config_data.token) >= 20
    
    def test_config_validation_invalid_url(self):
        """Test validation URL invalide"""
        with pytest.raises(ValueError, match="URL doit commencer par"):
            HAConfigCreate(
                name="Test",
                url="invalid-url",
                token="llat_test_token_very_long_example_12345678901234567890"
            )
    
    def test_config_validation_short_token(self):
        """Test validation token trop court"""
        with pytest.raises(ValueError, match="Token trop court"):
            HAConfigCreate(
                name="Test",
                url="http://localhost:8123",
                token="short"
            )
    
    def test_config_validation_https_recommendation(self, caplog):
        """Test recommandation HTTPS pour production"""
        config = HAConfigCreate(
            name="Test",
            url="http://example.com:8123",
            token="llat_test_token_very_long_example_12345678901234567890"
        )
        # Le warning devrait être loggé
        assert "example.com" in config.url
    
    async def test_encryption_decryption(self, ha_manager):
        """Test chiffrement et déchiffrement des tokens"""
        original_token = "llat_test_token_very_long_example_12345678901234567890"
        
        # Chiffrer
        encrypted = ha_manager._encrypt_token(original_token)
        assert encrypted != original_token
        assert len(encrypted) > len(original_token)
        
        # Déchiffrer
        decrypted = ha_manager._decrypt_token(encrypted)
        assert decrypted == original_token
    
    async def test_encrypt_different_tokens_different_output(self, ha_manager):
        """Test que deux tokens différents donnent des chiffrés différents"""
        token1 = "llat_test_token_1_very_long_example_12345678901234567890"
        token2 = "llat_test_token_2_very_long_example_12345678901234567890"
        
        encrypted1 = ha_manager._encrypt_token(token1)
        encrypted2 = ha_manager._encrypt_token(token2)
        
        assert encrypted1 != encrypted2
    
    @patch('aiohttp.ClientSession.get')
    async def test_ha_connection_success(self, mock_get, ha_manager):
        """Test connexion HA réussie"""
        # Mock des réponses HTTP
        mock_api_response = AsyncMock()
        mock_api_response.status = 200
        mock_api_response.json = AsyncMock(return_value={"message": "API running"})
        
        mock_config_response = AsyncMock()
        mock_config_response.status = 200
        mock_config_response.json = AsyncMock(return_value={"version": "2024.1.0"})
        
        mock_states_response = AsyncMock()
        mock_states_response.status = 200
        mock_states_response.json = AsyncMock(return_value=[{"entity_id": "light.test"}] * 10)
        
        # Configurer les mocks dans l'ordre des appels
        mock_get.side_effect = [
            mock_api_response,      # Premier appel à /api/
            mock_config_response,   # Deuxième appel à /api/config
            mock_states_response    # Troisième appel à /api/states
        ]
        
        # Tester la connexion
        result = await ha_manager.test_ha_connection(
            "http://localhost:8123",
            "llat_test_token_very_long_example_12345678901234567890"
        )
        
        # Vérifications
        assert result.success is True
        assert result.status == HAConnectionStatus.CONNECTED
        assert result.ha_version == "2024.1.0"
        assert result.entities_count == 10
        assert result.response_time_ms is not None
        assert result.response_time_ms > 0
    
    @patch('aiohttp.ClientSession.get')
    async def test_ha_connection_invalid_token(self, mock_get, ha_manager):
        """Test connexion HA avec token invalide"""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_get.return_value = mock_response
        
        result = await ha_manager.test_ha_connection(
            "http://localhost:8123",
            "invalid_token"
        )
        
        assert result.success is False
        assert result.status == HAConnectionStatus.INVALID_TOKEN
        assert "Token d'accès invalide" in result.message
    
    @patch('aiohttp.ClientSession.get')
    async def test_ha_connection_server_error(self, mock_get, ha_manager):
        """Test connexion HA avec erreur serveur"""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_get.return_value = mock_response
        
        result = await ha_manager.test_ha_connection(
            "http://localhost:8123",
            "llat_test_token_very_long_example_12345678901234567890"
        )
        
        assert result.success is False
        assert result.status == HAConnectionStatus.ERROR
        assert "Erreur HTTP 500" in result.message
    
    @patch('aiohttp.ClientSession.get')
    async def test_ha_connection_timeout(self, mock_get, ha_manager):
        """Test connexion HA avec timeout"""
        mock_get.side_effect = asyncio.TimeoutError()
        
        result = await ha_manager.test_ha_connection(
            "http://localhost:8123",
            "llat_test_token_very_long_example_12345678901234567890"
        )
        
        assert result.success is False
        assert result.status == HAConnectionStatus.ERROR
        assert "Timeout de connexion" in result.message
    
    @patch.object(HAConfigManager, 'test_ha_connection')
    async def test_create_config(self, mock_test, ha_manager, sample_config_data):
        """Test création d'une configuration HA"""
        # Mock du test de connexion
        mock_test.return_value = HATestResult(
            success=True,
            status=HAConnectionStatus.CONNECTED,
            message="Test successful",
            tested_at=datetime.now()
        )
        
        # Créer la configuration
        config = await ha_manager.create_config(1, sample_config_data)
        
        # Vérifications
        assert config.user_id == 1
        assert config.name == sample_config_data.name
        assert config.url == sample_config_data.url
        assert config.is_active is True
        assert config.last_status == HAConnectionStatus.CONNECTED
        assert config.token_encrypted != sample_config_data.token
        
        # Vérifier que le test a été appelé
        mock_test.assert_called_once_with(sample_config_data.url, sample_config_data.token)
    
    async def test_get_config_not_found(self, ha_manager):
        """Test récupération d'une configuration inexistante"""
        config = await ha_manager.get_config(999, 999)
        assert config is None
    
    async def test_get_decrypted_token_not_found(self, ha_manager):
        """Test récupération d'un token pour une config inexistante"""
        token = await ha_manager.get_decrypted_token(999, 999)
        assert token is None
    
    @patch.object(HAConfigManager, 'test_ha_connection')
    async def test_config_lifecycle(self, mock_test, ha_manager, sample_config_data):
        """Test cycle de vie complet d'une configuration"""
        # Mock du test de connexion
        mock_test.return_value = HATestResult(
            success=True,
            status=HAConnectionStatus.CONNECTED,
            message="Test successful",
            tested_at=datetime.now()
        )
        
        user_id = 1
        
        # 1. Créer
        config = await ha_manager.create_config(user_id, sample_config_data)
        assert config is not None
        
        # 2. Récupérer
        retrieved_config = await ha_manager.get_config(user_id)
        assert retrieved_config is not None
        assert retrieved_config.name == sample_config_data.name
        
        # 3. Récupérer le token déchiffré
        decrypted_token = await ha_manager.get_decrypted_token(user_id)
        assert decrypted_token == sample_config_data.token
        
        # 4. Lister
        configs = await ha_manager.list_configs(user_id)
        assert len(configs) == 1
        assert configs[0].name == sample_config_data.name
        
        # 5. Mettre à jour
        update_data = HAConfigUpdate(name="Updated HA")
        updated_config = await ha_manager.update_config(user_id, 1, update_data)
        assert updated_config.name == "Updated HA"
        
        # 6. Supprimer
        success = await ha_manager.delete_config(user_id, 1)
        assert success is True
        
        # 7. Vérifier suppression
        deleted_config = await ha_manager.get_config(user_id, 1)
        assert deleted_config is None


class TestHAConfigIntegration:
    """Tests d'intégration pour la configuration HA"""
    
    @pytest.mark.asyncio
    async def test_full_encryption_cycle(self):
        """Test complet du cycle de chiffrement"""
        # Créer un gestionnaire temporaire
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            # Configurer la base temporaire
            from database import db_manager
            original_path = db_manager.db_path
            db_manager.db_path = temp_db.name
            await db_manager.initialize()
            
            # Créer deux gestionnaires (simule redémarrage)
            manager1 = HAConfigManager()
            token_original = "llat_super_secret_token_12345678901234567890"
            
            # Chiffrer avec le premier gestionnaire
            encrypted = manager1._encrypt_token(token_original)
            
            # Fermer le premier
            await manager1.close_session()
            
            # Créer un second gestionnaire (simule redémarrage)
            manager2 = HAConfigManager()
            
            # Déchiffrer avec le second gestionnaire
            decrypted = manager2._decrypt_token(encrypted)
            
            # Vérifier que ça fonctionne
            assert decrypted == token_original
            
            await manager2.close_session()
            
            # Restaurer le chemin original
            db_manager.db_path = original_path
            
        finally:
            try:
                os.unlink(temp_db.name)
            except:
                pass
    
    def test_config_models_serialization(self):
        """Test sérialisation des modèles de configuration"""
        # Test HAConfigCreate
        config_data = HAConfigCreate(
            name="Test Serialization",
            url="https://homeassistant.local:8123",
            token="llat_serialization_test_token_12345678901234567890"
        )
        
        # Doit pouvoir être sérialisé en JSON
        json_data = config_data.dict()
        assert json_data['name'] == "Test Serialization"
        assert json_data['url'] == "https://homeassistant.local:8123"
        
        # Test HAConfigUpdate avec valeurs partielles
        update_data = HAConfigUpdate(name="Updated Name")
        json_update = update_data.dict(exclude_unset=True)
        assert 'name' in json_update
        assert 'url' not in json_update  # Pas défini
        assert 'token' not in json_update  # Pas défini


# Fixtures pytest pour les tests async
@pytest.fixture(scope="session")
def event_loop():
    """Fixture pour gérer la boucle d'événements async"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v", "--tb=short"])