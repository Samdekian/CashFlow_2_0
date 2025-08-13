"""
Transaction service for managing financial transactions.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.exc import IntegrityError

from ..models.transaction import Transaction
from ..models.category import Category
from ..schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionFilters,
    TransactionSummary,
    BulkTransactionOperation
)
from ..schemas.common import PaginationParams, PaginatedResponse
from .categorization_service import CategorizationService


class TransactionService:
    """Service for managing financial transactions."""
    
    def __init__(self, db: Session):
        self.db = db
        self.categorization_service = CategorizationService(db)
    
    def create_transaction(self, transaction_data: TransactionCreate) -> Transaction:
        """Create a new transaction."""
        try:
            # Auto-categorize if no category is provided
            if not transaction_data.category_id:
                suggested_category = self.categorization_service.suggest_category(
                    transaction_data.description,
                    float(transaction_data.amount)
                )
                if suggested_category:
                    transaction_data.category_id = suggested_category.id
            
            # Create transaction instance
            db_transaction = Transaction(
                date=transaction_data.date,
                amount=transaction_data.amount,
                description=transaction_data.description,
                transaction_type=transaction_data.transaction_type,
                category_id=transaction_data.category_id,
                account=transaction_data.account,
                account_type=transaction_data.account_type,
                currency=transaction_data.currency,
                country_code=transaction_data.country_code,
                reference_number=transaction_data.reference_number,
                institution_code=transaction_data.institution_code,
                is_recurring=transaction_data.is_recurring,
                recurring_pattern=transaction_data.recurring_pattern,
                tags=transaction_data.tags,
                notes=transaction_data.notes
            )
            
            self.db.add(db_transaction)
            self.db.commit()
            self.db.refresh(db_transaction)
            
            return db_transaction
            
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create transaction: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Unexpected error creating transaction: {str(e)}")
    
    def get_transaction(self, transaction_id: UUID) -> Optional[Transaction]:
        """Get a transaction by ID."""
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    def get_transactions(
        self,
        filters: Optional[TransactionFilters] = None,
        pagination: Optional[PaginationParams] = None
    ) -> PaginatedResponse:
        """Get transactions with filtering and pagination."""
        query = self.db.query(Transaction)
        
        # Apply filters
        if filters:
            query = self._apply_transaction_filters(query, filters)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        if pagination:
            query = query.offset(pagination.offset).limit(pagination.limit)
        
        # Order by date (newest first)
        query = query.order_by(desc(Transaction.date), desc(Transaction.created_at))
        
        # Execute query
        transactions = query.all()
        
        # Create paginated response
        if pagination:
            return PaginatedResponse(
                items=transactions,
                total=total,
                page=pagination.page,
                size=pagination.size
            )
        else:
            return PaginatedResponse(
                items=transactions,
                total=total,
                page=1,
                size=total
            )
    
    def update_transaction(self, transaction_id: UUID, update_data: TransactionUpdate) -> Optional[Transaction]:
        """Update an existing transaction."""
        db_transaction = self.get_transaction(transaction_id)
        if not db_transaction:
            return None
        
        try:
            # Update fields
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(db_transaction, field, value)
            
            # Update timestamp
            db_transaction.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_transaction)
            
            return db_transaction
            
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to update transaction: {str(e)}")
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Unexpected error updating transaction: {str(e)}")
    
    def delete_transaction(self, transaction_id: UUID) -> bool:
        """Delete a transaction."""
        db_transaction = self.get_transaction(transaction_id)
        if not db_transaction:
            return False
        
        try:
            self.db.delete(db_transaction)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to delete transaction: {str(e)}")
    
    def search_transactions(self, search_criteria: str, limit: int = 50) -> List[Transaction]:
        """Search transactions by description and notes."""
        query = self.db.query(Transaction).filter(
            or_(
                Transaction.description.ilike(f"%{search_criteria}%"),
                Transaction.notes.ilike(f"%{search_criteria}%")
            )
        )
        
        return query.order_by(desc(Transaction.date)).limit(limit).all()
    
    def get_transaction_summary(self, date_range: Optional[Tuple[date, date]] = None) -> TransactionSummary:
        """Get transaction summary statistics."""
        query = self.db.query(Transaction)
        
        # Apply date range filter
        if date_range:
            start_date, end_date = date_range
            query = query.filter(
                and_(Transaction.date >= start_date, Transaction.date <= end_date)
            )
        
        # Get all transactions for summary
        transactions = query.all()
        
        # Calculate summary statistics
        total_transactions = len(transactions)
        total_income = sum(t.amount for t in transactions if t.is_income)
        total_expenses = sum(abs(t.amount) for t in transactions if t.is_expense)
        total_transfers = sum(abs(t.amount) for t in transactions if t.is_transfer)
        total_investments = sum(abs(t.amount) for t in transactions if t.is_investment)
        
        net_amount = total_income - total_expenses
        average_transaction = (total_income + total_expenses + total_transfers + total_investments) / total_transactions if total_transactions > 0 else Decimal('0')
        
        return TransactionSummary(
            total_transactions=total_transactions,
            total_income=total_income,
            total_expenses=total_expenses,
            total_transfers=total_transfers,
            total_investments=total_investments,
            net_amount=net_amount,
            average_transaction=average_transaction
        )
    
    def bulk_operation(self, operation_data: BulkTransactionOperation) -> Dict[str, Any]:
        """Perform bulk operations on transactions."""
        results = {
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }
        
        for transaction_id in operation_data.transaction_ids:
            try:
                if operation_data.operation == "delete":
                    if self.delete_transaction(transaction_id):
                        results["success_count"] += 1
                    else:
                        results["error_count"] += 1
                        results["errors"].append(f"Transaction {transaction_id} not found")
                
                elif operation_data.operation == "update" and operation_data.update_data:
                    if self.update_transaction(transaction_id, operation_data.update_data):
                        results["success_count"] += 1
                    else:
                        results["error_count"] += 1
                        results["errors"].append(f"Transaction {transaction_id} not found")
                
                elif operation_data.operation == "categorize" and operation_data.category_id:
                    update_data = TransactionUpdate(category_id=operation_data.category_id)
                    if self.update_transaction(transaction_id, update_data):
                        results["success_count"] += 1
                    else:
                        results["error_count"] += 1
                        results["errors"].append(f"Transaction {transaction_id} not found")
                
            except Exception as e:
                results["error_count"] += 1
                results["errors"].append(f"Error processing transaction {transaction_id}: {str(e)}")
        
        return results
    
    def get_transactions_by_category(self, category_id: UUID, limit: int = 100) -> List[Transaction]:
        """Get transactions for a specific category."""
        return self.db.query(Transaction).filter(
            Transaction.category_id == category_id
        ).order_by(desc(Transaction.date)).limit(limit).all()
    
    def get_recent_transactions(self, limit: int = 10) -> List[Transaction]:
        """Get recent transactions."""
        return self.db.query(Transaction).order_by(
            desc(Transaction.created_at)
        ).limit(limit).all()
    
    def get_transactions_by_date_range(self, start_date: date, end_date: date) -> List[Transaction]:
        """Get transactions within a date range."""
        return self.db.query(Transaction).filter(
            and_(Transaction.date >= start_date, Transaction.date <= end_date)
        ).order_by(desc(Transaction.date)).all()
    
    def _apply_transaction_filters(self, query, filters: TransactionFilters):
        """Apply transaction filters to query."""
        if filters.date_range:
            query = query.filter(
                and_(
                    Transaction.date >= filters.date_range.start_date,
                    Transaction.date <= filters.date_range.end_date
                )
            )
        
        if filters.category_ids:
            query = query.filter(Transaction.category_id.in_(filters.category_ids))
        
        if filters.transaction_types:
            query = query.filter(Transaction.transaction_type.in_(filters.transaction_types))
        
        if filters.min_amount is not None:
            query = query.filter(Transaction.amount >= filters.min_amount)
        
        if filters.max_amount is not None:
            query = query.filter(Transaction.amount <= filters.max_amount)
        
        if filters.accounts:
            query = query.filter(Transaction.account.in_(filters.accounts))
        
        if filters.tags:
            # Filter by tags (assuming tags is a JSON array)
            for tag in filters.tags:
                query = query.filter(Transaction.tags.contains([tag]))
        
        if filters.is_recurring is not None:
            query = query.filter(Transaction.is_recurring == filters.is_recurring)
        
        if filters.search_query:
            query = query.filter(
                or_(
                    Transaction.description.ilike(f"%{filters.search_query}%"),
                    Transaction.notes.ilike(f"%{filters.search_query}%")
                )
            )
        
        return query
    
    def get_transaction_statistics_by_period(
        self,
        start_date: date,
        end_date: date,
        group_by: str = "month"
    ) -> List[Dict[str, Any]]:
        """Get transaction statistics grouped by period."""
        if group_by == "month":
            date_format = func.strftime("%Y-%m", Transaction.date)
        elif group_by == "week":
            date_format = func.strftime("%Y-W%W", Transaction.date)
        elif group_by == "day":
            date_format = func.date(Transaction.date)
        else:
            raise ValueError("group_by must be 'day', 'week', or 'month'")
        
        query = self.db.query(
            date_format.label("period"),
            func.count(Transaction.id).label("count"),
            func.sum(Transaction.amount).label("total_amount"),
            func.avg(Transaction.amount).label("avg_amount")
        ).filter(
            and_(Transaction.date >= start_date, Transaction.date <= end_date)
        ).group_by(date_format).order_by(date_format)
        
        return [dict(row) for row in query.all()]
    
    def detect_duplicate_transactions(
        self,
        date: date,
        amount: Decimal,
        description: str,
        tolerance_days: int = 1
    ) -> List[Transaction]:
        """Detect potential duplicate transactions."""
        start_date = date - datetime.timedelta(days=tolerance_days)
        end_date = date + datetime.timedelta(days=tolerance_days)
        
        return self.db.query(Transaction).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.amount == amount,
                Transaction.description.ilike(f"%{description}%")
            )
        ).all()
