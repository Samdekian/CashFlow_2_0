"""
Transaction model for financial transactions.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import Column, String, Date, Numeric, Boolean, Text, JSON, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..database import Base
from ..core.open_finance_standards import TransactionType


class Transaction(Base):
    """Transaction model representing financial transactions."""
    
    __tablename__ = "transactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction details
    date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=False)
    transaction_type = Column(String(20), nullable=False)
    
    # Categorization
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    
    # Account information
    account = Column(String(100), nullable=True)
    account_type = Column(String(50), nullable=True)
    
    # Open Finance Brasil compliance
    currency = Column(String(3), default="BRL", nullable=False)
    country_code = Column(String(2), default="BR", nullable=False)
    reference_number = Column(String(100), nullable=True)
    institution_code = Column(String(50), nullable=True)
    
    # Additional metadata
    is_recurring = Column(Boolean, default=False)
    recurring_pattern = Column(String(50), nullable=True)
    tags = Column(JSON, nullable=True)  # List of tags
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="transactions")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_transactions_date', 'date'),
        Index('idx_transactions_amount', 'amount'),
        Index('idx_transactions_type', 'transaction_type'),
        Index('idx_transactions_category', 'category_id'),
        Index('idx_transactions_account', 'account'),
        Index('idx_transactions_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, date={self.date}, amount={self.amount}, description='{self.description}')>"
    
    @property
    def formatted_amount(self) -> str:
        """Format amount according to Brazilian currency standards."""
        if self.currency == "BRL":
            return f"R$ {self.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{self.currency} {self.amount:,.2f}"
    
    @property
    def is_income(self) -> bool:
        """Check if transaction is income."""
        return self.transaction_type == TransactionType.INCOME
    
    @property
    def is_expense(self) -> bool:
        """Check if transaction is expense."""
        return self.transaction_type == TransactionType.EXPENSE
    
    @property
    def is_transfer(self) -> bool:
        """Check if transaction is transfer."""
        return self.transaction_type == TransactionType.TRANSFER
    
    @property
    def is_investment(self) -> bool:
        """Check if transaction is investment."""
        return self.transaction_type == TransactionType.INVESTMENT
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary."""
        return {
            "id": str(self.id),
            "date": self.date.isoformat() if self.date else None,
            "amount": float(self.amount) if self.amount else None,
            "description": self.description,
            "transaction_type": self.transaction_type,
            "category_id": str(self.category_id) if self.category_id else None,
            "account": self.account,
            "account_type": self.account_type,
            "currency": self.currency,
            "country_code": self.country_code,
            "reference_number": self.reference_number,
            "institution_code": self.institution_code,
            "is_recurring": self.is_recurring,
            "recurring_pattern": self.recurring_pattern,
            "tags": self.tags,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
