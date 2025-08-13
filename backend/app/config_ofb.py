"""
Open Finance Brasil Configuration Settings
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class OFBSettings(BaseSettings):
    """Open Finance Brasil specific settings"""
    
    # Client Registration
    ofb_client_id: str = Field(default="", description="OFB client ID")
    ofb_client_secret: str = Field(default="", description="OFB client secret")
    ofb_redirect_uri: str = Field(default="http://localhost:3000/ofb/callback", description="OAuth redirect URI")
    
    # Endpoints
    ofb_auth_base_url: str = Field(
        default="https://auth.openfinancebrasil.org.br",
        description="Authorization server base URL"
    )
    ofb_api_base_url: str = Field(
        default="https://api.openfinancebrasil.org.br",
        description="API server base URL"
    )
    ofb_directory_url: str = Field(
        default="https://directory.openfinancebrasil.org.br",
        description="Directory server URL"
    )
    
    # Certificate Paths
    ofb_transport_cert_path: str = Field(
        default="certs/transport.pem",
        description="Transport certificate path"
    )
    ofb_transport_key_path: str = Field(
        default="certs/transport.key",
        description="Transport private key path"
    )
    ofb_signing_cert_path: str = Field(
        default="certs/signing.pem",
        description="Signing certificate path"
    )
    ofb_signing_key_path: str = Field(
        default="certs/signing.key",
        description="Signing private key path"
    )
    ofb_ca_bundle_path: str = Field(
        default="certs/ca-bundle.pem",
        description="CA bundle path"
    )
    
    # Security Settings
    ofb_request_timeout: int = Field(default=30, description="Request timeout in seconds")
    ofb_max_retries: int = Field(default=3, description="Maximum retry attempts")
    
    # Rate Limiting
    ofb_rate_limit_requests: int = Field(default=100, description="Rate limit requests per window")
    ofb_rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # Feature Flags
    ofb_enabled: bool = Field(default=False, description="Enable Open Finance Brasil integration")
    ofb_sandbox_mode: bool = Field(default=True, description="Use sandbox environment")
    ofb_mock_mode: bool = Field(default=True, description="Use mock mode for development")
    
    # Monitoring
    ofb_enable_metrics: bool = Field(default=True, description="Enable OFB metrics collection")
    ofb_metrics_endpoint: str = Field(default="/metrics", description="Metrics endpoint")
    
    class Config:
        env_file = ".env"
        env_prefix = "OFB_"
    
    def get_certificate_paths(self) -> dict:
        """Get absolute certificate paths"""
        base_path = Path(__file__).parent.parent.parent / "certs"
        
        return {
            "transport_cert_path": str(base_path / self.ofb_transport_cert_path),
            "transport_key_path": str(base_path / self.ofb_transport_key_path),
            "signing_cert_path": str(base_path / self.ofb_signing_cert_path),
            "signing_key_path": str(base_path / self.ofb_signing_key_path),
            "ca_bundle_path": str(base_path / self.ofb_ca_bundle_path)
        }
    
    def get_endpoints(self) -> dict:
        """Get OFB endpoints based on environment"""
        if self.ofb_sandbox_mode:
            return {
                "auth_base_url": "https://auth.sandbox.openfinancebrasil.org.br",
                "api_base_url": "https://api.sandbox.openfinancebrasil.org.br",
                "directory_url": "https://directory.sandbox.openfinancebrasil.org.br"
            }
        else:
            return {
                "auth_base_url": self.ofb_auth_base_url,
                "api_base_url": self.ofb_api_base_url,
                "directory_url": self.ofb_directory_url
            }
    
    def is_configured(self) -> bool:
        """Check if OFB is properly configured"""
        if not self.ofb_enabled:
            return False
        
        if not self.ofb_client_id or not self.ofb_client_secret:
            return False
        
        # Check if certificates exist
        cert_paths = self.get_certificate_paths()
        for path in cert_paths.values():
            if not os.path.exists(path):
                return False
        
        return True


# Global OFB settings instance
ofb_settings = OFBSettings()
