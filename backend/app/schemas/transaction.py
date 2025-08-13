"""
Transaction schemas for API requests and responses.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID


class TransactionBase(BaseModel):
    """Base transaction schema with common fields."""
    date: date
    amount: Decimal
    description: str
    transaction_type: str
    category_id: Optional[UUID] = None
    account: Optional[str] = None
    currency: str = "BRL"
    country_code: str = "BR"
    is_recurring: bool = False
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""
    pass


class TransactionUpdate(BaseModel):
    """Schema for updating an existing transaction."""
    date: Optional[date] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    transaction_type: Optional[str] = None
    category_id: Optional[UUID] = None
    account: Optional[str] = None
    currency: Optional[str] = None
    country_code: Optional[str] = None
    is_recurring: Optional[bool] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class TransactionListResponse(BaseModel):
    """Schema for transaction list response."""
    transactions: List[TransactionResponse]
    total: int
    page: int
    size: int
    pages: int


class TransactionFilters(BaseModel):
    """Schema for transaction filtering."""
    date_range: Optional[date] = None
    category_ids: Optional[List[UUID]] = None
    transaction_types: Optional[List[str]] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    accounts: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_recurring: Optional[bool] = None
    search_query: Optional[str] = None


class TransactionSummary(BaseModel):
    """Schema for transaction summary statistics."""
    total_transactions: int
    total_income: Decimal
    total_expenses: Decimal
    net_amount: Decimal


class BulkTransactionOperation(BaseModel):
    """Schema for bulk transaction operations."""
    operation: str
    transaction_ids: List[UUID]
    update_data: Optional[TransactionUpdate] = None
    category_id: Optional[UUID] = None


class TransactionImport(BaseModel):
    """Schema for transaction import data."""
    date: date
    amount: Decimal
    description: str
    category: Optional[str] = None
    account: Optional[str] = None
    transaction_type: Optional[str] = None
    notes: Optional[str] = None
