"""
Category model for transaction categorization.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..database import Base


class Category(Base):
    """Category model for transaction categorization with Open Finance Brasil compliance."""
    
    __tablename__ = "categories"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Category information
    name = Column(String(100), nullable=False)
    name_en = Column(String(100), nullable=True)  # English name for internationalization
    description = Column(Text, nullable=True)
    
    # Hierarchy structure
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    level = Column(Integer, nullable=False, default=1)  # 1=Primary, 2=Secondary, 3=Detailed
    
    # Open Finance Brasil compliance
    open_finance_code = Column(String(100), nullable=True, unique=True)
    open_finance_category = Column(String(100), nullable=True)
    
    # Visual properties
    color = Column(String(7), nullable=True)  # Hex color code
    icon = Column(String(50), nullable=True)  # Emoji or icon identifier
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    is_system = Column(Boolean, default=False, nullable=False)  # System-defined categories
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent")
    transactions = relationship("Transaction", back_populates="category")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_categories_parent', 'parent_id'),
        Index('idx_categories_level', 'level'),
        Index('idx_categories_active', 'is_active'),
        Index('idx_categories_order', 'sort_order'),
        Index('idx_categories_open_finance', 'open_finance_code'),
    )
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', level={self.level})>"
    
    @property
    def is_primary(self) -> bool:
        """Check if category is primary level."""
        return self.level == 1
    
    @property
    def is_secondary(self) -> bool:
        """Check if category is secondary level."""
        return self.level == 2
    
    @property
    def is_detailed(self) -> bool:
        """Check if category is detailed level."""
        return self.level == 3
    
    @property
    def has_children(self) -> bool:
        """Check if category has child categories."""
        return len(self.children) > 0
    
    @property
    def is_leaf(self) -> bool:
        """Check if category is a leaf node (no children)."""
        return len(self.children) == 0
    
    def get_full_path(self) -> str:
        """Get the full category path from root to current category."""
        path_parts = [self.name]
        current = self.parent
        
        while current:
            path_parts.insert(0, current.name)
            current = current.parent
        
        return " > ".join(path_parts)
    
    def get_ancestors(self) -> List["Category"]:
        """Get all ancestor categories from root to parent."""
        ancestors = []
        current = self.parent
        
        while current:
            ancestors.append(current)
            current = current.parent
        
        return list(reversed(ancestors))
    
    def get_descendants(self) -> List["Category"]:
        """Get all descendant categories (children and their children)."""
        descendants = []
        
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        
        return descendants
    
    def to_dict(self) -> dict:
        """Convert category to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "name_en": self.name_en,
            "description": self.description,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "level": self.level,
            "open_finance_code": self.open_finance_code,
            "open_finance_category": self.open_finance_category,
            "color": self.color,
            "icon": self.icon,
            "is_active": self.is_active,
            "is_system": self.is_system,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_tree_dict(self) -> dict:
        """Convert category to tree dictionary with children."""
        result = self.to_dict()
        if self.children:
            result["children"] = [child.to_tree_dict() for child in sorted(self.children, key=lambda x: x.sort_order)]
        return result
