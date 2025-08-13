"""
Budget model for budget management and tracking.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, String, Date, Numeric, Boolean, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..database import Base
from ..core.open_finance_standards import BudgetPeriod


class Budget(Base):
    """Budget model for financial planning and tracking."""
    
    __tablename__ = "budgets"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Budget information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Budget allocation
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    
    # Period settings
    period_type = Column(String(20), nullable=False)  # WEEKLY, MONTHLY, QUARTERLY, YEARLY
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Alert settings
    alert_threshold = Column(Numeric(5, 2), default=80.00, nullable=False)  # Percentage
    alert_enabled = Column(Boolean, default=True, nullable=False)
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurring_pattern = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    category = relationship("Category")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_budgets_category', 'category_id'),
        Index('idx_budgets_period', 'period_type'),
        Index('idx_budgets_dates', 'start_date', 'end_date'),
        Index('idx_budgets_active', 'is_active'),
        Index('idx_budgets_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Budget(id={self.id}, name='{self.name}', amount={self.amount}, period={self.period_type})>"
    
    @property
    def is_weekly(self) -> bool:
        """Check if budget is weekly."""
        return self.period_type == BudgetPeriod.WEEKLY
    
    @property
    def is_monthly(self) -> bool:
        """Check if budget is monthly."""
        return self.period_type == BudgetPeriod.MONTHLY
    
    @property
    def is_quarterly(self) -> bool:
        """Check if budget is quarterly."""
        return self.period_type == BudgetPeriod.QUARTERLY
    
    @property
    def is_yearly(self) -> bool:
        """Check if budget is yearly."""
        return self.period_type == BudgetPeriod.YEARLY
    
    @property
    def is_current_period(self) -> bool:
        """Check if budget is for the current period."""
        today = date.today()
        return self.start_date <= today <= self.end_date
    
    @property
    def is_expired(self) -> bool:
        """Check if budget period has expired."""
        return date.today() > self.end_date
    
    @property
    def is_future(self) -> bool:
        """Check if budget period is in the future."""
        return date.today() < self.start_date
    
    @property
    def days_remaining(self) -> int:
        """Get days remaining in budget period."""
        today = date.today()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days
    
    @property
    def days_elapsed(self) -> int:
        """Get days elapsed in budget period."""
        today = date.today()
        if today < self.start_date:
            return 0
        return (today - self.start_date).days
    
    @property
    def period_progress(self) -> float:
        """Get budget period progress as percentage."""
        total_days = (self.end_date - self.start_date).days
        if total_days == 0:
            return 0.0
        return min(100.0, (self.days_elapsed / total_days) * 100)
    
    def get_period_dates(self) -> tuple[date, date]:
        """Get the start and end dates for the budget period."""
        return self.start_date, self.end_date
    
    def is_within_period(self, check_date: date) -> bool:
        """Check if a date is within the budget period."""
        return self.start_date <= check_date <= self.end_date
    
    def to_dict(self) -> dict:
        """Convert budget to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category_id": str(self.category_id) if self.category_id else None,
            "amount": float(self.amount) if self.amount else None,
            "period_type": self.period_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "alert_threshold": float(self.alert_threshold) if self.alert_threshold else None,
            "alert_enabled": self.alert_enabled,
            "is_active": self.is_active,
            "is_recurring": self.is_recurring,
            "recurring_pattern": self.recurring_pattern,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
