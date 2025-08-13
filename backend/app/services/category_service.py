"""
Category service for managing transaction categories.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.exc import IntegrityError

from ..models.category import Category
from ..models.transaction import Transaction
from ..schemas.category import CategoryCreate, CategoryUpdate, CategoryFilters
from ..schemas.common import PaginatedResponse


class CategoryService:
    """Service for managing transaction categories."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category."""
        try:
            # Validate parent category if specified
            if category_data.parent_id:
                parent = self.get_category(category_data.parent_id)
                if not parent:
                    raise ValueError("Parent category not found")
                
                # Validate level hierarchy
                if category_data.level <= parent.level:
                    raise ValueError("Category level must be greater than parent level")
            
            # Create category instance
            db_category = Category(
                name=category_data.name,
                name_en=category_data.name_en,
                description=category_data.description,
                level=category_data.level,
                parent_id=category_data.parent_id,
                open_finance_code=category_data.open_finance_code,
                open_finance_category=category_data.open_finance_category,
                color=category_data.color,
                icon=category_data.icon,
                sort_order=category_data.sort_order,
                is_active=True,
                is_system=False
            )
            
            self.db.add(db_category)
            self.db.commit()
            self.db.refresh(db_category)
            
            return db_category
            
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create category: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Unexpected error creating category: {str(e)}")
    
    def get_category(self, category_id: UUID) -> Optional[Category]:
        """Get a category by ID."""
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    def get_categories(
        self,
        filters: Optional[CategoryFilters] = None,
        pagination: Optional[dict] = None
    ) -> PaginatedResponse:
        """Get categories with filtering and pagination."""
        query = self.db.query(Category)
        
        # Apply filters
        if filters:
            query = self._apply_category_filters(query, filters)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        if pagination:
            query = query.offset(pagination.get("offset", 0)).limit(pagination.get("limit", 20))
        
        # Order by level, sort_order, and name
        query = query.order_by(asc(Category.level), asc(Category.sort_order), asc(Category.name))
        
        # Execute query
        categories = query.all()
        
        # Create paginated response
        if pagination:
            return PaginatedResponse(
                items=categories,
                total=total,
                page=pagination.get("page", 1),
                size=pagination.get("size", 20)
            )
        else:
            return PaginatedResponse(
                items=categories,
                total=total,
                page=1,
                size=total
            )
    
    def update_category(self, category_id: UUID, update_data: CategoryUpdate) -> Optional[Category]:
        """Update an existing category."""
        db_category = self.get_category(category_id)
        if not db_category:
            return None
        
        try:
            # Don't allow updating system categories
            if db_category.is_system:
                raise ValueError("Cannot update system-defined categories")
            
            # Validate parent category if specified
            if update_data.parent_id:
                parent = self.get_category(update_data.parent_id)
                if not parent:
                    raise ValueError("Parent category not found")
                
                # Validate level hierarchy
                new_level = update_data.level or db_category.level
                if new_level <= parent.level:
                    raise ValueError("Category level must be greater than parent level")
            
            # Update fields
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(db_category, field, value)
            
            self.db.commit()
            self.db.refresh(db_category)
            
            return db_category
            
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to update category: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Unexpected error updating category: {str(e)}")
    
    def delete_category(self, category_id: UUID) -> bool:
        """Delete a category."""
        db_category = self.get_category(category_id)
        if not db_category:
            return False
        
        try:
            # Don't allow deletion of system categories
            if db_category.is_system:
                raise ValueError("Cannot delete system-defined categories")
            
            # Check if category has children
            if db_category.has_children:
                raise ValueError("Cannot delete category with child categories")
            
            # Check if category has transactions
            transaction_count = self.db.query(Transaction).filter(
                Transaction.category_id == category_id
            ).count()
            
            if transaction_count > 0:
                raise ValueError(f"Cannot delete category with {transaction_count} transactions")
            
            self.db.delete(db_category)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to delete category: {str(e)}")
    
    def get_category_tree(self) -> List[Category]:
        """Get the complete category hierarchy tree."""
        # Get all primary categories
        primary_categories = self.db.query(Category).filter(
            and_(Category.level == 1, Category.is_active == True)
        ).order_by(Category.sort_order, Category.name).all()
        
        return primary_categories
    
    def get_category_children(self, category_id: UUID) -> List[Category]:
        """Get child categories for a specific category."""
        return self.db.query(Category).filter(
            and_(Category.parent_id == category_id, Category.is_active == True)
        ).order_by(Category.sort_order, Category.name).all()
    
    def get_category_ancestors(self, category_id: UUID) -> List[Category]:
        """Get ancestor categories for a specific category."""
        category = self.get_category(category_id)
        if not category:
            return []
        
        return category.get_ancestors()
    
    def get_category_descendants(self, category_id: UUID) -> List[Category]:
        """Get descendant categories for a specific category."""
        category = self.get_category(category_id)
        if not category:
            return []
        
        return category.get_descendants()
    
    def get_categories_by_level(self, level: int) -> List[Category]:
        """Get all categories at a specific level."""
        if level < 1 or level > 3:
            raise ValueError("Level must be between 1 and 3")
        
        return self.db.query(Category).filter(
            and_(Category.level == level, Category.is_active == True)
        ).order_by(Category.sort_order, Category.name).all()
    
    def get_primary_categories(self) -> List[Category]:
        """Get all primary (level 1) categories."""
        return self.get_categories_by_level(1)
    
    def get_secondary_categories(self) -> List[Category]:
        """Get all secondary (level 2) categories."""
        return self.get_categories_by_level(2)
    
    def get_detailed_categories(self) -> List[Category]:
        """Get all detailed (level 3) categories."""
        return self.get_categories_by_level(3)
    
    def activate_category(self, category_id: UUID) -> Optional[Category]:
        """Activate a category."""
        db_category = self.get_category(category_id)
        if not db_category:
            return None
        
        db_category.is_active = True
        self.db.commit()
        self.db.refresh(db_category)
        
        return db_category
    
    def deactivate_category(self, category_id: UUID) -> Optional[Category]:
        """Deactivate a category."""
        db_category = self.get_category(category_id)
        if not db_category:
            return None
        
        # Don't allow deactivating system categories
        if db_category.is_system:
            raise ValueError("Cannot deactivate system-defined categories")
        
        db_category.is_active = False
        self.db.commit()
        self.db.refresh(db_category)
        
        return db_category
    
    def get_category_statistics(self, category_id: UUID) -> Dict[str, Any]:
        """Get statistics for a specific category."""
        category = self.get_category(category_id)
        if not category:
            raise ValueError("Category not found")
        
        # Get transaction count and amounts
        transactions = self.db.query(Transaction).filter(
            Transaction.category_id == category_id
        ).all()
        
        if not transactions:
            return {
                "category_id": category_id,
                "category_name": category.name,
                "transaction_count": 0,
                "total_amount": "0.00",
                "percentage_of_total": 0.0,
                "average_amount": "0.00"
            }
        
        # Calculate statistics
        transaction_count = len(transactions)
        total_amount = sum(abs(t.amount) for t in transactions)
        
        # Get total transactions for percentage calculation
        total_transactions = self.db.query(Transaction).count()
        percentage_of_total = (transaction_count / total_transactions * 100) if total_transactions > 0 else 0
        
        average_amount = total_amount / transaction_count if transaction_count > 0 else 0
        
        return {
            "category_id": category_id,
            "category_name": category.name,
            "transaction_count": transaction_count,
            "total_amount": f"{total_amount:.2f}",
            "percentage_of_total": round(percentage_of_total, 2),
            "average_amount": f"{average_amount:.2f}"
        }
    
    def get_category_counts_by_level(self) -> Dict[str, int]:
        """Get category counts by level."""
        counts = {}
        
        for level in range(1, 4):
            count = self.db.query(Category).filter(
                and_(Category.level == level, Category.is_active == True)
            ).count()
            counts[f"level_{level}"] = count
        
        return counts
    
    def bulk_operation(self, operation_data: dict) -> Dict[str, Any]:
        """Perform bulk operations on categories."""
        results = {
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }
        
        for category_id in operation_data["category_ids"]:
            try:
                if operation_data["operation"] == "delete":
                    if self.delete_category(category_id):
                        results["success_count"] += 1
                    else:
                        results["error_count"] += 1
                        results["errors"].append(f"Category {category_id} not found")
                
                elif operation_data["operation"] == "update" and operation_data.get("update_data"):
                    update_data = CategoryUpdate(**operation_data["update_data"])
                    if self.update_category(category_id, update_data):
                        results["success_count"] += 1
                    else:
                        results["error_count"] += 1
                        results["errors"].append(f"Category {category_id} not found")
                
                elif operation_data["operation"] == "activate":
                    if self.activate_category(category_id):
                        results["success_count"] += 1
                    else:
                        results["error_count"] += 1
                        results["errors"].append(f"Category {category_id} not found")
                
                elif operation_data["operation"] == "deactivate":
                    if self.deactivate_category(category_id):
                        results["success_count"] += 1
                    else:
                        results["error_count"] += 1
                        results["errors"].append(f"Category {category_id} not found")
                
            except Exception as e:
                results["error_count"] += 1
                results["errors"].append(f"Error processing category {category_id}: {str(e)}")
        
        return results
    
    def _apply_category_filters(self, query, filters: CategoryFilters):
        """Apply category filters to query."""
        if filters.level is not None:
            query = query.filter(Category.level == filters.level)
        
        if filters.parent_id is not None:
            query = query.filter(Category.parent_id == filters.parent_id)
        
        if filters.is_active is not None:
            query = query.filter(Category.is_active == filters.is_active)
        
        if filters.is_system is not None:
            query = query.filter(Category.is_system == filters.is_system)
        
        if filters.search_query:
            query = query.filter(
                or_(
                    Category.name.ilike(f"%{filters.search_query}%"),
                    Category.description.ilike(f"%{filters.search_query}%")
                )
            )
        
        return query
    
    def search_categories(self, search_query: str, limit: int = 50) -> List[Category]:
        """Search categories by name and description."""
        query = self.db.query(Category).filter(
            and_(
                Category.is_active == True,
                or_(
                    Category.name.ilike(f"%{search_query}%"),
                    Category.description.ilike(f"%{search_query}%")
                )
            )
        )
        
        return query.order_by(Category.level, Category.sort_order, Category.name).limit(limit).all()
    
    def get_category_path(self, category_id: UUID) -> str:
        """Get the full path of a category from root."""
        category = self.get_category(category_id)
        if not category:
            return ""
        
        return category.get_full_path()
    
    def validate_category_hierarchy(self, category_id: UUID) -> bool:
        """Validate that a category's hierarchy is valid."""
        category = self.get_category(category_id)
        if not category:
            return False
        
        # Check parent chain
        current = category
        while current.parent_id:
            parent = self.get_category(current.parent_id)
            if not parent:
                return False
            
            # Check level hierarchy
            if current.level <= parent.level:
                return False
            
            current = parent
        
        return True
