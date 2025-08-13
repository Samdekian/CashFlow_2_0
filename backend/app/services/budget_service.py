"""
Budget management service for the CashFlow Monitor.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from ..models.budget import Budget
from ..models.transaction import Transaction
from ..models.category import Category
from ..schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetListResponse,
    BudgetProgressResponse,
    BudgetAlertResponse,
    BudgetFilters,
    PaginationParams
)
from ..core.open_finance_standards import validate_budget_category


class BudgetService:
    """Service for budget management operations."""
    
    def create_budget(self, budget_data: BudgetCreate, db: Session) -> BudgetResponse:
        """
        Create a new budget.
        
        Args:
            budget_data: Budget creation data
            db: Database session
            
        Returns:
            Created budget response
            
        Raises:
            ValueError: If budget data is invalid
        """
        # Validate budget data
        if budget_data.amount <= 0:
            raise ValueError("Budget amount must be positive")
        
        if budget_data.start_date >= budget_data.end_date:
            raise ValueError("Start date must be before end date")
        
        # Check if category exists and is valid for budgets
        category = db.query(Category).filter(Category.id == budget_data.category_id).first()
        if not category:
            raise ValueError("Category not found")
        
        # Only allow budgets for expense categories
        if category.level == 1 and category.name != "DESPESAS":
            raise ValueError("Budgets can only be created for expense categories")
        
        # Create budget
        budget = Budget(
            name=budget_data.name,
            category_id=budget_data.category_id,
            amount=budget_data.amount,
            period_type=budget_data.period_type,
            start_date=budget_data.start_date,
            end_date=budget_data.end_date,
            alert_threshold=budget_data.alert_threshold,
            is_active=budget_data.is_active
        )
        
        db.add(budget)
        db.commit()
        db.refresh(budget)
        
        return self._to_budget_response(budget)
    
    def get_budgets(self, filters: BudgetFilters, pagination: PaginationParams, db: Session) -> BudgetListResponse:
        """
        Get budgets with filtering and pagination.
        
        Args:
            filters: Budget filtering criteria
            pagination: Pagination parameters
            db: Database session
            
        Returns:
            Paginated list of budgets
        """
        query = db.query(Budget).join(Category)
        
        # Apply filters
        if filters.category_id:
            query = query.filter(Budget.category_id == filters.category_id)
        
        if filters.is_active is not None:
            query = query.filter(Budget.is_active == filters.is_active)
        
        if filters.period_type:
            query = query.filter(Budget.period_type == filters.period_type)
        
        if filters.start_date:
            query = query.filter(Budget.start_date >= filters.start_date)
        
        if filters.end_date:
            query = query.filter(Budget.end_date <= filters.end_date)
        
        if filters.min_amount:
            query = query.filter(Budget.amount >= filters.min_amount)
        
        if filters.max_amount:
            query = query.filter(Budget.amount <= filters.max_amount)
        
        # Apply sorting
        if filters.sort_by:
            if filters.sort_by == "amount":
                query = query.order_by(desc(Budget.amount) if filters.sort_desc else Budget.amount)
            elif filters.sort_by == "start_date":
                query = query.order_by(desc(Budget.start_date) if filters.sort_desc else Budget.start_date)
            elif filters.sort_by == "name":
                query = query.order_by(desc(Budget.name) if filters.sort_desc else Budget.name)
        else:
            query = query.order_by(desc(Budget.created_at))
        
        # Apply pagination
        total = query.count()
        budgets = query.offset(pagination.offset).limit(pagination.limit).all()
        
        # Convert to response format
        budget_responses = [self._to_budget_response(budget) for budget in budgets]
        
        return BudgetListResponse(
            items=budget_responses,
            total=total,
            page=pagination.page,
            size=pagination.limit,
            pages=(total + pagination.limit - 1) // pagination.limit
        )
    
    def get_budget(self, budget_id: UUID, db: Session) -> Optional[BudgetResponse]:
        """
        Get a specific budget by ID.
        
        Args:
            budget_id: Budget unique identifier
            db: Database session
            
        Returns:
            Budget response or None if not found
        """
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            return None
        
        return self._to_budget_response(budget)
    
    def update_budget(self, budget_id: UUID, budget_data: BudgetUpdate, db: Session) -> Optional[BudgetResponse]:
        """
        Update an existing budget.
        
        Args:
            budget_id: Budget unique identifier
            budget_data: Budget update data
            db: Database session
            
        Returns:
            Updated budget response or None if not found
            
        Raises:
            ValueError: If update data is invalid
        """
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            return None
        
        # Validate update data
        if budget_data.amount is not None and budget_data.amount <= 0:
            raise ValueError("Budget amount must be positive")
        
        if budget_data.start_date and budget_data.end_date:
            if budget_data.start_date >= budget_data.end_date:
                raise ValueError("Start date must be before end date")
        
        # Update fields
        update_data = budget_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(budget, field, value)
        
        budget.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(budget)
        
        return self._to_budget_response(budget)
    
    def delete_budget(self, budget_id: UUID, db: Session) -> bool:
        """
        Delete a budget.
        
        Args:
            budget_id: Budget unique identifier
            db: Database session
            
        Returns:
            True if deleted, False if not found
        """
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            return False
        
        db.delete(budget)
        db.commit()
        
        return True
    
    def get_budget_progress(self, budget_id: UUID, db: Session) -> Optional[BudgetProgressResponse]:
        """
        Get budget progress and spending analysis.
        
        Args:
            budget_id: Budget unique identifier
            db: Database session
            
        Returns:
            Budget progress response or None if not found
        """
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            return None
        
        # Calculate current period
        current_date = date.today()
        if current_date < budget.start_date:
            # Budget hasn't started yet
            return BudgetProgressResponse(
                budget_id=budget.id,
                budget_name=budget.name,
                total_amount=budget.amount,
                spent_amount=Decimal('0'),
                remaining_amount=budget.amount,
                progress_percentage=0.0,
                days_remaining=0,
                is_over_budget=False,
                alert_level="none"
            )
        
        if current_date > budget.end_date:
            # Budget period has ended
            end_date = budget.end_date
        else:
            end_date = current_date
        
        # Calculate spending for the period
        spent_query = db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.category_id == budget.category_id,
                Transaction.date >= budget.start_date,
                Transaction.date <= end_date,
                Transaction.amount < 0  # Only expenses
            )
        )
        
        spent_amount = spent_query.scalar() or Decimal('0')
        spent_amount = abs(spent_amount)  # Convert to positive for comparison
        
        # Calculate progress
        remaining_amount = budget.amount - spent_amount
        progress_percentage = (spent_amount / budget.amount * 100) if budget.amount > 0 else 0
        
        # Calculate days remaining
        if current_date <= budget.end_date:
            days_remaining = (budget.end_date - current_date).days
        else:
            days_remaining = 0
        
        # Determine alert level
        alert_level = "none"
        if progress_percentage >= budget.alert_threshold:
            alert_level = "warning"
        if progress_percentage >= 100:
            alert_level = "critical"
        
        return BudgetProgressResponse(
            budget_id=budget.id,
            budget_name=budget.name,
            total_amount=budget.amount,
            spent_amount=spent_amount,
            remaining_amount=remaining_amount,
            progress_percentage=progress_percentage,
            days_remaining=days_remaining,
            is_over_budget=spent_amount > budget.amount,
            alert_level=alert_level
        )
    
    def get_budget_alerts(self, budget_id: UUID, db: Session) -> Optional[List[BudgetAlertResponse]]:
        """
        Get budget alerts and notifications.
        
        Args:
            budget_id: Budget unique identifier
            db: Database session
            
        Returns:
            List of budget alerts or None if budget not found
        """
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            return None
        
        alerts = []
        progress = self.get_budget_progress(budget_id, db)
        
        if not progress:
            return alerts
        
        # Check for various alert conditions
        if progress.progress_percentage >= 100:
            alerts.append(BudgetAlertResponse(
                type="over_budget",
                message=f"Budget '{budget.name}' has been exceeded by {progress.spent_amount - progress.total_amount}",
                severity="critical",
                created_at=datetime.utcnow()
            ))
        elif progress.progress_percentage >= budget.alert_threshold:
            alerts.append(BudgetAlertResponse(
                type="threshold_warning",
                message=f"Budget '{budget.name}' is {progress.progress_percentage:.1f}% used",
                severity="warning",
                created_at=datetime.utcnow()
            ))
        
        # Check for rapid spending alerts
        if progress.days_remaining > 0:
            daily_spending_rate = progress.spent_amount / (progress.days_remaining + 1)
            projected_total = daily_spending_rate * (budget.end_date - budget.start_date).days
            
            if projected_total > budget.amount * 1.2:  # 20% over projection
                alerts.append(BudgetAlertResponse(
                    type="spending_rate_warning",
                    message=f"Current spending rate suggests budget '{budget.name}' will be exceeded",
                    severity="warning",
                    created_at=datetime.utcnow()
                ))
        
        return alerts
    
    def activate_budget(self, budget_id: UUID, db: Session) -> Optional[BudgetResponse]:
        """
        Activate a budget.
        
        Args:
            budget_id: Budget unique identifier
            db: Database session
            
        Returns:
            Activated budget response or None if not found
            
        Raises:
            ValueError: If budget cannot be activated
        """
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            return None
        
        # Check if budget can be activated
        if budget.start_date > date.today():
            raise ValueError("Cannot activate budget before start date")
        
        if budget.end_date < date.today():
            raise ValueError("Cannot activate budget after end date")
        
        budget.is_active = True
        budget.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(budget)
        
        return self._to_budget_response(budget)
    
    def deactivate_budget(self, budget_id: UUID, db: Session) -> Optional[BudgetResponse]:
        """
        Deactivate a budget.
        
        Args:
            budget_id: Budget unique identifier
            db: Database session
            
        Returns:
            Deactivated budget response or None if not found
        """
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            return None
        
        budget.is_active = False
        budget.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(budget)
        
        return self._to_budget_response(budget)
    
    def get_budgets_by_category(self, category_id: UUID, db: Session) -> List[BudgetResponse]:
        """
        Get all budgets for a specific category.
        
        Args:
            category_id: Category unique identifier
            db: Database session
            
        Returns:
            List of budgets for the category
        """
        budgets = db.query(Budget).filter(Budget.category_id == category_id).all()
        return [self._to_budget_response(budget) for budget in budgets]
    
    def get_budgets_overview(self, db: Session) -> Dict[str, Any]:
        """
        Get overview of all budgets with summary statistics.
        
        Args:
            db: Database session
            
        Returns:
            Budget overview with summary data
        """
        total_budgets = db.query(Budget).count()
        active_budgets = db.query(Budget).filter(Budget.is_active == True).count()
        
        # Calculate total budget amounts
        total_budget_amount = db.query(func.sum(Budget.amount)).scalar() or Decimal('0')
        
        # Calculate total spent across all budgets
        total_spent = Decimal('0')
        budgets = db.query(Budget).filter(Budget.is_active == True).all()
        
        for budget in budgets:
            progress = self.get_budget_progress(budget.id, db)
            if progress:
                total_spent += progress.spent_amount
        
        # Calculate overall progress
        overall_progress = (total_spent / total_budget_amount * 100) if total_budget_amount > 0 else 0
        
        # Count budgets by alert level
        critical_budgets = 0
        warning_budgets = 0
        
        for budget in budgets:
            progress = self.get_budget_progress(budget.id, db)
            if progress:
                if progress.alert_level == "critical":
                    critical_budgets += 1
                elif progress.alert_level == "warning":
                    warning_budgets += 1
        
        return {
            "total_budgets": total_budgets,
            "active_budgets": active_budgets,
            "total_budget_amount": total_budget_amount,
            "total_spent": total_spent,
            "overall_progress_percentage": overall_progress,
            "alert_summary": {
                "critical": critical_budgets,
                "warning": warning_budgets,
                "healthy": active_budgets - critical_budgets - warning_budgets
            }
        }
    
    def bulk_create_budgets(self, budgets_data: List[BudgetCreate], db: Session) -> List[BudgetResponse]:
        """
        Create multiple budgets in a single operation.
        
        Args:
            budgets_data: List of budget creation data
            db: Database session
            
        Returns:
            List of created budget responses
        """
        created_budgets = []
        
        for budget_data in budgets_data:
            try:
                budget_response = self.create_budget(budget_data, db)
                created_budgets.append(budget_response)
            except ValueError as e:
                # Log error but continue with other budgets
                print(f"Failed to create budget {budget_data.name}: {e}")
                continue
        
        return created_budgets
    
    def bulk_delete_budgets(self, budget_ids: List[UUID], db: Session) -> bool:
        """
        Delete multiple budgets in a single operation.
        
        Args:
            budget_ids: List of budget IDs to delete
            db: Database session
            
        Returns:
            True if all budgets were deleted successfully
        """
        try:
            db.query(Budget).filter(Budget.id.in_(budget_ids)).delete(synchronize_session=False)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Failed to delete budgets: {e}")
            return False
    
    def _to_budget_response(self, budget: Budget) -> BudgetResponse:
        """
        Convert budget model to response schema.
        
        Args:
            budget: Budget model instance
            
        Returns:
            Budget response schema
        """
        return BudgetResponse(
            id=budget.id,
            name=budget.name,
            category_id=budget.category_id,
            amount=budget.amount,
            period_type=budget.period_type,
            start_date=budget.start_date,
            end_date=budget.end_date,
            alert_threshold=budget.alert_threshold,
            is_active=budget.is_active,
            created_at=budget.created_at,
            updated_at=budget.updated_at
        )
