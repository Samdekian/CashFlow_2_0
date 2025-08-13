"""
Open Finance Brasil API Endpoints
Phase 2: OAuth 2.0 + FAPI + Consent Management
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from ....core.open_finance_brasil import (
    OFBConfig,
    OpenFinanceBrasilIntegration,
)
from ....config_ofb import ofb_settings
from ....database import get_db
from ....schemas.common import PaginationParams
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/open-finance", tags=["Open Finance Brasil"])


# Pydantic Models for API
class OFBConnectionRequest(BaseModel):
    """Request to connect to bank via Open Finance Brasil"""
    
    user_id: str = Field(..., description="User CPF or identification")
    scopes: List[str] = Field(
        default=["accounts", "transactions"],
        description="Requested permissions"
    )
    bank_code: Optional[str] = Field(None, description="Specific bank code")
    expiration_days: int = Field(default=90, description="Consent expiration in days")


class OFBConnectionResponse(BaseModel):
    """Response for bank connection initiation"""
    
    authorization_url: str = Field(..., description="OAuth authorization URL")
    consent_id: str = Field(..., description="Consent ID for tracking")
    state: str = Field(..., description="OAuth state parameter")
    nonce: str = Field(..., description="OAuth nonce parameter")
    expires_at: str = Field(..., description="Consent expiration timestamp")
    scopes: List[str] = Field(..., description="Requested permissions")


class OFBCallbackRequest(BaseModel):
    """OAuth callback request"""
    
    code: str = Field(..., description="Authorization code")
    state: str = Field(..., description="OAuth state parameter")


class OFBCallbackResponse(BaseModel):
    """OAuth callback response"""
    
    status: str = Field(..., description="Connection status")
    consent_id: str = Field(..., description="Consent ID")
    access_token_expires_at: int = Field(..., description="Token expiration in seconds")
    scopes: List[str] = Field(..., description="Granted permissions")


class OFBConsentInfo(BaseModel):
    """Consent information"""
    
    consent_id: str = Field(..., description="Consent ID")
    status: str = Field(..., description="Consent status")
    permissions: List[str] = Field(..., description="Granted permissions")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: str = Field(..., description="Expiration timestamp")
    user_id: str = Field(..., description="User identification")


class OFBHealthResponse(BaseModel):
    """OFB integration health status"""
    
    status: str = Field(..., description="Integration status")
    certificates: dict = Field(..., description="Certificate information")
    initialized: bool = Field(..., description="Initialization status")
    timestamp: str = Field(..., description="Health check timestamp")
    configuration: dict = Field(..., description="Configuration status")


# OFB Integration instance
ofb_integration: Optional[OpenFinanceBrasilIntegration] = None


async def get_ofb_integration() -> OpenFinanceBrasilIntegration:
    """Get OFB integration instance"""
    global ofb_integration
    
    if ofb_integration is None:
        if not ofb_settings.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Open Finance Brasil integration not configured"
            )
        
        # Create OFB configuration
        cert_paths = ofb_settings.get_certificate_paths()
        endpoints = ofb_settings.get_endpoints()
        
        config = OFBConfig(
            client_id=ofb_settings.ofb_client_id,
            client_secret=ofb_settings.ofb_client_secret,
            redirect_uri=ofb_settings.ofb_redirect_uri,
            **endpoints,
            **cert_paths,
            request_timeout=ofb_settings.ofb_request_timeout,
            max_retries=ofb_settings.ofb_max_retries,
            rate_limit_requests=ofb_settings.ofb_rate_limit_requests,
            rate_limit_window=ofb_settings.ofb_rate_limit_window
        )
        
        ofb_integration = OpenFinanceBrasilIntegration(config)
        await ofb_integration.initialize()
    
    return ofb_integration


@router.get("/health", response_model=OFBHealthResponse)
async def get_ofb_health(
    ofb: OpenFinanceBrasilIntegration = Depends(get_ofb_integration)
):
    """Get Open Finance Brasil integration health status"""
    
    try:
        health_status = await ofb.get_health_status()
        
        # Add configuration status
        health_status["configuration"] = {
            "enabled": ofb_settings.ofb_enabled,
            "sandbox_mode": ofb_settings.ofb_sandbox_mode,
            "mock_mode": ofb_settings.ofb_mock_mode,
            "client_configured": bool(ofb_settings.ofb_client_id and ofb_settings.ofb_client_secret),
            "certificates_exist": all(
                os.path.exists(path) 
                for path in ofb_settings.get_certificate_paths().values()
            )
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"OFB health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OFB integration health check failed: {str(e)}"
        )


@router.post("/connect", response_model=OFBConnectionResponse)
async def initiate_bank_connection(
    request: OFBConnectionRequest,
    ofb: OpenFinanceBrasilIntegration = Depends(get_ofb_integration)
):
    """Initiate bank connection via Open Finance Brasil"""
    
    try:
        # Validate scopes
        valid_scopes = ["accounts", "transactions", "payments", "consents"]
        invalid_scopes = [scope for scope in request.scopes if scope not in valid_scopes]
        if invalid_scopes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid scopes: {invalid_scopes}. Valid scopes: {valid_scopes}"
            )
        
        # Calculate expiration date
        expiration_date = datetime.utcnow() + timedelta(days=request.expiration_days)
        
        # Start authorization flow
        auth_flow = await ofb.start_authorization_flow(
            user_id=request.user_id,
            scopes=request.scopes
        )
        
        logger.info(f"Bank connection initiated for user {request.user_id}")
        
        return OFBConnectionResponse(
            authorization_url=auth_flow["authorization_url"],
            consent_id=auth_flow["consent_id"],
            state=auth_flow["state"],
            nonce=auth_flow["nonce"],
            expires_at=auth_flow["expires_at"],
            scopes=request.scopes
        )
        
    except Exception as e:
        logger.error(f"Failed to initiate bank connection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate bank connection: {str(e)}"
        )


@router.get("/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code"),
    state: str = Query(..., description="OAuth state parameter"),
    ofb: OpenFinanceBrasilIntegration = Depends(get_ofb_integration)
):
    """Handle OAuth callback from bank"""
    
    try:
        # Complete authorization flow
        tokens = await ofb.complete_authorization_flow(code, state)
        
        logger.info(f"OAuth callback completed successfully for state {state}")
        
        return OFBCallbackResponse(
            status="connected",
            consent_id="",  # Would be retrieved from stored state
            access_token_expires_at=tokens["expires_in"],
            scopes=tokens["scope"].split(" ") if tokens.get("scope") else []
        )
        
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        )


@router.get("/consents/{consent_id}", response_model=OFBConsentInfo)
async def get_consent_info(
    consent_id: str,
    ofb: OpenFinanceBrasilIntegration = Depends(get_ofb_integration)
):
    """Get consent information"""
    
    try:
        consent = await ofb.consent_manager.get_consent(consent_id)
        
        if not consent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consent not found"
            )
        
        return OFBConsentInfo(
            consent_id=consent["data"]["consentId"],
            status=consent["data"]["status"],
            permissions=consent["data"]["permissions"],
            created_at=datetime.utcnow().isoformat(),  # Would be from actual consent
            expires_at=consent["data"]["expirationDateTime"],
            user_id=consent["data"]["loggedUser"]["document"]["identification"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get consent info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get consent info: {str(e)}"
        )


@router.delete("/consents/{consent_id}")
async def revoke_consent(
    consent_id: str,
    ofb: OpenFinanceBrasilIntegration = Depends(get_ofb_integration)
):
    """Revoke consent"""
    
    try:
        success = await ofb.consent_manager.revoke_consent(consent_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consent not found"
            )
        
        logger.info(f"Consent {consent_id} revoked successfully")
        
        return {"status": "revoked", "consent_id": consent_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke consent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke consent: {str(e)}"
        )


@router.get("/consents")
async def list_consents(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, description="Filter by consent status"),
    pagination: PaginationParams = Depends(),
    ofb: OpenFinanceBrasilIntegration = Depends(get_ofb_integration)
):
    """List consents with optional filtering"""
    
    try:
        # In production, this would query the database
        # For now, return mock data
        consents = []
        
        # Mock consent data
        if ofb.consent_manager.consents:
            for consent_id, consent_data in ofb.consent_manager.consents.items():
                if user_id and consent_data["data"]["loggedUser"]["document"]["identification"] != user_id:
                    continue
                if status and consent_data["data"]["status"] != status:
                    continue
                
                consents.append({
                    "consent_id": consent_id,
                    "status": consent_data["data"]["status"],
                    "permissions": consent_data["data"]["permissions"],
                    "user_id": consent_data["data"]["loggedUser"]["document"]["identification"],
                    "expires_at": consent_data["data"]["expirationDateTime"]
                })
        
        # Apply pagination
        total = len(consents)
        start = (pagination.page - 1) * pagination.size
        end = start + pagination.size
        paginated_consents = consents[start:end]
        
        return {
            "consents": paginated_consents,
            "pagination": {
                "total": total,
                "page": pagination.page,
                "size": pagination.size,
                "pages": (total + pagination.size - 1) // pagination.size
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to list consents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list consents: {str(e)}"
        )


@router.post("/validate-access")
async def validate_access(
    consent_id: str = Query(..., description="Consent ID"),
    required_permissions: List[str] = Query(..., description="Required permissions"),
    ofb: OpenFinanceBrasilIntegration = Depends(get_ofb_integration)
):
    """Validate access for required permissions"""
    
    try:
        has_access = await ofb.validate_access(consent_id, required_permissions)
        
        return {
            "consent_id": consent_id,
            "required_permissions": required_permissions,
            "has_access": has_access,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to validate access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate access: {str(e)}"
        )


@router.get("/configuration")
async def get_ofb_configuration():
    """Get Open Finance Brasil configuration status"""
    
    try:
        cert_paths = ofb_settings.get_certificate_paths()
        endpoints = ofb_settings.get_endpoints()
        
        return {
            "enabled": ofb_settings.ofb_enabled,
            "sandbox_mode": ofb_settings.ofb_sandbox_mode,
            "mock_mode": ofb_settings.ofb_mock_mode,
            "client_configured": bool(ofb_settings.ofb_client_id and ofb_settings.ofb_client_secret),
            "certificates": {
                "transport_cert": {
                    "path": cert_paths["transport_cert_path"],
                    "exists": os.path.exists(cert_paths["transport_cert_path"])
                },
                "transport_key": {
                    "path": cert_paths["transport_key_path"],
                    "exists": os.path.exists(cert_paths["transport_key_path"])
                },
                "signing_cert": {
                    "path": cert_paths["signing_cert_path"],
                    "exists": os.path.exists(cert_paths["signing_cert_path"])
                },
                "signing_key": {
                    "path": cert_paths["signing_key_path"],
                    "exists": os.path.exists(cert_paths["signing_key_path"])
                },
                "ca_bundle": {
                    "path": cert_paths["ca_bundle_path"],
                    "exists": os.path.exists(cert_paths["ca_bundle_path"])
                }
            },
            "endpoints": endpoints,
            "timeouts": {
                "request_timeout": ofb_settings.ofb_request_timeout,
                "max_retries": ofb_settings.ofb_max_retries
            },
            "rate_limiting": {
                "requests_per_window": ofb_settings.ofb_rate_limit_requests,
                "window_seconds": ofb_settings.ofb_rate_limit_window
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get OFB configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OFB configuration: {str(e)}"
        )
