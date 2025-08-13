"""
Category schemas for API requests and responses.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from uuid import UUID


class CategoryBase(BaseModel):
    """Base category schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    name_en: Optional[str] = Field(None, max_length=100, description="English category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    level: int = Field(..., ge=1, le=3, description="Category level (1=Primary, 2=Secondary, 3=Detailed)")
    parent_id: Optional[UUID] = Field(None, description="Parent category ID for hierarchy")
    open_finance_code: Optional[str] = Field(None, max_length=100, description="Open Finance Brasil code")
    open_finance_category: Optional[str] = Field(None, max_length=100, description="Open Finance Brasil category")
    color: Optional[str] = Field(None, max_length=7, description="Hex color code")
    icon: Optional[str] = Field(None, max_length=50, description="Icon identifier")
    sort_order: int = Field(0, ge=0, description="Sort order for display")
    
    @validator('level')
    def validate_level(cls, v):
        """Validate category level."""
        if v < 1 or v > 3:
            raise ValueError('Category level must be between 1 and 3')
        return v
    
    @validator('color')
    def validate_color(cls, v):
        """Validate hex color code."""
        if v is not None and not v.startswith('#') and len(v) != 7:
            raise ValueError('Color must be a valid hex color code (e.g., #FF0000)')
        return v


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Category name")
    name_en: Optional[str] = Field(None, max_length=100, description="English category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    level: Optional[int] = Field(None, ge=1, le=3, description="Category level")
    parent_id: Optional[UUID] = Field(None, description="Parent category ID")
    open_finance_code: Optional[str] = Field(None, max_length=100, description="Open Finance Brasil code")
    open_finance_category: Optional[str] = Field(None, max_length=100, description="Open Finance Brasil category")
    color: Optional[str] = Field(None, max_length=7, description="Hex color code")
    icon: Optional[str] = Field(None, max_length=50, description="Icon identifier")
    sort_order: Optional[int] = Field(None, ge=0, description="Sort order")
    
    @validator('level')
    def validate_level(cls, v):
        """Validate category level if provided."""
        if v is not None and (v < 1 or v > 3):
            raise ValueError('Category level must be between 1 and 3')
        return v


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: UUID = Field(..., description="Category unique identifier")
    is_active: bool = Field(..., description="Whether the category is active")
    is_system: bool = Field(..., description="Whether this is a system-defined category")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Alimentação",
                "name_en": "Food & Dining",
                "description": "Food, restaurants, and dining expenses",
                "level": 2,
                "parent_id": "456e7890-e89b-12d3-a456-426614174000",
                "open_finance_code": "OFB_DESPESAS_ALIMENTACAO",
                "open_finance_category": "DESPESAS",
                "color": "#EF4444",
                "icon": "🍽️",
                "sort_order": 0,
                "is_active": True,
                "is_system": True,
                "created_at": "2024-12-01T00:00:00Z",
                "updated_at": "2024-12-01T00:00:00Z"
            }
        }


class CategoryTreeResponse(CategoryResponse):
    """Schema for category tree response with children."""
    children: Optional[List['CategoryTreeResponse']] = Field(None, description="Child categories")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Despesas",
                "name_en": "Expenses",
                "description": "All forms of expenses and costs",
                "level": 1,
                "parent_id": None,
                "open_finance_code": "OFB_DESPESAS",
                "open_finance_category": "DESPESAS",
                "color": "#EF4444",
                "icon": "💸",
                "sort_order": 0,
                "is_active": True,
                "is_system": True,
                "created_at": "2024-12-01T00:00:00Z",
                "updated_at": "2024-12-01T00:00:00Z",
                "children": [
                    {
                        "id": "789e0123-e89b-12d3-a456-426614174000",
                        "name": "Alimentação",
                        "name_en": "Food & Dining",
                        "description": "Food, restaurants, and dining expenses",
                        "level": 2,
                        "parent_id": "123e4567-e89b-12d3-a456-426614174000",
                        "open_finance_code": "OFB_DESPESAS_ALIMENTACAO",
                        "open_finance_category": "DESPESAS",
                        "color": "#EF4444",
                        "icon": "🍽️",
                        "sort_order": 0,
                        "is_active": True,
                        "is_system": True,
                        "created_at": "2024-12-01T00:00:00Z",
                        "updated_at": "2024-12-01T00:00:00Z",
                        "children": []
                    }
                ]
            }
        }


class CategoryListResponse(BaseModel):
    """Schema for category list response."""
    categories: List[CategoryResponse] = Field(..., description="List of categories")
    total: int = Field(..., description="Total number of categories")
    
    class Config:
        schema_extra = {
            "example": {
                "categories": [],
                "total": 25
            }
        }


class CategoryFilters(BaseModel):
    """Schema for category filtering."""
    level: Optional[int] = Field(None, ge=1, le=3, description="Filter by category level")
    parent_id: Optional[UUID] = Field(None, description="Filter by parent category")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    is_system: Optional[bool] = Field(None, description="Filter by system category status")
    search_query: Optional[str] = Field(None, description="Search in name and description")
    
    @validator('level')
    def validate_level(cls, v):
        """Validate level filter if provided."""
        if v is not None and (v < 1 or v > 3):
            raise ValueError('Level must be between 1 and 3')
        return v


class CategoryBulkOperation(BaseModel):
    """Schema for bulk category operations."""
    operation: str = Field(..., description="Operation type (update, delete, activate, deactivate)")
    category_ids: List[UUID] = Field(..., description="List of category IDs to operate on")
    update_data: Optional[CategoryUpdate] = Field(None, description="Update data for bulk update")
    
    @validator('operation')
    def validate_operation(cls, v):
        """Validate operation type."""
        valid_operations = ['update', 'delete', 'activate', 'deactivate']
        if v not in valid_operations:
            raise ValueError(f'Operation must be one of: {", ".join(valid_operations)}')
        return v
    
    @validator('category_ids')
    def validate_category_ids(cls, v):
        """Validate category IDs list."""
        if not v:
            raise ValueError('Category IDs list cannot be empty')
        if len(v) > 50:
            raise ValueError('Cannot operate on more than 50 categories at once')
        return v


class CategoryStatistics(BaseModel):
    """Schema for category statistics."""
    category_id: UUID = Field(..., description="Category ID")
    category_name: str = Field(..., description="Category name")
    transaction_count: int = Field(..., description="Number of transactions in this category")
    total_amount: str = Field(..., description="Total amount in this category")
    percentage_of_total: float = Field(..., description="Percentage of total transactions")
    average_amount: str = Field(..., description="Average transaction amount in this category")
    
    class Config:
        schema_extra = {
            "example": {
                "category_id": "123e4567-e89b-12d3-a456-426614174000",
                "category_name": "Alimentação",
                "transaction_count": 45,
                "total_amount": "2250.00",
                "percentage_of_total": 30.0,
                "average_amount": "50.00"
            }
        }


# Update forward references
CategoryTreeResponse.model_rebuild()
