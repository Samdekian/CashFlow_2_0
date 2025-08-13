"""
Budget-related Pydantic schemas for the CashFlow Monitor API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from enum import Enum

from .common import PaginationParams


class BudgetPeriod(str, Enum):
    """Budget period types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class BudgetCreate(BaseModel):
    """Schema for creating a new budget."""
    name: str = Field(..., min_length=1, max_length=100, description="Budget name")
    category_id: UUID = Field(..., description="Category ID for the budget")
    amount: Decimal = Field(..., gt=0, description="Budget amount")
    period_type: BudgetPeriod = Field(..., description="Budget period type")
    start_date: date = Field(..., description="Budget start date")
    end_date: date = Field(..., description="Budget end date")
    alert_threshold: Decimal = Field(80.0, ge=0, le=100, description="Alert threshold percentage")
    is_active: bool = Field(True, description="Whether the budget is active")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate that end date is after start date."""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        """Validate budget amount."""
        if v <= 0:
            raise ValueError('Budget amount must be positive')
        return v


class BudgetUpdate(BaseModel):
    """Schema for updating an existing budget."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Budget name")
    category_id: Optional[UUID] = Field(None, description="Category ID for the budget")
    amount: Optional[Decimal] = Field(None, gt=0, description="Budget amount")
    period_type: Optional[BudgetPeriod] = Field(None, description="Budget period type")
    start_date: Optional[date] = Field(None, description="Budget start date")
    end_date: Optional[date] = Field(None, description="Budget end date")
    alert_threshold: Optional[Decimal] = Field(None, ge=0, le=100, description="Alert threshold percentage")
    is_active: Optional[bool] = Field(None, description="Whether the budget is active")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate that end date is after start date if both are provided."""
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v
    
    @validator('amount')
    def validate_amount(cls, v):
        """Validate budget amount."""
        if v is not None and v <= 0:
            raise ValueError('Budget amount must be positive')
        return v


class BudgetResponse(BaseModel):
    """Schema for budget response."""
    id: UUID = Field(..., description="Budget unique identifier")
    name: str = Field(..., description="Budget name")
    category_id: UUID = Field(..., description="Category ID for the budget")
    amount: Decimal = Field(..., description="Budget amount")
    period_type: BudgetPeriod = Field(..., description="Budget period type")
    start_date: date = Field(..., description="Budget start date")
    end_date: date = Field(..., description="Budget end date")
    alert_threshold: Decimal = Field(..., description="Alert threshold percentage")
    is_active: bool = Field(..., description="Whether the budget is active")
    created_at: datetime = Field(..., description="Budget creation timestamp")
    updated_at: datetime = Field(..., description="Budget last update timestamp")
    
    class Config:
        from_attributes = True


class BudgetListResponse(BaseModel):
    """Schema for paginated budget list response."""
    items: List[BudgetResponse] = Field(..., description="List of budgets")
    total: int = Field(..., description="Total number of budgets")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")


class BudgetProgressResponse(BaseModel):
    """Schema for budget progress response."""
    budget_id: UUID = Field(..., description="Budget unique identifier")
    budget_name: str = Field(..., description="Budget name")
    total_amount: Decimal = Field(..., description="Total budget amount")
    spent_amount: Decimal = Field(..., description="Amount spent so far")
    remaining_amount: Decimal = Field(..., description="Remaining budget amount")
    progress_percentage: float = Field(..., description="Progress percentage (0-100)")
    days_remaining: int = Field(..., description="Days remaining in budget period")
    is_over_budget: bool = Field(..., description="Whether budget has been exceeded")
    alert_level: str = Field(..., description="Alert level (none, warning, critical)")


class BudgetAlertResponse(BaseModel):
    """Schema for budget alert response."""
    type: str = Field(..., description="Alert type")
    message: str = Field(..., description="Alert message")
    severity: str = Field(..., description="Alert severity level")
    created_at: datetime = Field(..., description="Alert creation timestamp")


class BudgetFilters(BaseModel):
    """Schema for budget filtering criteria."""
    category_id: Optional[UUID] = Field(None, description="Filter by category ID")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    period_type: Optional[BudgetPeriod] = Field(None, description="Filter by period type")
    start_date: Optional[date] = Field(None, description="Filter by start date")
    end_date: Optional[date] = Field(None, description="Filter by end date")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum budget amount")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="Maximum budget amount")
    sort_by: Optional[str] = Field(None, description="Sort field (amount, start_date, name)")
    sort_desc: bool = Field(False, description="Sort in descending order")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate that end date is after start date if both are provided."""
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v
    
    @validator('max_amount')
    def validate_max_amount(cls, v, values):
        """Validate that max amount is greater than min amount if both are provided."""
        if v and 'min_amount' in values and values['min_amount']:
            if v <= values['min_amount']:
                raise ValueError('Max amount must be greater than min amount')
        return v


class BudgetSummaryResponse(BaseModel):
    """Schema for budget summary response."""
    total_budgets: int = Field(..., description="Total number of budgets")
    active_budgets: int = Field(..., description="Number of active budgets")
    total_budgeted_amount: Decimal = Field(..., description="Total budgeted amount")
    total_spent_amount: Decimal = Field(..., description="Total amount spent")
    overall_progress_percentage: float = Field(..., description="Overall progress percentage")
    over_budget_count: int = Field(..., description="Number of budgets over limit")
    alert_summary: dict = Field(..., description="Summary of alerts by level")


class BudgetCategoryResponse(BaseModel):
    """Schema for budget by category response."""
    category_id: UUID = Field(..., description="Category ID")
    category_name: str = Field(..., description="Category name")
    budget_amount: Decimal = Field(..., description="Budget amount for category")
    spent_amount: Decimal = Field(..., description="Amount spent in category")
    remaining_amount: Decimal = Field(..., description="Remaining budget for category")
    progress_percentage: float = Field(..., description="Progress percentage")
    is_over_budget: bool = Field(..., description="Whether category budget is exceeded")


class BudgetPeriodResponse(BaseModel):
    """Schema for budget period information."""
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    period_days: int = Field(..., description="Number of days in period")
    days_elapsed: int = Field(..., description="Days elapsed in period")
    days_remaining: int = Field(..., description="Days remaining in period")
    is_period_active: bool = Field(..., description="Whether period is currently active")


class BudgetRecommendationResponse(BaseModel):
    """Schema for budget recommendations."""
    recommendation_type: str = Field(..., description="Type of recommendation")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Recommendation description")
    priority: str = Field(..., description="Recommendation priority (low, medium, high)")
    action_items: List[str] = Field(..., description="List of action items")
    estimated_impact: str = Field(..., description="Estimated impact of following recommendation")


class BudgetHistoryResponse(BaseModel):
    """Schema for budget history response."""
    budget_id: UUID = Field(..., description="Budget unique identifier")
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    budgeted_amount: Decimal = Field(..., description="Budgeted amount for period")
    actual_spent: Decimal = Field(..., description="Actual amount spent")
    variance: Decimal = Field(..., description="Difference between budgeted and actual")
    variance_percentage: float = Field(..., description="Variance as percentage")
    status: str = Field(..., description="Period status (under, over, on_target)")


class BudgetTemplateResponse(BaseModel):
    """Schema for budget template response."""
    template_id: UUID = Field(..., description="Template unique identifier")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category_allocations: List[dict] = Field(..., description="Category budget allocations")
    period_type: BudgetPeriod = Field(..., description="Default period type")
    is_default: bool = Field(..., description="Whether this is the default template")


class BudgetExportRequest(BaseModel):
    """Schema for budget export request."""
    budget_ids: List[UUID] = Field(..., description="List of budget IDs to export")
    format: str = Field("csv", description="Export format (csv, json, pdf)")
    include_progress: bool = Field(True, description="Include progress information")
    include_alerts: bool = Field(True, description="Include alert information")
    date_range: Optional[dict] = Field(None, description="Date range for export")


class BudgetImportRequest(BaseModel):
    """Schema for budget import request."""
    file_content: str = Field(..., description="File content for import")
    file_format: str = Field(..., description="File format (csv, json)")
    overwrite_existing: bool = Field(False, description="Whether to overwrite existing budgets")
    validate_only: bool = Field(False, description="Whether to only validate without importing")
