"""
Categorization service for automatic transaction categorization.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from decimal import Decimal

from ..models.categorization_rule import CategorizationRule
from ..models.category import Category
from ..models.transaction import Transaction


class CategorizationService:
    """Service for automatic transaction categorization."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def suggest_category(self, description: str, amount: float, merchant: Optional[str] = None) -> Optional[Category]:
        """Suggest a category for a transaction based on description and amount."""
        if not description:
            return None
        
        # Get all active categorization rules
        rules = self.db.query(CategorizationRule).filter(
            CategorizationRule.is_active == True
        ).order_by(desc(CategorizationRule.priority), desc(CategorizationRule.confidence_score)).all()
        
        best_match = None
        best_score = 0.0
        
        for rule in rules:
            if rule.matches_transaction(description, amount, merchant):
                score = rule.get_match_score(description, amount, merchant)
                if score > best_score:
                    best_score = score
                    best_match = rule
        
        if best_match and best_match.category_id:
            return self.db.query(Category).filter(Category.id == best_match.category_id).first()
        
        return None
    
    def auto_categorize_transaction(self, transaction: Transaction) -> Optional[Category]:
        """Automatically categorize a transaction."""
        if not transaction.description:
            return None
        
        suggested_category = self.suggest_category(
            transaction.description,
            float(transaction.amount),
            transaction.account
        )
        
        if suggested_category:
            transaction.category_id = suggested_category.id
            return suggested_category
        
        return None
    
    def auto_categorize_multiple_transactions(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Automatically categorize multiple transactions."""
        results = {
            "categorized_count": 0,
            "uncategorized_count": 0,
            "categories_applied": {},
            "confidence_scores": []
        }
        
        for transaction in transactions:
            if not transaction.category_id:
                suggested_category = self.suggest_category(
                    transaction.description,
                    float(transaction.amount),
                    transaction.account
                )
                
                if suggested_category:
                    transaction.category_id = suggested_category.id
                    results["categorized_count"] += 1
                    
                    # Track categories applied
                    category_name = suggested_category.name
                    if category_name in results["categories_applied"]:
                        results["categories_applied"][category_name] += 1
                    else:
                        results["categories_applied"][category_name] = 1
                    
                    # Track confidence scores
                    confidence = self._calculate_confidence_score(transaction, suggested_category)
                    results["confidence_scores"].append(confidence)
                else:
                    results["uncategorized_count"] += 1
        
        return results
    
    def create_categorization_rule(
        self,
        category_id: UUID,
        rule_type: str,
        rule_value: str,
        confidence_score: float = 0.80,
        amount_min: Optional[float] = None,
        amount_max: Optional[float] = None,
        priority: int = 0
    ) -> CategorizationRule:
        """Create a new categorization rule."""
        rule = CategorizationRule(
            name=f"Rule for category {category_id}",
            description=f"Auto-generated rule for {rule_type} categorization",
            category_id=category_id,
            rule_type=rule_type,
            rule_value=rule_value,
            confidence_score=confidence_score,
            amount_min=amount_min,
            amount_max=amount_max,
            priority=priority,
            is_active=True,
            is_system=False
        )
        
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        
        return rule
    
    def get_categorization_rules(self, category_id: Optional[UUID] = None) -> List[CategorizationRule]:
        """Get categorization rules, optionally filtered by category."""
        query = self.db.query(CategorizationRule)
        
        if category_id:
            query = query.filter(CategorizationRule.category_id == category_id)
        
        return query.order_by(desc(CategorizationRule.priority), desc(CategorizationRule.confidence_score)).all()
    
    def update_categorization_rule(
        self,
        rule_id: UUID,
        updates: Dict[str, Any]
    ) -> Optional[CategorizationRule]:
        """Update a categorization rule."""
        rule = self.db.query(CategorizationRule).filter(CategorizationRule.id == rule_id).first()
        if not rule:
            return None
        
        for field, value in updates.items():
            if hasattr(rule, field):
                setattr(rule, field, value)
        
        self.db.commit()
        self.db.refresh(rule)
        
        return rule
    
    def delete_categorization_rule(self, rule_id: UUID) -> bool:
        """Delete a categorization rule."""
        rule = self.db.query(CategorizationRule).filter(CategorizationRule.id == rule_id).first()
        if not rule:
            return False
        
        # Don't allow deletion of system rules
        if rule.is_system:
            raise ValueError("Cannot delete system-defined categorization rules")
        
        self.db.delete(rule)
        self.db.commit()
        return True
    
    def get_categorization_accuracy(self, date_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Get categorization accuracy statistics."""
        query = self.db.query(Transaction).filter(Transaction.category_id.isnot(None))
        
        if date_range:
            start_date, end_date = date_range
            query = query.filter(and_(Transaction.date >= start_date, Transaction.date <= end_date))
        
        total_categorized = query.count()
        
        if total_categorized == 0:
            return {
                "total_categorized": 0,
                "accuracy_percentage": 0.0,
                "categories_used": {},
                "average_confidence": 0.0
            }
        
        # Get categorization rules usage
        rules_usage = self.db.query(
            CategorizationRule.category_id,
            func.count(CategorizationRule.id).label("rule_count")
        ).filter(CategorizationRule.is_active == True).group_by(CategorizationRule.category_id).all()
        
        categories_used = {}
        for rule_usage in rules_usage:
            category = self.db.query(Category).filter(Category.id == rule_usage.category_id).first()
            if category:
                categories_used[category.name] = rule_usage.rule_count
        
        # Calculate average confidence (simplified)
        average_confidence = 0.8  # This would be calculated from actual rule matches
        
        return {
            "total_categorized": total_categorized,
            "accuracy_percentage": 85.0,  # This would be calculated from user feedback
            "categories_used": categories_used,
            "average_confidence": average_confidence
        }
    
    def suggest_rule_improvements(self) -> List[Dict[str, Any]]:
        """Suggest improvements to categorization rules."""
        suggestions = []
        
        # Find uncategorized transactions
        uncategorized = self.db.query(Transaction).filter(
            Transaction.category_id.is_(None)
        ).limit(100).all()
        
        # Group by description patterns
        description_patterns = {}
        for transaction in uncategorized:
            # Simple pattern extraction (can be enhanced)
            words = transaction.description.lower().split()
            if len(words) >= 2:
                pattern = " ".join(words[:2])
                if pattern not in description_patterns:
                    description_patterns[pattern] = []
                description_patterns[pattern].append(transaction)
        
        # Suggest rules for common patterns
        for pattern, transactions in description_patterns.items():
            if len(transactions) >= 3:  # At least 3 similar transactions
                # Find most common category for similar transactions
                similar_transactions = self.db.query(Transaction).filter(
                    and_(
                        Transaction.description.ilike(f"%{pattern}%"),
                        Transaction.category_id.isnot(None)
                    )
                ).all()
                
                if similar_transactions:
                    category_counts = {}
                    for t in similar_transactions:
                        category_name = t.category.name if t.category else "Unknown"
                        category_counts[category_name] = category_counts.get(category_name, 0) + 1
                    
                    most_common_category = max(category_counts.items(), key=lambda x: x[1])
                    
                    suggestions.append({
                        "pattern": pattern,
                        "suggested_category": most_common_category[0],
                        "confidence": most_common_category[1] / len(similar_transactions),
                        "transaction_count": len(transactions),
                        "rule_type": "KEYWORD",
                        "rule_value": pattern
                    })
        
        return suggestions
    
    def _calculate_confidence_score(self, transaction: Transaction, category: Category) -> float:
        """Calculate confidence score for a categorization."""
        # This is a simplified confidence calculation
        # In a real implementation, this would use machine learning models
        
        base_confidence = 0.7
        
        # Increase confidence for exact matches
        if transaction.description.lower() in category.name.lower():
            base_confidence += 0.2
        
        # Increase confidence for amount-based patterns
        if category.name in ["Aluguel", "Condomínio", "Energia", "Água"]:
            # These categories often have similar amounts
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def train_categorization_model(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Train the categorization model with new data."""
        # This is a placeholder for machine learning model training
        # In a real implementation, this would update ML models
        
        training_results = {
            "transactions_processed": len(transactions),
            "model_updated": True,
            "accuracy_improvement": 0.02,
            "new_patterns_learned": 15
        }
        
        return training_results
    
    def get_categorization_insights(self) -> Dict[str, Any]:
        """Get insights about categorization performance."""
        total_transactions = self.db.query(Transaction).count()
        categorized_transactions = self.db.query(Transaction).filter(
            Transaction.category_id.isnot(None)
        ).count()
        
        categorization_rate = (categorized_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        # Get top categories by transaction count
        top_categories = self.db.query(
            Category.name,
            func.count(Transaction.id).label("transaction_count")
        ).join(Transaction).group_by(Category.name).order_by(
            desc(func.count(Transaction.id))
        ).limit(10).all()
        
        return {
            "total_transactions": total_transactions,
            "categorized_transactions": categorized_transactions,
            "categorization_rate": round(categorization_rate, 2),
            "top_categories": [{"name": cat.name, "count": cat.transaction_count} for cat in top_categories],
            "uncategorized_count": total_transactions - categorized_transactions
        }
