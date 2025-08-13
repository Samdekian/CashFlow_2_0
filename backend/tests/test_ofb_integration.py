"""
Test Open Finance Brasil Integration
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import os
import tempfile

from app.core.open_finance_brasil import (
    OFBConfig,
    OFBCertificateManager,
    OFBOAuthClient,
    OFBConsentManager,
    OpenFinanceBrasilIntegration
)


class TestOFBConfig:
    """Test OFB configuration"""
    
    def test_ofb_config_creation(self):
        """Test OFB configuration creation"""
        config = OFBConfig(
            client_id="test_client",
            client_secret="test_secret",
            redirect_uri="http://localhost:3000/callback",
            transport_cert_path="certs/transport.pem",
            transport_key_path="certs/transport.key",
            signing_cert_path="certs/signing.pem",
            signing_key_path="certs/signing.key",
            ca_bundle_path="certs/ca-bundle.pem"
        )
        
        assert config.client_id == "test_client"
        assert config.client_secret == "test_secret"
        assert config.redirect_uri == "http://localhost:3000/callback"


class TestOFBCertificateManager:
    """Test certificate management"""
    
    @pytest.fixture
    def temp_certs(self):
        """Create temporary certificates for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock certificate files
            cert_path = os.path.join(temp_dir, "test.pem")
            key_path = os.path.join(temp_dir, "test.key")
            
            with open(cert_path, 'w') as f:
                f.write("-----BEGIN CERTIFICATE-----\nMOCK\n-----END CERTIFICATE-----")
            
            with open(key_path, 'w') as f:
                f.write("-----BEGIN PRIVATE KEY-----\nMOCK\n-----END PRIVATE KEY-----")
            
            yield {
                "cert_path": cert_path,
                "key_path": key_path,
                "temp_dir": temp_dir
            }
    
    def test_certificate_manager_creation(self, temp_certs):
        """Test certificate manager creation"""
        config = OFBConfig(
            client_id="test",
            client_secret="test",
            redirect_uri="http://localhost:3000/callback",
            transport_cert_path=temp_certs["cert_path"],
            transport_key_path=temp_certs["key_path"],
            signing_cert_path=temp_certs["cert_path"],
            signing_key_path=temp_certs["key_path"],
            ca_bundle_path=temp_certs["cert_path"]
        )
        
        cert_manager = OFBCertificateManager(config)
        assert cert_manager.config == config


class TestOFBOAuthClient:
    """Test OAuth client"""
    
    def test_oauth_client_creation(self):
        """Test OAuth client creation"""
        config = Mock()
        cert_manager = Mock()
        
        oauth_client = OFBOAuthClient(config, cert_manager)
        assert oauth_client.config == config
        assert oauth_client.cert_manager == cert_manager
    
    def test_pkce_challenge_generation(self):
        """Test PKCE challenge generation"""
        config = Mock()
        cert_manager = Mock()
        
        oauth_client = OFBOAuthClient(config, cert_manager)
        state = "test_state"
        
        challenge, verifier = oauth_client.generate_pkce_challenge(state)
        
        assert challenge is not None
        assert verifier is not None
        assert challenge != verifier
        assert oauth_client.code_verifiers[state] == verifier


class TestOFBConsentManager:
    """Test consent management"""
    
    def test_consent_manager_creation(self):
        """Test consent manager creation"""
        config = Mock()
        oauth_client = Mock()
        
        consent_manager = OFBConsentManager(config, oauth_client)
        assert consent_manager.config == config
        assert consent_manager.oauth_client == oauth_client
        assert consent_manager.consents == {}


class TestOpenFinanceBrasilIntegration:
    """Test main integration class"""
    
    def test_integration_creation(self):
        """Test integration creation"""
        config = Mock()
        
        integration = OpenFinanceBrasilIntegration(config)
        assert integration.config == config
        assert integration.cert_manager is not None
        assert integration.oauth_client is not None
        assert integration.consent_manager is not None
        assert integration.api_client is not None


# Integration tests
@pytest.mark.asyncio
async def test_ofb_integration_flow():
    """Test complete OFB integration flow"""
    # This would test the complete flow in a real scenario
    # For now, just test that the classes can be instantiated
    
    config = OFBConfig(
        client_id="test_client",
        client_secret="test_secret",
        redirect_uri="http://localhost:3000/callback",
        transport_cert_path="certs/transport.pem",
        transport_key_path="certs/transport.key",
        signing_cert_path="certs/signing.pem",
        signing_key_path="certs/signing.key",
        ca_bundle_path="certs/ca-bundle.pem"
    )
    
    integration = OpenFinanceBrasilIntegration(config)
    
    # Test that all components are properly initialized
    assert integration.cert_manager is not None
    assert integration.oauth_client is not None
    assert integration.consent_manager is not None
    assert integration.api_client is not None
    
    # Test health status (should work without real certificates in mock mode)
    health_status = await integration.get_health_status()
    assert health_status["status"] == "healthy"
    assert health_status["initialized"] is True
