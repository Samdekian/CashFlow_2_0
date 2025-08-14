"""
Open Finance Brasil Multi-Bank API endpoints
Handles multi-bank connections, aggregation, and management.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ....services.ofb_multi_bank_service import OFBMultiBankService
from ....core.open_finance_brasil import OpenFinanceBrasilIntegration
from ....database import get_db

router = APIRouter()


# Request/Response models
class BankConnectionRequest(BaseModel):
    bank_code: str
    bank_name: str
    consent_id: str
    access_token: str
    user_id: str


class BankDisconnectionRequest(BaseModel):
    connection_id: str
    user_id: str


@router.post("/connect", response_model=dict)
async def connect_bank(
    request: BankConnectionRequest,
    db=Depends(get_db)
):
    """Connect a new bank to the user's account."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        result = await multi_bank_service.connect_bank(
            bank_code=request.bank_code,
            bank_name=request.bank_name,
            consent_id=request.consent_id,
            access_token=request.access_token,
            user_id=request.user_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Bank connection failed: {str(e)}"
        )


@router.post("/disconnect", response_model=dict)
async def disconnect_bank(
    request: BankDisconnectionRequest,
    db=Depends(get_db)
):
    """Disconnect a bank from the user's account."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        result = await multi_bank_service.disconnect_bank(
            connection_id=request.connection_id,
            user_id=request.user_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Bank disconnection failed: {str(e)}"
        )


@router.get("/connections", response_model=dict)
async def get_connected_banks(
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db)
):
    """Get all connected banks for a user."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        result = await multi_bank_service.get_connected_banks(user_id=user_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get connected banks: {str(e)}"
        )


@router.get("/balance/aggregated", response_model=dict)
async def get_aggregated_balance(
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db)
):
    """Get aggregated balance across all connected banks."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        result = await multi_bank_service.get_aggregated_balance(user_id=user_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get aggregated balance: {str(e)}"
        )


@router.post("/sync/all", response_model=dict)
async def sync_all_banks(
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db)
):
    """Sync all connected banks for a user."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        result = await multi_bank_service.sync_all_banks(user_id=user_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to sync all banks: {str(e)}"
        )


@router.get("/health/status", response_model=dict)
async def get_bank_health_status(
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db)
):
    """Get health status of all connected banks."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        result = await multi_bank_service.get_bank_health_status(user_id=user_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get bank health status: {str(e)}"
        )


@router.get("/summary", response_model=dict)
async def get_multi_bank_summary(
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db)
):
    """Get comprehensive summary of multi-bank status."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        # Get all relevant data
        connections = await multi_bank_service.get_connected_banks(user_id)
        balance = await multi_bank_service.get_aggregated_balance(user_id)
        health = await multi_bank_service.get_bank_health_status(user_id)
        
        # Calculate summary metrics
        total_balance = balance["total_balance"]
        active_banks = len(connections["active_connections"])
        total_accounts = connections["summary"]["total_accounts"]
        
        # Determine overall status
        if health["banks_needing_attention"] == 0:
            overall_status = "HEALTHY"
        elif health["banks_needing_attention"] < health["total_banks"]:
            overall_status = "ATTENTION_NEEDED"
        else:
            overall_status = "CRITICAL"
        
        summary = {
            "overall_status": overall_status,
            "total_banks": connections["total_connections"],
            "active_banks": active_banks,
            "total_accounts": total_accounts,
            "total_balance": total_balance,
            "currency": "BRL",
            "last_sync": connections["summary"]["last_sync"],
            "health_summary": {
                "healthy_banks": health["healthy_banks"],
                "banks_needing_attention": health["banks_needing_attention"]
            },
            "summary_date": datetime.utcnow().isoformat()
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get multi-bank summary: {str(e)}"
        )


@router.get("/banks/available", response_model=dict)
async def get_available_banks():
    """Get list of available banks for connection."""
    return {
        "available_banks": [
            {
                "code": "001",
                "name": "Banco do Brasil",
                "type": "Public",
                "features": ["PIX", "TED", "DOC", "Investment Accounts"],
                "connection_status": "Available"
            },
            {
                "code": "341",
                "name": "Itaú Unibanco",
                "type": "Private",
                "features": ["PIX", "TED", "DOC", "Credit Cards", "Investment Accounts"],
                "connection_status": "Available"
            },
            {
                "code": "237",
                "name": "Bradesco",
                "type": "Private",
                "features": ["PIX", "TED", "DOC", "Insurance", "Investment Accounts"],
                "connection_status": "Available"
            },
            {
                "code": "104",
                "name": "Caixa Econômica Federal",
                "type": "Public",
                "features": ["PIX", "TED", "DOC", "Social Benefits", "Investment Accounts"],
                "connection_status": "Available"
            },
            {
                "code": "033",
                "name": "Santander",
                "type": "Private",
                "features": ["PIX", "TED", "DOC", "International Banking", "Investment Accounts"],
                "connection_status": "Available"
            }
        ],
        "connection_features": [
            "Real-time balance updates",
            "Transaction synchronization",
            "Multi-account management",
            "Automated data sync",
            "Secure API access"
        ],
        "last_updated": datetime.utcnow().isoformat()
    }
