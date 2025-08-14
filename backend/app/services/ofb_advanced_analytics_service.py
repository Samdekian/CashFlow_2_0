"""
Open Finance Brasil Advanced Analytics Service
Provides advanced analytics and insights based on aggregated OFB data.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from collections import defaultdict, Counter
import statistics

from ..core.open_finance_brasil import OpenFinanceBrasilIntegration
from ..services.ofb_multi_bank_service import OFBMultiBankService
from ..services.ofb_account_service import OFBAccountService

logger = logging.getLogger(__name__)


class OFBAdvancedAnalyticsService:
    """Service for advanced analytics and insights based on OFB data."""
    
    def __init__(self, db, ofb_integration: OpenFinanceBrasilIntegration):
        self.db = db
        self.ofb_integration = ofb_integration
        self.multi_bank_service = OFBMultiBankService(db, ofb_integration)
        self.account_service = OFBAccountService(db)
        
        # Mock transaction data for analytics (replace with database queries)
        self.mock_transactions = [
            {
                "id": "txn_001",
                "date": (datetime.utcnow() - timedelta(days=1)).date(),
                "amount": 150.00,
                "type": "EXPENSE",
                "category": "ALIMENTACAO",
                "bank": "Banco do Brasil",
                "account": "Conta Corrente"
            },
            {
                "id": "txn_002",
                "date": (datetime.utcnow() - timedelta(days=2)).date(),
                "amount": 80.00,
                "type": "EXPENSE",
                "category": "TRANSPORTE",
                "bank": "Itaú Unibanco",
                "account": "Conta Corrente"
            },
            {
                "id": "txn_003",
                "date": (datetime.utcnow() - timedelta(days=3)).date(),
                "amount": 5000.00,
                "type": "INCOME",
                "category": "SALARIO",
                "bank": "Banco do Brasil",
                "account": "Conta Corrente"
            },
            {
                "id": "txn_004",
                "date": (datetime.utcnow() - timedelta(days=4)).date(),
                "amount": 200.00,
                "type": "EXPENSE",
                "category": "MORADIA",
                "bank": "Bradesco",
                "account": "Conta Corrente"
            },
            {
                "id": "txn_005",
                "date": (datetime.utcnow() - timedelta(days=5)).date(),
                "amount": 120.00,
                "type": "EXPENSE",
                "category": "LAZER",
                "bank": "Banco do Brasil",
                "account": "Conta Corrente"
            }
        ]
    
    async def get_cash_flow_analysis(
        self,
        user_id: str,
        period: str = "monthly",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Analyze cash flow patterns across all connected banks."""
        try:
            # Get aggregated balance
            balance_data = await self.multi_bank_service.get_aggregated_balance(user_id)
            
            # Analyze transaction patterns
            transactions = self._filter_transactions_by_period(from_date, to_date)
            
            # Calculate income and expenses
            income = sum(t["amount"] for t in transactions if t["type"] == "INCOME")
            expenses = sum(t["amount"] for t in transactions if t["type"] == "EXPENSE")
            net_flow = income - expenses
            
            # Calculate cash flow metrics
            cash_flow_metrics = {
                "total_income": income,
                "total_expenses": expenses,
                "net_cash_flow": net_flow,
                "savings_rate": (net_flow / income * 100) if income > 0 else 0,
                "expense_ratio": (expenses / income * 100) if income > 0 else 0
            }
            
            # Analyze trends
            trends = self._analyze_cash_flow_trends(transactions, period)
            
            # Generate insights
            insights = self._generate_cash_flow_insights(cash_flow_metrics, trends)
            
            return {
                "period": period,
                "date_range": {
                    "from": from_date.isoformat() if from_date else None,
                    "to": to_date.isoformat() if to_date else None
                },
                "current_balance": balance_data["total_balance"],
                "cash_flow_metrics": cash_flow_metrics,
                "trends": trends,
                "insights": insights,
                "analysis_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Cash flow analysis failed: {str(e)}")
            raise
    
    async def get_spending_patterns(
        self,
        user_id: str,
        category_level: str = "PRIMARY",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Analyze spending patterns by category and bank."""
        try:
            transactions = self._filter_transactions_by_period(from_date, to_date)
            expense_transactions = [t for t in transactions if t["type"] == "EXPENSE"]
            
            # Group by category
            category_spending = defaultdict(float)
            bank_spending = defaultdict(float)
            category_bank_matrix = defaultdict(lambda: defaultdict(float))
            
            for transaction in expense_transactions:
                category = transaction["category"]
                bank = transaction["bank"]
                amount = transaction["amount"]
                
                category_spending[category] += amount
                bank_spending[bank] += amount
                category_bank_matrix[category][bank] += amount
            
            # Calculate percentages
            total_expenses = sum(category_spending.values())
            category_percentages = {
                cat: (amount / total_expenses * 100) if total_expenses > 0 else 0
                for cat, amount in category_spending.items()
            }
            
            bank_percentages = {
                bank: (amount / total_expenses * 100) if total_expenses > 0 else 0
                for bank, amount in bank_spending.items()
            }
            
            # Identify top spending categories
            top_categories = sorted(
                category_spending.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Generate insights
            insights = self._generate_spending_insights(
                category_spending, bank_spending, total_expenses
            )
            
            return {
                "total_expenses": total_expenses,
                "category_breakdown": dict(category_spending),
                "category_percentages": category_percentages,
                "bank_breakdown": dict(bank_spending),
                "bank_percentages": bank_percentages,
                "category_bank_matrix": dict(category_bank_matrix),
                "top_categories": top_categories,
                "insights": insights,
                "analysis_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Spending pattern analysis failed: {str(e)}")
            raise
    
    async def get_bank_performance_analysis(
        self,
        user_id: str,
        analysis_period: str = "30_days"
    ) -> Dict[str, Any]:
        """Analyze performance and efficiency of connected banks."""
        try:
            # Get bank health status
            health_status = await self.multi_bank_service.get_bank_health_status(user_id)
            
            # Get aggregated balance for comparison
            balance_data = await self.multi_bank_service.get_aggregated_balance(user_id)
            
            # Analyze bank performance metrics
            bank_performance = []
            
            for bank_health in health_status["health_details"]:
                bank_name = bank_health["bank_name"]
                bank_code = bank_health["bank_code"]
                
                # Find bank balance
                bank_balance = next(
                    (b["total_balance"] for b in balance_data["bank_breakdown"] 
                     if b["bank_code"] == bank_code),
                    0.0
                )
                
                # Calculate performance score
                performance_score = self._calculate_bank_performance_score(bank_health, bank_balance)
                
                # Generate recommendations
                recommendations = self._generate_bank_recommendations(bank_health, bank_balance)
                
                bank_performance.append({
                    "bank_name": bank_name,
                    "bank_code": bank_code,
                    "health_status": bank_health,
                    "balance": bank_balance,
                    "performance_score": performance_score,
                    "recommendations": recommendations
                })
            
            # Overall performance summary
            overall_score = statistics.mean([bp["performance_score"] for bp in bank_performance])
            
            return {
                "overall_performance_score": overall_score,
                "bank_performance": bank_performance,
                "health_summary": health_status,
                "balance_summary": balance_data,
                "analysis_period": analysis_period,
                "analysis_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Bank performance analysis failed: {str(e)}")
            raise
    
    async def get_financial_health_score(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Calculate overall financial health score based on OFB data."""
        try:
            # Get various metrics
            balance_data = await self.multi_bank_service.get_aggregated_balance(user_id)
            health_status = await self.multi_bank_service.get_bank_health_status(user_id)
            
            # Calculate component scores
            balance_score = self._calculate_balance_score(balance_data)
            bank_health_score = self._calculate_bank_health_score(health_status)
            cash_flow_score = await self._calculate_cash_flow_score(user_id)
            
            # Weighted overall score
            overall_score = (
                balance_score * 0.3 +
                bank_health_score * 0.3 +
                cash_flow_score * 0.4
            )
            
            # Determine health level
            if overall_score >= 80:
                health_level = "EXCELLENT"
            elif overall_score >= 70:
                health_level = "GOOD"
            elif overall_score >= 60:
                health_level = "FAIR"
            elif overall_score >= 50:
                health_level = "POOR"
            else:
                health_level = "CRITICAL"
            
            # Generate recommendations
            recommendations = self._generate_financial_health_recommendations(
                balance_score, bank_health_score, cash_flow_score
            )
            
            return {
                "overall_score": overall_score,
                "health_level": health_level,
                "component_scores": {
                    "balance_score": balance_score,
                    "bank_health_score": bank_health_score,
                    "cash_flow_score": cash_flow_score
                },
                "recommendations": recommendations,
                "calculation_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Financial health score calculation failed: {str(e)}")
            raise
    
    def _filter_transactions_by_period(
        self,
        from_date: Optional[datetime],
        to_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """Filter transactions by date period."""
        if not from_date and not to_date:
            # Default to last 30 days
            from_date = datetime.utcnow() - timedelta(days=30)
            to_date = datetime.utcnow()
        
        filtered_transactions = []
        for transaction in self.mock_transactions:
            tx_date = transaction["date"]
            if from_date and tx_date < from_date.date():
                continue
            if to_date and tx_date > to_date.date():
                continue
            filtered_transactions.append(transaction)
        
        return filtered_transactions
    
    def _analyze_cash_flow_trends(
        self,
        transactions: List[Dict[str, Any]],
        period: str
    ) -> Dict[str, Any]:
        """Analyze cash flow trends over time."""
        # Group transactions by period
        period_groups = defaultdict(lambda: {"income": 0, "expenses": 0})
        
        for transaction in transactions:
            if period == "daily":
                period_key = transaction["date"].strftime("%Y-%m-%d")
            elif period == "weekly":
                period_key = transaction["date"].strftime("%Y-W%W")
            elif period == "monthly":
                period_key = transaction["date"].strftime("%Y-%m")
            else:
                period_key = transaction["date"].strftime("%Y-%m")
            
            if transaction["type"] == "INCOME":
                period_groups[period_key]["income"] += transaction["amount"]
            else:
                period_groups[period_key]["expenses"] += transaction["amount"]
        
        # Calculate trends
        periods = sorted(period_groups.keys())
        if len(periods) >= 2:
            income_trend = self._calculate_trend(
                [period_groups[p]["income"] for p in periods]
            )
            expense_trend = self._calculate_trend(
                [period_groups[p]["expenses"] for p in periods]
            )
        else:
            income_trend = "STABLE"
            expense_trend = "STABLE"
        
        return {
            "periods": periods,
            "period_data": dict(period_groups),
            "income_trend": income_trend,
            "expense_trend": expense_trend
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values."""
        if len(values) < 2:
            return "STABLE"
        
        # Simple trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = statistics.mean(first_half) if first_half else 0
        second_avg = statistics.mean(second_half) if second_half else 0
        
        if second_avg > first_avg * 1.1:
            return "INCREASING"
        elif second_avg < first_avg * 0.9:
            return "DECREASING"
        else:
            return "STABLE"
    
    def _generate_cash_flow_insights(
        self,
        metrics: Dict[str, Any],
        trends: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from cash flow analysis."""
        insights = []
        
        if metrics["savings_rate"] < 20:
            insights.append("Your savings rate is below the recommended 20%. Consider reducing expenses or increasing income.")
        
        if metrics["expense_ratio"] > 90:
            insights.append("Your expenses are consuming most of your income. Look for ways to reduce spending.")
        
        if trends["income_trend"] == "DECREASING":
            insights.append("Your income appears to be decreasing. Review your income sources and consider additional revenue streams.")
        
        if trends["expense_trend"] == "INCREASING":
            insights.append("Your expenses are increasing. Monitor your spending patterns and identify areas for cost reduction.")
        
        if not insights:
            insights.append("Your cash flow appears healthy. Keep up the good financial management!")
        
        return insights
    
    def _generate_spending_insights(
        self,
        category_spending: Dict[str, float],
        bank_spending: Dict[str, float],
        total_expenses: float
    ) -> List[str]:
        """Generate insights from spending pattern analysis."""
        insights = []
        
        # Category insights
        top_category = max(category_spending.items(), key=lambda x: x[1])
        if top_category[1] > total_expenses * 0.4:
            insights.append(f"Your top spending category ({top_category[0]}) represents over 40% of expenses. Consider diversifying your spending.")
        
        # Bank insights
        if len(bank_spending) > 1:
            insights.append(f"You're using {len(bank_spending)} different banks. This provides good diversification but may increase complexity.")
        
        return insights
    
    def _calculate_bank_performance_score(
        self,
        health_status: Dict[str, Any],
        balance: float
    ) -> float:
        """Calculate performance score for a bank."""
        score = 0.0
        
        # Sync status scoring
        sync_status_scores = {
            "EXCELLENT": 100,
            "GOOD": 80,
            "WARNING": 60,
            "CRITICAL": 20,
            "NEVER_SYNCED": 0
        }
        score += sync_status_scores.get(health_status["sync_status"], 0) * 0.4
        
        # Account status scoring
        if health_status["account_status"] == "HEALTHY":
            score += 100 * 0.3
        elif health_status["account_status"] == "NO_ACCOUNTS":
            score += 0 * 0.3
        
        # Balance scoring (normalized)
        if balance > 0:
            score += min(100, (balance / 10000) * 100) * 0.3  # Cap at 10k for scoring
        
        return round(score, 2)
    
    def _generate_bank_recommendations(
        self,
        health_status: Dict[str, Any],
        balance: float
    ) -> List[str]:
        """Generate recommendations for a bank."""
        recommendations = []
        
        if health_status["sync_status"] in ["WARNING", "CRITICAL"]:
            recommendations.append("Schedule a manual sync to update your account data.")
        
        if health_status["account_status"] == "NO_ACCOUNTS":
            recommendations.append("No accounts found. Verify your bank connection and permissions.")
        
        if balance == 0:
            recommendations.append("Consider maintaining a minimum balance for emergency funds.")
        
        return recommendations
    
    def _calculate_balance_score(self, balance_data: Dict[str, Any]) -> float:
        """Calculate balance component score."""
        total_balance = balance_data["total_balance"]
        
        # Simple scoring based on balance tiers
        if total_balance >= 10000:
            return 100
        elif total_balance >= 5000:
            return 80
        elif total_balance >= 2000:
            return 60
        elif total_balance >= 500:
            return 40
        else:
            return 20
    
    def _calculate_bank_health_score(self, health_status: Dict[str, Any]) -> float:
        """Calculate bank health component score."""
        healthy_banks = health_status["healthy_banks"]
        total_banks = health_status["total_banks"]
        
        if total_banks == 0:
            return 0
        
        return (healthy_banks / total_banks) * 100
    
    async def _calculate_cash_flow_score(self, user_id: str) -> float:
        """Calculate cash flow component score."""
        try:
            # Get cash flow analysis for last 30 days
            cash_flow = await self.get_cash_flow_analysis(user_id, "monthly")
            metrics = cash_flow["cash_flow_metrics"]
            
            # Score based on savings rate
            savings_rate = metrics["savings_rate"]
            if savings_rate >= 20:
                return 100
            elif savings_rate >= 15:
                return 80
            elif savings_rate >= 10:
                return 60
            elif savings_rate >= 5:
                return 40
            else:
                return 20
                
        except Exception:
            return 50  # Default score if analysis fails
    
    def _generate_financial_health_recommendations(
        self,
        balance_score: float,
        bank_health_score: float,
        cash_flow_score: float
    ) -> List[str]:
        """Generate overall financial health recommendations."""
        recommendations = []
        
        if balance_score < 60:
            recommendations.append("Focus on building your emergency fund and savings.")
        
        if bank_health_score < 80:
            recommendations.append("Review and optimize your bank connections for better data synchronization.")
        
        if cash_flow_score < 60:
            recommendations.append("Work on improving your cash flow by increasing income or reducing expenses.")
        
        if not recommendations:
            recommendations.append("Your financial health is excellent! Continue maintaining good financial habits.")
        
        return recommendations
