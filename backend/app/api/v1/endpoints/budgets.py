"""
Budget management endpoints for the CashFlow Monitor API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from ....database import get_db
from ....schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetListResponse,
    BudgetProgressResponse,
    BudgetAlertResponse,
    BudgetFilters,
    PaginationParams
)
from ....services.budget_service import BudgetService
from ....core.open_finance_standards import validate_budget_category

# Create router
router = APIRouter()

# Initialize service
budget_service = BudgetService()


@router.post("/", response_model=BudgetResponse, status_code=201)
async def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new budget for a specific category.
    
    Args:
        budget_data: Budget creation data
        db: Database session
        
    Returns:
        Created budget with full details
        
    Raises:
        HTTPException: If category not found or validation fails
    """
    try:
        # Validate category exists and is compatible with budget
        if not validate_budget_category(budget_data.category_id, db):
            raise HTTPException(
                status_code=400,
                detail="Invalid category for budget creation. Only expense categories are allowed."
            )
        
        budget = budget_service.create_budget(budget_data, db)
        return budget
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create budget: {str(e)}")


@router.get("/", response_model=BudgetListResponse)
async def list_budgets(
    filters: BudgetFilters = Depends(),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    List all budgets with optional filtering and pagination.
    
    Args:
        filters: Budget filtering criteria
        pagination: Pagination parameters
        db: Database session
        
    Returns:
        Paginated list of budgets
    """
    try:
        budgets = budget_service.get_budgets(filters, pagination, db)
        return budgets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve budgets: {str(e)}")


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific budget by ID.
    
    Args:
        budget_id: Budget unique identifier
        db: Database session
        
    Returns:
        Budget details
        
    Raises:
        HTTPException: If budget not found
    """
    try:
        budget = budget_service.get_budget(budget_id, db)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return budget
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve budget: {str(e)}")


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: UUID,
    budget_data: BudgetUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing budget.
    
    Args:
        budget_id: Budget unique identifier
        budget_data: Budget update data
        db: Database session
        
    Returns:
        Updated budget details
        
    Raises:
        HTTPException: If budget not found or update fails
    """
    try:
        budget = budget_service.update_budget(budget_id, budget_data, db)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return budget
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update budget: {str(e)}")


@router.delete("/{budget_id}", status_code=204)
async def delete_budget(
    budget_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a budget.
    
    Args:
        budget_id: Budget unique identifier
        db: Database session
        
    Raises:
        HTTPException: If budget not found or deletion fails
    """
    try:
        success = budget_service.delete_budget(budget_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Budget not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete budget: {str(e)}")


@router.get("/{budget_id}/progress", response_model=BudgetProgressResponse)
async def get_budget_progress(
    budget_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get budget progress and spending analysis.
    
    Args:
        budget_id: Budget unique identifier
        db: Database session
        
    Returns:
        Budget progress with spending details
        
    Raises:
        HTTPException: If budget not found
    """
    try:
        progress = budget_service.get_budget_progress(budget_id, db)
        if not progress:
            raise HTTPException(status_code=404, detail="Budget not found")
        return progress
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve budget progress: {str(e)}")


@router.get("/{budget_id}/alerts", response_model=List[BudgetAlertResponse])
async def get_budget_alerts(
    budget_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get budget alerts and notifications.
    
    Args:
        budget_id: Budget unique identifier
        db: Database session
        
    Returns:
        List of budget alerts
        
    Raises:
        HTTPException: If budget not found
    """
    try:
        alerts = budget_service.get_budget_alerts(budget_id, db)
        if alerts is None:
            raise HTTPException(status_code=404, detail="Budget not found")
        return alerts
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve budget alerts: {str(e)}")


@router.post("/{budget_id}/activate", response_model=BudgetResponse)
async def activate_budget(
    budget_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Activate a budget.
    
    Args:
        budget_id: Budget unique identifier
        db: Database session
        
    Returns:
        Activated budget details
        
    Raises:
        HTTPException: If budget not found or activation fails
    """
    try:
        budget = budget_service.activate_budget(budget_id, db)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return budget
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate budget: {str(e)}")


@router.post("/{budget_id}/deactivate", response_model=BudgetResponse)
async def deactivate_budget(
    budget_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Deactivate a budget.
    
    Args:
        budget_id: Budget unique identifier
        db: Database session
        
    Returns:
        Deactivated budget details
        
    Raises:
        HTTPException: If budget not found or deactivation fails
    """
    try:
        budget = budget_service.deactivate_budget(budget_id, db)
        if not budget:
            raise HTTPException(status_code=404, detail="Budget not found")
        return budget
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate budget: {str(e)}")


@router.get("/category/{category_id}/summary", response_model=List[BudgetResponse])
async def get_category_budgets(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all budgets for a specific category.
    
    Args:
        category_id: Category unique identifier
        db: Database session
        
    Returns:
        List of budgets for the category
    """
    try:
        budgets = budget_service.get_budgets_by_category(category_id, db)
        return budgets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve category budgets: {str(e)}")


@router.get("/overview/summary", response_model=dict)
async def get_budgets_overview(
    db: Session = Depends(get_db)
):
    """
    Get overview of all budgets with summary statistics.
    
    Args:
        db: Database session
        
    Returns:
        Budget overview with summary data
    """
    try:
        overview = budget_service.get_budgets_overview(db)
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve budgets overview: {str(e)}")


@router.post("/bulk-create", response_model=List[BudgetResponse], status_code=201)
async def bulk_create_budgets(
    budgets_data: List[BudgetCreate],
    db: Session = Depends(get_db)
):
    """
    Create multiple budgets in a single operation.
    
    Args:
        budgets_data: List of budget creation data
        db: Database session
        
    Returns:
        List of created budgets
        
    Raises:
        HTTPException: If bulk creation fails
    """
    try:
        # Validate all categories
        for budget_data in budgets_data:
            if not validate_budget_category(budget_data.category_id, db):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid category {budget_data.category_id} for budget creation"
                )
        
        budgets = budget_service.bulk_create_budgets(budgets_data, db)
        return budgets
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create budgets: {str(e)}")


@router.delete("/bulk-delete", status_code=204)
async def bulk_delete_budgets(
    budget_ids: List[UUID],
    db: Session = Depends(get_db)
):
    """
    Delete multiple budgets in a single operation.
    
    Args:
        budget_ids: List of budget IDs to delete
        db: Database session
        
    Raises:
        HTTPException: If bulk deletion fails
    """
    try:
        success = budget_service.bulk_delete_budgets(budget_ids, db)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete some budgets")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete budgets: {str(e)}")
