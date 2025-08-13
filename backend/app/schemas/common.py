"""
Common schemas used across the application.
"""
from datetime import date, datetime
from typing import Optional, Any, List
from pydantic import BaseModel, Field, validator


class DateRange(BaseModel):
    """Date range for filtering data."""
    start_date: date = Field(..., description="Start date for the range")
    end_date: date = Field(..., description="End date for the range")
    
    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat()
        }


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(20, ge=1, le=100, description="Page size (1-100)")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size
    
    @property
    def limit(self) -> int:
        """Get limit for database queries."""
        return self.size


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any] = Field(..., description="List of items for current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
    
    @validator('pages', pre=True, always=True)
    def calculate_pages(cls, v, values):
        """Calculate total pages based on total items and page size."""
        if 'total' in values and 'size' in values:
            return (values['total'] + values['size'] - 1) // values['size']
        return v


class SearchCriteria(BaseModel):
    """Search criteria for filtering data."""
    query: Optional[str] = Field(None, description="Search query string")
    date_range: Optional[DateRange] = Field(None, description="Date range filter")
    category_ids: Optional[List[str]] = Field(None, description="Category IDs to filter by")
    transaction_types: Optional[List[str]] = Field(None, description="Transaction types to filter by")
    min_amount: Optional[float] = Field(None, description="Minimum amount filter")
    max_amount: Optional[float] = Field(None, description="Maximum amount filter")
    accounts: Optional[List[str]] = Field(None, description="Account names to filter by")
    tags: Optional[List[str]] = Field(None, description="Tags to filter by")
    
    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        return any([
            self.query,
            self.date_range,
            self.category_ids,
            self.transaction_types,
            self.min_amount is not None,
            self.max_amount is not None,
            self.accounts,
            self.tags
        ])
    
    def to_dict(self) -> dict:
        """Convert to dictionary format for database queries."""
        filters = {}
        
        if self.query:
            filters["query"] = self.query
        if self.date_range:
            filters["date_range"] = self.date_range.to_dict()
        if self.category_ids:
            filters["category_ids"] = self.category_ids
        if self.transaction_types:
            filters["transaction_types"] = self.transaction_types
        if self.min_amount is not None:
            filters["min_amount"] = self.min_amount
        if self.max_amount is not None:
            filters["max_amount"] = self.max_amount
        if self.accounts:
            filters["accounts"] = self.accounts
        if self.tags:
            filters["tags"] = self.tags
            
        return filters


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: dict = Field(..., description="Error information")


class SuccessResponse(BaseModel):
    """Standard success response format."""
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HealthCheckResponse(BaseModel):
    """Health check response format."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Check timestamp")
    version: str = Field(..., description="Application version")
    database: str = Field(..., description="Database status")
    open_finance_compliance: str = Field(..., description="Open Finance Brasil compliance status")
