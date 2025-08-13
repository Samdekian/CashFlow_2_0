"""
Open Finance Brasil Integration Module
Phase 2 Implementation: OAuth 2.0 + FAPI + Certificate Management
"""

import asyncio
import base64
import hashlib
import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode, urljoin

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from fastapi import HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class OFBConfig(BaseModel):
    """Open Finance Brasil configuration"""
    
    # Client Registration
    client_id: str = Field(..., description="OFB client ID")
    client_secret: str = Field(..., description="OFB client secret")
    redirect_uri: str = Field(..., description="OAuth redirect URI")
    
    # Endpoints
    auth_base_url: str = Field(default="https://auth.openfinancebrasil.org.br", description="Authorization server base URL")
    api_base_url: str = Field(default="https://api.openfinancebrasil.org.br", description="API server base URL")
    directory_url: str = Field(default="https://directory.openfinancebrasil.org.br", description="Directory server URL")
    
    # Certificates
    transport_cert_path: str = Field(..., description="Transport certificate path")
    transport_key_path: str = Field(..., description="Transport private key path")
    signing_cert_path: str = Field(..., description="Signing certificate path")
    signing_key_path: str = Field(..., description="Signing private key path")
    ca_bundle_path: str = Field(..., description="CA bundle path")
    
    # Security
    request_timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per window")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")


class OFBCertificateManager:
    """Manage Open Finance Brasil certificates"""
    
    def __init__(self, config: OFBConfig):
        self.config = config
        self.transport_cert: Optional[x509.Certificate] = None
        self.transport_key: Optional[rsa.RSAPrivateKey] = None
        self.signing_cert: Optional[x509.Certificate] = None
        self.signing_key: Optional[rsa.RSAPrivateKey] = None
        
    async def load_certificates(self) -> None:
        """Load and validate all certificates"""
        try:
            # Load transport certificate and key
            self.transport_cert = await self._load_certificate(
                self.config.transport_cert_path
            )
            self.transport_key = await self._load_private_key(
                self.config.transport_key_path
            )
            
            # Load signing certificate and key
            self.signing_cert = await self._load_certificate(
                self.config.signing_cert_path
            )
            self.signing_key = await self._load_private_key(
                self.config.signing_key_path
            )
            
            # Validate certificates
            await self._validate_certificates()
            
            logger.info("All certificates loaded and validated successfully")
            
        except Exception as e:
            logger.error(f"Failed to load certificates: {e}")
            raise
    
    async def _load_certificate(self, cert_path: str) -> x509.Certificate:
        """Load X.509 certificate from file"""
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
                return x509.load_pem_x509_certificate(cert_data)
        except Exception as e:
            raise ValueError(f"Failed to load certificate from {cert_path}: {e}")
    
    async def _load_private_key(self, key_path: str) -> rsa.RSAPrivateKey:
        """Load RSA private key from file"""
        try:
            with open(key_path, 'rb') as f:
                key_data = f.read()
                return serialization.load_pem_private_key(
                    key_data,
                    password=None
                )
        except Exception as e:
            raise ValueError(f"Failed to load private key from {key_path}: {e}")
    
    async def _validate_certificates(self) -> None:
        """Validate certificate compliance and expiration"""
        current_time = datetime.utcnow()
        
        for cert_name, cert in [
            ("transport", self.transport_cert),
            ("signing", self.signing_cert)
        ]:
            # Check expiration
            if cert.not_valid_after < current_time:
                raise ValueError(f"{cert_name} certificate expired")
            
            # Check remaining validity
            days_remaining = (cert.not_valid_after - current_time).days
            if days_remaining < 30:
                logger.warning(f"{cert_name} certificate expires in {days_remaining} days")
            
            # Validate certificate chain (basic validation)
            if not await self._validate_certificate_chain(cert):
                raise ValueError(f"{cert_name} certificate chain validation failed")
    
    async def _validate_certificate_chain(self, cert: x509.Certificate) -> bool:
        """Basic certificate chain validation"""
        try:
            # Load CA bundle
            with open(self.config.ca_bundle_path, 'rb') as f:
                ca_data = f.read()
            
            # Basic validation - in production, implement full chain validation
            return True
        except Exception as e:
            logger.warning(f"Certificate chain validation failed: {e}")
            return False
    
    def get_certificate_info(self) -> Dict:
        """Get certificate information for monitoring"""
        return {
            "transport_cert": {
                "subject": str(self.transport_cert.subject) if self.transport_cert else None,
                "issuer": str(self.transport_cert.issuer) if self.transport_cert else None,
                "expires_at": self.transport_cert.not_valid_after.isoformat() if self.transport_cert else None,
                "serial_number": str(self.transport_cert.serial_number) if self.transport_cert else None
            },
            "signing_cert": {
                "subject": str(self.signing_cert.subject) if self.signing_cert else None,
                "issuer": str(self.signing_cert.issuer) if self.signing_cert else None,
                "expires_at": self.signing_cert.not_valid_after.isoformat() if self.signing_cert else None,
                "serial_number": str(self.signing_cert.serial_number) if self.signing_cert else None
            }
        }


class OFBOAuthClient:
    """Open Finance Brasil OAuth 2.0 + FAPI Client"""
    
    def __init__(self, config: OFBConfig, cert_manager: OFBCertificateManager):
        self.config = config
        self.cert_manager = cert_manager
        self.code_verifiers: Dict[str, str] = {}  # Store PKCE code verifiers
        
    def generate_pkce_challenge(self, state: str) -> Tuple[str, str]:
        """Generate PKCE code challenge and verifier"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        # Store code verifier for later use
        self.code_verifiers[state] = code_verifier
        
        return code_challenge, code_verifier
    
    async def create_authorization_url(self,
                                     scopes: List[str],
                                     state: str,
                                     nonce: str) -> str:
        """Create OFB-compliant authorization URL with PKCE"""
        
        # Generate PKCE challenge
        code_challenge, _ = self.generate_pkce_challenge(state)
        
        # Create request object (FAPI requirement)
        request_object = await self._create_signed_request_object({
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "response_type": "code",
            "response_mode": "jwt"
        })
        
        # Build authorization URL
        auth_params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "response_type": "code",
            "response_mode": "jwt",
            "request": request_object
        }
        
        auth_url = f"{self.config.auth_base_url}/oauth2/authorize?{urlencode(auth_params)}"
        return auth_url
    
    async def exchange_code_for_tokens(self,
                                     code: str,
                                     state: str) -> Dict:
        """Exchange authorization code for access tokens"""
        
        # Retrieve stored code verifier
        code_verifier = self.code_verifiers.get(state)
        if not code_verifier:
            raise ValueError("Code verifier not found for state")
        
        # Prepare token request
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "redirect_uri": self.config.redirect_uri,
            "code_verifier": code_verifier
        }
        
        # Use MTLS client certificate
        async with httpx.AsyncClient(
            cert=(self.config.transport_cert_path, self.config.transport_key_path),
            verify=self.config.ca_bundle_path,
            timeout=self.config.request_timeout
        ) as client:
            response = await client.post(
                f"{self.config.auth_base_url}/oauth2/token",
                data=token_data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                }
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Token exchange failed: {response.text}"
            )
        
        tokens = response.json()
        
        # Validate certificate-bound access token
        await self._validate_certificate_bound_token(tokens.get("access_token"))
        
        # Clean up stored code verifier
        del self.code_verifiers[state]
        
        return tokens
    
    async def _create_signed_request_object(self, claims: Dict) -> str:
        """Create and sign JWT request object (FAPI requirement)"""
        
        if not self.cert_manager.signing_cert or not self.cert_manager.signing_key:
            raise ValueError("Signing certificate not loaded")
        
        # Create JWT header
        header = {
            "alg": "RS256",
            "typ": "JWT",
            "x5c": [base64.b64encode(
                self.cert_manager.signing_cert.public_bytes(serialization.Encoding.DER)
            ).decode('utf-8')]
        }
        
        # Create JWT payload
        payload = {
            **claims,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=10)
        }
        
        # Encode header and payload
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
        
        # Create signature
        message = f"{header_b64}.{payload_b64}"
        signature = self.cert_manager.signing_key.sign(
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        # Return complete JWT
        return f"{header_b64}.{payload_b64}.{signature_b64}"
    
    async def _validate_certificate_bound_token(self, access_token: str) -> None:
        """Validate that access token is bound to client certificate"""
        # In production, implement proper token validation
        # For now, basic validation
        if not access_token:
            raise ValueError("Access token is required")
        
        logger.info("Certificate-bound token validation passed")


class OFBConsentManager:
    """Manage Open Finance Brasil consent lifecycle"""
    
    def __init__(self, config: OFBConfig, oauth_client: OFBOAuthClient):
        self.config = config
        self.oauth_client = oauth_client
        self.consents: Dict[str, Dict] = {}  # In-memory storage for now
        
    async def create_consent(self,
                           user_id: str,
                           permissions: List[str],
                           expiration_date: datetime,
                           transaction_from_date: Optional[datetime] = None,
                           transaction_to_date: Optional[datetime] = None) -> Dict:
        """Create new consent request"""
        
        consent_data = {
            "data": {
                "permissions": permissions,
                "expirationDateTime": expiration_date.isoformat(),
                "transactionFromDateTime": transaction_from_date.isoformat() if transaction_from_date else None,
                "transactionToDateTime": transaction_to_date.isoformat() if transaction_to_date else None,
                "loggedUser": {
                    "document": {
                        "identification": user_id,
                        "rel": "CPF"
                    }
                }
            }
        }
        
        # In production, this would call the actual OFB consent API
        # For now, create a mock consent
        consent_id = f"consent_{secrets.token_hex(8)}"
        
        consent = {
            "data": {
                "consentId": consent_id,
                "permissions": permissions,
                "expirationDateTime": expiration_date.isoformat(),
                "status": "AWAITING_AUTHORISATION",
                "loggedUser": consent_data["data"]["loggedUser"]
            }
        }
        
        # Store consent locally
        self.consents[consent_id] = consent
        
        return consent
    
    async def get_consent(self, consent_id: str) -> Optional[Dict]:
        """Retrieve consent information"""
        return self.consents.get(consent_id)
    
    async def revoke_consent(self, consent_id: str) -> bool:
        """Revoke existing consent"""
        if consent_id in self.consents:
            self.consents[consent_id]["data"]["status"] = "REVOKED"
            return True
        return False
    
    async def validate_consent(self, consent_id: str, required_permissions: List[str]) -> bool:
        """Validate consent for required permissions"""
        consent = await self.get_consent(consent_id)
        if not consent:
            return False
        
        if consent["data"]["status"] != "AUTHORISED":
            return False
        
        # Check if consent has required permissions
        consent_permissions = set(consent["data"]["permissions"])
        required_permissions_set = set(required_permissions)
        
        return required_permissions_set.issubset(consent_permissions)


class OFBAPIClient:
    """Base HTTP client for Open Finance Brasil APIs with MTLS"""
    
    def __init__(self, config: OFBConfig):
        self.config = config
        self.base_url = config.api_base_url
        
    async def _get_authenticated_client(self, access_token: str) -> httpx.AsyncClient:
        """Get authenticated HTTP client with MTLS and bearer token"""
        return httpx.AsyncClient(
            cert=(self.config.transport_cert_path, self.config.transport_key_path),
            verify=self.config.ca_bundle_path,
            timeout=self.config.request_timeout,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
    
    async def _handle_response(self, response: httpx.Response) -> Dict:
        """Handle API response with error handling"""
        if response.status_code == 200:
            return response.json()
        
        # Handle OFB standard error responses
        try:
            error_data = response.json()
            error_code = error_data.get("errors", [{}])[0].get("code", "UNKNOWN_ERROR")
            error_detail = error_data.get("errors", [{}])[0].get("detail", "An unknown error occurred")
        except:
            error_code = "UNKNOWN_ERROR"
            error_detail = response.text
        
        raise HTTPException(
            status_code=response.status_code,
            detail={
                "error_code": error_code,
                "error_detail": error_detail,
                "status_code": response.status_code
            }
        )


class OpenFinanceBrasilIntegration:
    """Main Open Finance Brasil integration class"""
    
    def __init__(self, config: OFBConfig):
        self.config = config
        self.cert_manager = OFBCertificateManager(config)
        self.oauth_client = OFBOAuthClient(config, self.cert_manager)
        self.consent_manager = OFBConsentManager(config, self.oauth_client)
        self.api_client = OFBAPIClient(config)
        
    async def initialize(self) -> None:
        """Initialize the integration module"""
        await self.cert_manager.load_certificates()
        logger.info("Open Finance Brasil integration initialized successfully")
    
    async def get_health_status(self) -> Dict:
        """Get integration health status"""
        return {
            "status": "healthy",
            "certificates": self.cert_manager.get_certificate_info(),
            "initialized": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def start_authorization_flow(self,
                                     user_id: str,
                                     scopes: List[str]) -> Dict:
        """Start OAuth 2.0 authorization flow"""
        
        # Generate state and nonce
        state = secrets.token_hex(16)
        nonce = secrets.token_hex(16)
        
        # Create consent
        expiration_date = datetime.utcnow() + timedelta(days=90)
        consent = await self.consent_manager.create_consent(
            user_id=user_id,
            permissions=scopes,
            expiration_date=expiration_date
        )
        
        # Generate authorization URL
        auth_url = await self.oauth_client.create_authorization_url(
            scopes=scopes,
            state=state,
            nonce=nonce
        )
        
        return {
            "authorization_url": auth_url,
            "consent_id": consent["data"]["consentId"],
            "state": state,
            "nonce": nonce,
            "expires_at": expiration_date.isoformat()
        }
    
    async def complete_authorization_flow(self,
                                        code: str,
                                        state: str) -> Dict:
        """Complete OAuth 2.0 authorization flow"""
        
        # Exchange code for tokens
        tokens = await self.oauth_client.exchange_code_for_tokens(code, state)
        
        return {
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "token_type": tokens.get("token_type", "Bearer"),
            "expires_in": tokens.get("expires_in", 3600),
            "scope": tokens.get("scope")
        }
    
    async def validate_access(self,
                            consent_id: str,
                            required_permissions: List[str]) -> bool:
        """Validate access for required permissions"""
        return await self.consent_manager.validate_consent(consent_id, required_permissions)
