"""
Transaction API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from ....database import get_db
from ....services.transaction_service import TransactionService
from ....schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    TransactionFilters,
    TransactionSummary,
    BulkTransactionOperation
)
from ....schemas.common import PaginationParams, SuccessResponse, ErrorResponse

router = APIRouter()


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db)
):
    """Create a new transaction."""
    try:
        transaction_service = TransactionService(db)
        transaction = transaction_service.create_transaction(transaction_data)
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=TransactionListResponse)
async def get_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    category_ids: Optional[List[UUID]] = Query(None, description="Category IDs to filter by"),
    transaction_types: Optional[List[str]] = Query(None, description="Transaction types to filter by"),
    min_amount: Optional[float] = Query(None, description="Minimum amount filter"),
    max_amount: Optional[float] = Query(None, description="Maximum amount filter"),
    accounts: Optional[List[str]] = Query(None, description="Account names to filter by"),
    tags: Optional[List[str]] = Query(None, description="Tags to filter by"),
    is_recurring: Optional[bool] = Query(None, description="Filter by recurring status"),
    search: Optional[str] = Query(None, description="Search in description and notes"),
    db: Session = Depends(get_db)
):
    """Get transactions with filtering and pagination."""
    try:
        # Build filters
        filters = None
        if any([date_from, date_to, category_ids, transaction_types, min_amount, max_amount, accounts, tags, is_recurring, search]):
            from datetime import date
            from ....schemas.common import DateRange
            
            filters = TransactionFilters()
            
            if date_from and date_to:
                filters.date_range = DateRange(
                    start_date=date.fromisoformat(date_from),
                    end_date=date.fromisoformat(date_to)
                )
            
            filters.category_ids = category_ids
            filters.transaction_types = transaction_types
            filters.min_amount = min_amount
            filters.max_amount = max_amount
            filters.accounts = accounts
            filters.tags = tags
            filters.is_recurring = is_recurring
            filters.search_query = search
        
        # Build pagination
        pagination = PaginationParams(page=page, size=size)
        
        # Get transactions
        transaction_service = TransactionService(db)
        result = transaction_service.get_transactions(filters=filters, pagination=pagination)
        
        return TransactionListResponse(
            transactions=result.items,
            total=result.total,
            page=result.page,
            size=result.size,
            pages=result.pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific transaction by ID."""
    try:
        transaction_service = TransactionService(db)
        transaction = transaction_service.get_transaction(transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    update_data: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing transaction."""
    try:
        transaction_service = TransactionService(db)
        transaction = transaction_service.update_transaction(transaction_id, update_data)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return transaction
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{transaction_id}", response_model=SuccessResponse)
async def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a transaction."""
    try:
        transaction_service = TransactionService(db)
        success = transaction_service.delete_transaction(transaction_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return SuccessResponse(message="Transaction deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/search/{query}", response_model=List[TransactionResponse])
async def search_transactions(
    query: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Search transactions by description and notes."""
    try:
        transaction_service = TransactionService(db)
        transactions = transaction_service.search_transactions(query, limit)
        return transactions
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/summary/overview", response_model=TransactionSummary)
async def get_transaction_summary(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get transaction summary statistics."""
    try:
        transaction_service = TransactionService(db)
        
        date_range = None
        if date_from and date_to:
            from datetime import date
            date_range = (date.fromisoformat(date_from), date.fromisoformat(date_to))
        
        summary = transaction_service.get_transaction_summary(date_range)
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/bulk", response_model=dict)
async def bulk_transaction_operation(
    operation_data: BulkTransactionOperation,
    db: Session = Depends(get_db)
):
    """Perform bulk operations on transactions."""
    try:
        transaction_service = TransactionService(db)
        results = transaction_service.bulk_operation(operation_data)
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/category/{category_id}", response_model=List[TransactionResponse])
async def get_transactions_by_category(
    category_id: UUID,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get transactions for a specific category."""
    try:
        transaction_service = TransactionService(db)
        transactions = transaction_service.get_transactions_by_category(category_id, limit)
        return transactions
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/recent/list", response_model=List[TransactionResponse])
async def get_recent_transactions(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Get recent transactions."""
    try:
        transaction_service = TransactionService(db)
        transactions = transaction_service.get_recent_transactions(limit)
        return transactions
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/period", response_model=List[dict])
async def get_transaction_statistics_by_period(
    date_from: str = Query(..., description="Start date (YYYY-MM-DD)"),
    date_to: str = Query(..., description="End date (YYYY-MM-DD)"),
    group_by: str = Query("month", description="Group by: day, week, or month"),
    db: Session = Depends(get_db)
):
    """Get transaction statistics grouped by period."""
    try:
        from datetime import date
        
        if group_by not in ["day", "week", "month"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="group_by must be 'day', 'week', or 'month'"
            )
        
        transaction_service = TransactionService(db)
        start_date = date.fromisoformat(date_from)
        end_date = date.fromisoformat(date_to)
        
        statistics = transaction_service.get_transaction_statistics_by_period(
            start_date, end_date, group_by
        )
        return statistics
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/duplicates/check", response_model=List[TransactionResponse])
async def check_duplicate_transactions(
    date: str = Query(..., description="Transaction date (YYYY-MM-DD)"),
    amount: float = Query(..., description="Transaction amount"),
    description: str = Query(..., description="Transaction description"),
    tolerance_days: int = Query(1, ge=0, le=7, description="Tolerance for date matching"),
    db: Session = Depends(get_db)
):
    """Check for potential duplicate transactions."""
    try:
        from datetime import date as date_type
        
        transaction_service = TransactionService(db)
        transaction_date = date_type.fromisoformat(date)
        
        duplicates = transaction_service.detect_duplicate_transactions(
            transaction_date, amount, description, tolerance_days
        )
        return duplicates
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
