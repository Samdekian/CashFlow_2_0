"""
Open Finance Brasil Account Information API Endpoints
Phase 3: Account Discovery, Balance Retrieval, and Transaction Import
"""

import logging
from datetime import date, timedelta, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ....database import get_db
from ....services.ofb_account_service import OFBAccountService
from ....schemas.common import PaginationParams

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ofb-accounts", tags=["Open Finance Brasil Accounts"])


# Pydantic Models for API
class OFBAccountInfo(BaseModel):
    """OFB Account Information"""
    
    account_id: str = Field(..., description="Unique account identifier")
    type: str = Field(..., description="Account type (CACC, SVGS, etc.)")
    subtype: str = Field(..., description="Account subtype")
    currency: str = Field(..., description="Account currency")
    brand_name: str = Field(..., description="Bank brand name")
    company_cnpj: str = Field(..., description="Bank CNPJ")
    number: str = Field(..., description="Account number")
    check_digit: str = Field(..., description="Account check digit")
    agency_number: str = Field(..., description="Agency number")
    agency_check_digit: str = Field(..., description="Agency check digit")
    status: str = Field(..., description="Account status")


class OFBAccountBalance(BaseModel):
    """OFB Account Balance Information"""
    
    available_amount: str = Field(..., description="Available balance")
    available_amount_currency: str = Field(..., description="Available balance currency")
    blocked_amount: str = Field(..., description="Blocked amount")
    blocked_amount_currency: str = Field(..., description="Blocked amount currency")
    automatically_invested_amount: str = Field(..., description="Automatically invested amount")
    automatically_invested_amount_currency: str = Field(..., description="Invested amount currency")
    last_updated: str = Field(..., description="Last update timestamp")


class OFBTransaction(BaseModel):
    """OFB Transaction Information"""
    
    transaction_id: str = Field(..., description="Transaction identifier")
    booking_date: str = Field(..., description="Transaction date")
    amount: str = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Transaction currency")
    credit_debit_type: str = Field(..., description="Credit or debit")
    transaction_name: str = Field(..., description="Transaction description")
    reference_number: Optional[str] = Field(None, description="Reference number")
    type: Optional[str] = Field(None, description="Transaction type")
    transaction_category: Optional[str] = Field(None, description="Transaction category")


class OFBTransactionsResponse(BaseModel):
    """OFB Transactions Response"""
    
    transactions: List[OFBTransaction] = Field(..., description="List of transactions")
    pagination: dict = Field(..., description="Pagination information")
    date_range: dict = Field(..., description="Date range information")


class OFBImportRequest(BaseModel):
    """Request to import transactions from OFB"""
    
    account_id: str = Field(..., description="Account ID to import from")
    consent_id: str = Field(..., description="Consent ID for access")
    access_token: str = Field(..., description="Access token for API calls")
    from_date: Optional[str] = Field(None, description="Start date for import (YYYY-MM-DD)")
    to_date: Optional[str] = Field(None, description="End date for import (YYYY-MM-DD)")
    auto_categorize: bool = Field(default=True, description="Auto-categorize transactions")


class OFBImportResponse(BaseModel):
    """Response for transaction import"""
    
    status: str = Field(..., description="Import status")
    imported_count: int = Field(..., description="Number of transactions imported")
    skipped_count: int = Field(..., description="Number of transactions skipped")
    total_processed: int = Field(..., description="Total transactions processed")
    errors: List[str] = Field(..., description="List of errors during import")
    account_id: str = Field(..., description="Account ID processed")
    date_range: dict = Field(..., description="Date range processed")


class OFBSyncRequest(BaseModel):
    """Request to sync account data"""
    
    account_id: str = Field(..., description="Account ID to sync")
    consent_id: str = Field(..., description="Consent ID for access")
    access_token: str = Field(..., description="Access token for API calls")


class OFBSyncResponse(BaseModel):
    """Response for account sync"""
    
    status: str = Field(..., description="Sync status")
    account_id: str = Field(..., description="Account ID synced")
    balance: dict = Field(..., description="Account balance information")
    recent_transactions: int = Field(..., description="Number of recent transactions")
    import_result: dict = Field(..., description="Transaction import results")
    sync_timestamp: str = Field(..., description="Sync completion timestamp")


@router.get("/discover", response_model=List[OFBAccountInfo])
async def discover_accounts(
    consent_id: str = Query(..., description="Consent ID for access"),
    access_token: str = Query(..., description="Access token for API calls"),
    db: Session = Depends(get_db)
):
    """Discover bank accounts for a user"""
    
    try:
        account_service = OFBAccountService(db)
        accounts = await account_service.discover_accounts(consent_id, access_token)
        
        # Transform to response format
        account_list = []
        for account in accounts:
            account_list.append(OFBAccountInfo(
                account_id=account["accountId"],
                type=account["type"],
                subtype=account["subtype"],
                currency=account["currency"],
                brand_name=account["brandName"],
                company_cnpj=account["companyCnpj"],
                number=account["number"],
                check_digit=account["checkDigit"],
                agency_number=account["agencyNumber"],
                agency_check_digit=account["agencyCheckDigit"],
                status=account["status"]
            ))
        
        return account_list
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account discovery failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account discovery failed: {str(e)}"
        )


@router.get("/{account_id}/balance", response_model=OFBAccountBalance)
async def get_account_balance(
    account_id: str,
    consent_id: str = Query(..., description="Consent ID for access"),
    access_token: str = Query(..., description="Access token for API calls"),
    db: Session = Depends(get_db)
):
    """Get account balance information"""
    
    try:
        account_service = OFBAccountService(db)
        balance = await account_service.get_account_balances(account_id, consent_id, access_token)
        
        return OFBAccountBalance(
            available_amount=balance["availableAmount"],
            available_amount_currency=balance["availableAmountCurrency"],
            blocked_amount=balance["blockedAmount"],
            blocked_amount_currency=balance["blockedAmountCurrency"],
            automatically_invested_amount=balance["automaticallyInvestedAmount"],
            automatically_invested_amount_currency=balance["automaticallyInvestedAmountCurrency"],
            last_updated=balance["lastUpdated"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Balance retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Balance retrieval failed: {str(e)}"
        )


@router.get("/{account_id}/transactions", response_model=OFBTransactionsResponse)
async def get_account_transactions(
    account_id: str,
    consent_id: str = Query(..., description="Consent ID for access"),
    access_token: str = Query(..., description="Access token for API calls"),
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """Get account transactions"""
    
    try:
        # Parse dates
        parsed_from_date = None
        parsed_to_date = None
        
        if from_date:
            parsed_from_date = date.fromisoformat(from_date)
        if to_date:
            parsed_to_date = date.fromisoformat(to_date)
        
        account_service = OFBAccountService(db)
        transactions_data = await account_service.get_account_transactions(
            account_id=account_id,
            consent_id=consent_id,
            access_token=access_token,
            from_date=parsed_from_date,
            to_date=parsed_to_date,
            page_size=pagination.size,
            page=pagination.page
        )
        
        # Transform transactions to response format
        transactions = []
        for txn in transactions_data["transactions"]:
            transactions.append(OFBTransaction(
                transaction_id=txn["transactionId"],
                booking_date=txn["bookingDate"],
                amount=txn["amount"],
                currency=txn["currency"],
                credit_debit_type=txn["creditDebitType"],
                transaction_name=txn["transactionName"],
                reference_number=txn.get("referenceNumber"),
                type=txn.get("type"),
                transaction_category=txn.get("transactionCategory")
            ))
        
        return OFBTransactionsResponse(
            transactions=transactions,
            pagination=transactions_data["pagination"],
            date_range=transactions_data["dateRange"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transaction retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction retrieval failed: {str(e)}"
        )


@router.post("/{account_id}/import", response_model=OFBImportResponse)
async def import_transactions(
    account_id: str,
    request: OFBImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Import transactions from OFB to local database"""
    
    try:
        # Parse dates
        parsed_from_date = None
        parsed_to_date = None
        
        if request.from_date:
            parsed_from_date = date.fromisoformat(request.from_date)
        if request.to_date:
            parsed_to_date = date.fromisoformat(request.to_date)
        
        account_service = OFBAccountService(db)
        import_result = await account_service.import_transactions(
            account_id=account_id,
            consent_id=request.consent_id,
            access_token=request.access_token,
            from_date=parsed_from_date,
            to_date=parsed_to_date,
            auto_categorize=request.auto_categorize
        )
        
        return OFBImportResponse(
            status=import_result["status"],
            imported_count=import_result["imported_count"],
            skipped_count=import_result["skipped_count"],
            total_processed=import_result["total_processed"],
            errors=import_result["errors"],
            account_id=import_result["account_id"],
            date_range=import_result["date_range"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transaction import failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transaction import failed: {str(e)}"
        )


@router.post("/{account_id}/sync", response_model=OFBSyncResponse)
async def sync_account_data(
    account_id: str,
    request: OFBSyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Synchronize all account data (balance + recent transactions)"""
    
    try:
        account_service = OFBAccountService(db)
        sync_result = await account_service.sync_account_data(
            account_id=account_id,
            consent_id=request.consent_id,
            access_token=request.access_token
        )
        
        return OFBSyncResponse(
            status=sync_result["status"],
            account_id=sync_result["account_id"],
            balance=sync_result["balance"],
            recent_transactions=sync_result["recent_transactions"],
            import_result=sync_result["import_result"],
            sync_timestamp=sync_result["sync_timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account sync failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account sync failed: {str(e)}"
        )


@router.get("/{account_id}/summary")
async def get_account_summary(
    account_id: str,
    consent_id: str = Query(..., description="Consent ID for access"),
    access_token: str = Query(..., description="Access token for API calls"),
    db: Session = Depends(get_db)
):
    """Get comprehensive account summary"""
    
    try:
        account_service = OFBAccountService(db)
        
        # Get account balance
        balance = await account_service.get_account_balances(account_id, consent_id, access_token)
        
        # Get recent transactions (last 30 days)
        from_date = date.today() - timedelta(days=30)
        transactions_data = await account_service.get_account_transactions(
            account_id=account_id,
            consent_id=consent_id,
            access_token=access_token,
            from_date=from_date,
            page_size=100
        )
        
        # Calculate summary statistics
        total_income = 0
        total_expenses = 0
        
        for txn in transactions_data["transactions"]:
            amount = float(txn["amount"])
            if txn["creditDebitType"] == "CREDITO":
                total_income += amount
            else:
                total_expenses += amount
        
        net_flow = total_income - total_expenses
        
        return {
            "account_id": account_id,
            "balance": balance,
            "summary": {
                "total_income": f"{total_income:.2f}",
                "total_expenses": f"{total_expenses:.2f}",
                "net_flow": f"{net_flow:.2f}",
                "transaction_count": len(transactions_data["transactions"]),
                "period": {
                    "from": from_date.isoformat(),
                    "to": date.today().isoformat()
                }
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account summary failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account summary failed: {str(e)}"
        )
