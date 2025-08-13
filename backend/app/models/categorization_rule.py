"""
CategorizationRule model for automatic transaction categorization.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey, Index, Numeric, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..database import Base


class CategorizationRule(Base):
    """Rule for automatic transaction categorization."""
    
    __tablename__ = "categorization_rules"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Rule information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Target category
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    
    # Rule conditions
    rule_type = Column(String(20), nullable=False)  # KEYWORD, AMOUNT_RANGE, MERCHANT, PATTERN
    rule_value = Column(Text, nullable=False)
    
    # Rule parameters
    amount_min = Column(Numeric(12, 2), nullable=True)
    amount_max = Column(Numeric(12, 2), nullable=True)
    confidence_score = Column(Numeric(3, 2), default=0.80, nullable=False)  # 0.00 to 1.00
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=0, nullable=False)  # Higher priority = applied first
    is_system = Column(Boolean, default=False, nullable=False)  # System-defined rules
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    category = relationship("Category")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_categorization_rules_category', 'category_id'),
        Index('idx_categorization_rules_type', 'rule_type'),
        Index('idx_categorization_rules_active', 'is_active'),
        Index('idx_categorization_rules_priority', 'priority'),
        Index('idx_categorization_rules_created', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<CategorizationRule(id={self.id}, name='{self.name}', type={self.rule_type})>"
    
    @property
    def is_keyword_rule(self) -> bool:
        """Check if rule is keyword-based."""
        return self.rule_type == "KEYWORD"
    
    @property
    def is_amount_rule(self) -> bool:
        """Check if rule is amount-based."""
        return self.rule_type == "AMOUNT_RANGE"
    
    @property
    def is_merchant_rule(self) -> bool:
        """Check if rule is merchant-based."""
        return self.rule_type == "MERCHANT"
    
    @property
    def is_pattern_rule(self) -> bool:
        """Check if rule is pattern-based."""
        return self.rule_type == "PATTERN"
    
    def matches_transaction(self, description: str, amount: float, merchant: Optional[str] = None) -> bool:
        """Check if this rule matches a transaction."""
        if not self.is_active:
            return False
        
        if self.is_keyword_rule:
            return self._matches_keyword(description)
        elif self.is_amount_rule:
            return self._matches_amount(amount)
        elif self.is_merchant_rule:
            return self._matches_merchant(merchant or description)
        elif self.is_pattern_rule:
            return self._matches_pattern(description)
        
        return False
    
    def _matches_keyword(self, description: str) -> bool:
        """Check if description matches keyword rule."""
        if not description:
            return False
        
        keywords = [kw.strip().lower() for kw in self.rule_value.split(',')]
        description_lower = description.lower()
        
        return any(keyword in description_lower for keyword in keywords)
    
    def _matches_amount(self, amount: float) -> bool:
        """Check if amount matches amount range rule."""
        if amount is None:
            return False
        
        if self.amount_min is not None and amount < float(self.amount_min):
            return False
        
        if self.amount_max is not None and amount > float(self.amount_max):
            return False
        
        return True
    
    def _matches_merchant(self, merchant: str) -> bool:
        """Check if merchant matches merchant rule."""
        if not merchant:
            return False
        
        merchants = [m.strip().lower() for m in self.rule_value.split(',')]
        merchant_lower = merchant.lower()
        
        return any(m in merchant_lower for m in merchants)
    
    def _matches_pattern(self, description: str) -> bool:
        """Check if description matches pattern rule."""
        if not description:
            return False
        
        # Simple pattern matching - can be enhanced with regex
        patterns = [p.strip().lower() for p in self.rule_value.split(',')]
        description_lower = description.lower()
        
        return any(pattern in description_lower for pattern in patterns)
    
    def get_match_score(self, description: str, amount: float, merchant: Optional[str] = None) -> float:
        """Get confidence score for a transaction match."""
        if not self.matches_transaction(description, amount, merchant):
            return 0.0
        
        # Base confidence score
        score = float(self.confidence_score)
        
        # Adjust score based on rule type and match quality
        if self.is_keyword_rule:
            # Higher score for exact keyword matches
            keywords = [kw.strip().lower() for kw in self.rule_value.split(',')]
            description_lower = description.lower()
            
            exact_matches = sum(1 for kw in keywords if kw == description_lower)
            if exact_matches > 0:
                score = min(1.0, score + 0.1)
        
        elif self.is_amount_rule:
            # Higher score for amounts in the middle of the range
            if self.amount_min is not None and self.amount_max is not None:
                range_mid = (float(self.amount_min) + float(self.amount_max)) / 2
                distance_from_mid = abs(amount - range_mid)
                range_size = float(self.amount_max) - float(self.amount_min)
                
                if range_size > 0:
                    # Closer to middle = higher score
                    score = min(1.0, score + (1 - distance_from_mid / range_size) * 0.1)
        
        elif self.is_merchant_rule:
            # Higher score for exact merchant matches
            merchants = [m.strip().lower() for m in self.rule_value.split(',')]
            merchant_lower = (merchant or "").lower()
            
            if merchant_lower in merchants:
                score = min(1.0, score + 0.1)
        
        return min(1.0, score)
    
    def to_dict(self) -> dict:
        """Convert categorization rule to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category_id": str(self.category_id) if self.category_id else None,
            "rule_type": self.rule_type,
            "rule_value": self.rule_value,
            "amount_min": float(self.amount_min) if self.amount_min else None,
            "amount_max": float(self.amount_max) if self.amount_max else None,
            "confidence_score": float(self.confidence_score) if self.confidence_score else None,
            "is_active": self.is_active,
            "priority": self.priority,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
