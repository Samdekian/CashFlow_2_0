"""
Open Finance Brasil Payment API endpoints
Handles payment initiation, status, and history.
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ....services.ofb_payment_service import OFBPaymentService
from ....core.open_finance_brasil import OpenFinanceBrasilIntegration
from ....database import get_db

router = APIRouter()


# Request/Response models
class PIXPaymentRequest(BaseModel):
    consent_id: str
    access_token: str
    amount: Decimal
    recipient_key: str
    recipient_key_type: str = "CPF"
    description: str = ""
    scheduled_date: Optional[datetime] = None


class TEDDOCTransferRequest(BaseModel):
    consent_id: str
    access_token: str
    amount: Decimal
    recipient_bank_code: str
    recipient_agency: str
    recipient_account: str
    recipient_name: str
    transfer_type: str = "TED"
    description: str = ""
    scheduled_date: Optional[datetime] = None


class RecurringPaymentRequest(BaseModel):
    consent_id: str
    access_token: str
    payment_type: str
    amount: Decimal
    frequency: str
    start_date: datetime
    end_date: Optional[datetime] = None
    max_occurrences: Optional[int] = None
    payment_details: dict = {}


class PaymentHistoryQuery(BaseModel):
    consent_id: str
    access_token: str
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    payment_type: Optional[str] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 25


@router.post("/pix", response_model=dict)
async def initiate_pix_payment(
    request: PIXPaymentRequest,
    db=Depends(get_db)
):
    """Initiate a PIX instant payment."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        payment_service = OFBPaymentService(db, ofb_integration)
        
        result = await payment_service.initiate_pix_payment(
            consent_id=request.consent_id,
            access_token=request.access_token,
            amount=request.amount,
            recipient_key=request.recipient_key,
            recipient_key_type=request.recipient_key_type,
            description=request.description,
            scheduled_date=request.scheduled_date
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"PIX payment initiation failed: {str(e)}"
        )


@router.post("/ted-doc", response_model=dict)
async def initiate_ted_doc_transfer(
    request: TEDDOCTransferRequest,
    db=Depends(get_db)
):
    """Initiate a TED or DOC transfer."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        payment_service = OFBPaymentService(db, ofb_integration)
        
        result = await payment_service.initiate_ted_doc_transfer(
            consent_id=request.consent_id,
            access_token=request.access_token,
            amount=request.amount,
            recipient_bank_code=request.recipient_bank_code,
            recipient_agency=request.recipient_agency,
            recipient_account=request.recipient_account,
            recipient_name=request.recipient_name,
            transfer_type=request.transfer_type,
            description=request.description,
            scheduled_date=request.scheduled_date
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"{request.transfer_type} transfer initiation failed: {str(e)}"
        )


@router.post("/recurring", response_model=dict)
async def schedule_recurring_payment(
    request: RecurringPaymentRequest,
    db=Depends(get_db)
):
    """Schedule a recurring payment."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        payment_service = OFBPaymentService(db, ofb_integration)
        
        result = await payment_service.schedule_recurring_payment(
            consent_id=request.consent_id,
            access_token=request.access_token,
            payment_type=request.payment_type,
            amount=request.amount,
            frequency=request.frequency,
            start_date=request.start_date,
            end_date=request.end_date,
            max_occurrences=request.max_occurrences,
            **request.payment_details
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Recurring payment scheduling failed: {str(e)}"
        )


@router.get("/{payment_id}/status", response_model=dict)
async def get_payment_status(
    payment_id: str,
    consent_id: str = Query(..., description="Consent ID"),
    access_token: str = Query(..., description="Access token"),
    db=Depends(get_db)
):
    """Get the status of a payment."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        payment_service = OFBPaymentService(db, ofb_integration)
        
        result = await payment_service.get_payment_status(
            payment_id=payment_id,
            consent_id=consent_id,
            access_token=access_token
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Payment status retrieval failed: {str(e)}"
        )


@router.delete("/{payment_id}", response_model=dict)
async def cancel_payment(
    payment_id: str,
    consent_id: str = Query(..., description="Consent ID"),
    access_token: str = Query(..., description="Access token"),
    db=Depends(get_db)
):
    """Cancel a pending or scheduled payment."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        payment_service = OFBPaymentService(db, ofb_integration)
        
        result = await payment_service.cancel_payment(
            payment_id=payment_id,
            consent_id=consent_id,
            access_token=access_token
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Payment cancellation failed: {str(e)}"
        )


@router.get("/history", response_model=dict)
async def get_payment_history(
    consent_id: str = Query(..., description="Consent ID"),
    access_token: str = Query(..., description="Access token"),
    from_date: Optional[datetime] = Query(None, description="Start date"),
    to_date: Optional[datetime] = Query(None, description="End date"),
    payment_type: Optional[str] = Query(None, description="Payment type filter"),
    status: Optional[str] = Query(None, description="Status filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Page size"),
    db=Depends(get_db)
):
    """Get payment history with filtering and pagination."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        payment_service = OFBPaymentService(db, ofb_integration)
        
        result = await payment_service.get_payment_history(
            consent_id=consent_id,
            access_token=access_token,
            from_date=from_date,
            to_date=to_date,
            payment_type=payment_type,
            status=status,
            page=page,
            page_size=page_size
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Payment history retrieval failed: {str(e)}"
        )


@router.get("/types", response_model=dict)
async def get_payment_types():
    """Get available payment types and their characteristics."""
    return {
        "payment_types": [
            {
                "type": "PIX",
                "name": "PIX Instant Payment",
                "description": "Brazilian instant payment system",
                "processing_time": "Immediate (up to 10 seconds)",
                "max_amount": "No limit",
                "fees": "Usually free",
                "availability": "24/7"
            },
            {
                "type": "TED",
                "name": "TED Transfer",
                "description": "Electronic transfer between banks",
                "processing_time": "Same business day",
                "max_amount": "No limit",
                "fees": "Varies by bank",
                "availability": "Business hours only"
            },
            {
                "type": "DOC",
                "name": "DOC Transfer",
                "description": "Documented transfer between banks",
                "processing_time": "Next business day",
                "max_amount": "R$ 4,999.99",
                "fees": "Usually lower than TED",
                "availability": "Business hours only"
            }
        ],
        "recurring_options": [
            "daily",
            "weekly", 
            "monthly",
            "yearly"
        ]
    }
