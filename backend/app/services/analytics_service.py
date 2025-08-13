"""
Analytics service for financial insights and reporting.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, extract, case
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID
import json

from ..models.transaction import Transaction
from ..models.category import Category
from ..models.budget import Budget
from ..schemas.common import DateRange
from ..schemas.analytics import (
    SpendingSummaryResponse,
    CategoryBreakdownResponse,
    TrendAnalysisResponse,
    MonthlyComparisonResponse,
    CashFlowAnalysisResponse,
    BudgetAnalysisResponse,
    SpendingPatternResponse,
    FinancialHealthResponse
)
from ..core.open_finance_standards import get_category_hierarchy


class AnalyticsService:
    """Service for financial analytics and insights."""
    
    def get_spending_summary(self, date_range: DateRange, db: Session) -> SpendingSummaryResponse:
        """
        Get comprehensive spending summary for a date range.
        
        Args:
            date_range: Date range for analysis
            db: Database session
            
        Returns:
            Spending summary with income, expenses, and net cash flow
        """
        # Query transactions in date range
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.date >= date_range.start_date,
                Transaction.date <= date_range.end_date
            )
        ).all()
        
        # Calculate totals
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = abs(sum(t.amount for t in transactions if t.amount < 0))
        net_cash_flow = total_income - total_expenses
        
        # Calculate transaction counts
        income_count = len([t for t in transactions if t.amount > 0])
        expense_count = len([t for t in transactions if t.amount < 0])
        
        # Calculate average amounts
        avg_income = total_income / income_count if income_count > 0 else Decimal('0')
        avg_expense = total_expenses / expense_count if expense_count > 0 else Decimal('0')
        
        # Calculate daily averages
        days_in_period = (date_range.end_date - date_range.start_date).days + 1
        daily_avg_income = total_income / days_in_period
        daily_avg_expense = total_expenses / days_in_period
        
        return SpendingSummaryResponse(
            period_start=date_range.start_date,
            period_end=date_range.end_date,
            total_income=total_income,
            total_expenses=total_expenses,
            net_cash_flow=net_cash_flow,
            income_count=income_count,
            expense_count=expense_count,
            avg_income=avg_income,
            avg_expense=avg_expense,
            daily_avg_income=daily_avg_income,
            daily_avg_expense=daily_avg_expense,
            savings_rate=(net_cash_flow / total_income * 100) if total_income > 0 else 0
        )
    
    def get_category_breakdown(self, date_range: DateRange, category_level: int, db: Session) -> CategoryBreakdownResponse:
        """
        Get spending breakdown by category hierarchy level.
        
        Args:
            date_range: Date range for analysis
            category_level: Category hierarchy level (1-3)
            db: Database session
            
        Returns:
            Category breakdown with spending amounts and percentages
        """
        # Build category filter based on level
        if category_level == 1:
            category_filter = Category.level == 1
        elif category_level == 2:
            category_filter = Category.level == 2
        else:
            category_filter = Category.level == 3
        
        # Query categories and their spending
        categories = db.query(
            Category.id,
            Category.name,
            Category.level,
            func.sum(case((Transaction.amount < 0, func.abs(Transaction.amount)), else_=0)).label('total_spent'),
            func.count(case((Transaction.amount < 0, 1), else_=None)).label('transaction_count')
        ).join(
            Transaction, Category.id == Transaction.category_id, isouter=True
        ).filter(
            and_(
                category_filter,
                or_(
                    Transaction.date >= date_range.start_date,
                    Transaction.date <= date_range.end_date,
                    Transaction.date.is_(None)
                )
            )
        ).group_by(
            Category.id, Category.name, Category.level
        ).order_by(
            desc('total_spent')
        ).all()
        
        # Calculate total spending for percentage calculation
        total_spending = sum(cat.total_spent or 0 for cat in categories)
        
        # Build category breakdown
        category_breakdown = []
        for cat in categories:
            spent = cat.total_spent or 0
            percentage = (spent / total_spending * 100) if total_spending > 0 else 0
            
            category_breakdown.append({
                "category_id": cat.id,
                "category_name": cat.name,
                "level": cat.level,
                "total_spent": spent,
                "transaction_count": cat.transaction_count or 0,
                "percentage": percentage
            })
        
        return CategoryBreakdownResponse(
            period_start=date_range.start_date,
            period_end=date_range.end_date,
            category_level=category_level,
            total_spending=total_spending,
            categories=category_breakdown
        )
    
    def get_spending_trends(self, metric: str, periods: int, period_type: str, db: Session) -> TrendAnalysisResponse:
        """
        Analyze spending trends over time.
        
        Args:
            metric: Metric to analyze (spending, income, net_flow)
            periods: Number of periods to analyze
            period_type: Type of period for analysis
            db: Database session
            
        Returns:
            Trend analysis with period data and insights
        """
        # Calculate date range
        end_date = date.today()
        if period_type == "day":
            start_date = end_date - timedelta(days=periods-1)
            date_format = "%Y-%m-%d"
        elif period_type == "week":
            start_date = end_date - timedelta(weeks=periods-1)
            date_format = "%Y-W%U"
        elif period_type == "month":
            start_date = end_date - timedelta(days=periods*30)
            date_format = "%Y-%m"
        else:  # quarter
            start_date = end_date - timedelta(days=periods*90)
            date_format = "%Y-Q%m"
        
        # Build query based on metric
        if metric == "spending":
            amount_filter = Transaction.amount < 0
            value_func = func.abs(func.sum(Transaction.amount))
        elif metric == "income":
            amount_filter = Transaction.amount > 0
            value_func = func.sum(Transaction.amount)
        elif metric == "net_flow":
            amount_filter = None
            value_func = func.sum(Transaction.amount)
        else:  # category_spending
            amount_filter = Transaction.amount < 0
            value_func = func.abs(func.sum(Transaction.amount))
        
        # Build base query
        query = db.query(
            func.date_trunc(period_type, Transaction.date).label('period'),
            value_func.label('value'),
            func.count(Transaction.id).label('count')
        ).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        )
        
        if amount_filter:
            query = query.filter(amount_filter)
        
        # Group by period and order
        query = query.group_by('period').order_by('period')
        
        # Execute query
        results = query.all()
        
        # Build trend data
        trend_data = []
        for result in results:
            trend_data.append({
                "period": result.period.strftime(date_format),
                "value": result.value or 0,
                "count": result.count
            })
        
        # Calculate trend statistics
        if len(trend_data) > 1:
            values = [d["value"] for d in trend_data]
            trend_direction = "increasing" if values[-1] > values[0] else "decreasing"
            avg_change = (values[-1] - values[0]) / (len(values) - 1) if len(values) > 1 else 0
        else:
            trend_direction = "stable"
            avg_change = 0
        
        return TrendAnalysisResponse(
            metric=metric,
            period_type=period_type,
            periods_analyzed=periods,
            start_date=start_date,
            end_date=end_date,
            trend_data=trend_data,
            trend_direction=trend_direction,
            average_change=avg_change,
            total_value=sum(d["value"] for d in trend_data)
        )
    
    def get_monthly_comparison(self, months: int, db: Session) -> MonthlyComparisonResponse:
        """
        Compare monthly spending patterns.
        
        Args:
            months: Number of months to compare
            db: Database session
            
        Returns:
            Monthly comparison with spending patterns and insights
        """
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=months*30)
        
        # Query monthly data
        monthly_data = db.query(
            extract('year', Transaction.date).label('year'),
            extract('month', Transaction.date).label('month'),
            func.sum(case((Transaction.amount < 0, func.abs(Transaction.amount)), else_=0)).label('expenses'),
            func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)).label('income'),
            func.count(Transaction.id).label('transaction_count')
        ).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        ).group_by(
            extract('year', Transaction.date),
            extract('month', Transaction.date)
        ).order_by(
            extract('year', Transaction.date),
            extract('month', Transaction.date)
        ).all()
        
        # Build monthly comparison data
        comparison_data = []
        for month_data in monthly_data:
            net_flow = month_data.income - month_data.expenses
            comparison_data.append({
                "year": month_data.year,
                "month": month_data.month,
                "month_name": datetime(month_data.year, month_data.month, 1).strftime("%B"),
                "income": month_data.income or 0,
                "expenses": month_data.expenses or 0,
                "net_flow": net_flow,
                "transaction_count": month_data.transaction_count or 0
            })
        
        # Calculate comparison statistics
        if len(comparison_data) > 1:
            avg_monthly_expenses = sum(d["expenses"] for d in comparison_data) / len(comparison_data)
            avg_monthly_income = sum(d["income"] for d in comparison_data) / len(comparison_data)
            best_month = max(comparison_data, key=lambda x: x["net_flow"])
            worst_month = min(comparison_data, key=lambda x: x["net_flow"])
        else:
            avg_monthly_expenses = 0
            avg_monthly_income = 0
            best_month = comparison_data[0] if comparison_data else None
            worst_month = comparison_data[0] if comparison_data else None
        
        return MonthlyComparisonResponse(
            months_analyzed=months,
            start_date=start_date,
            end_date=end_date,
            monthly_data=comparison_data,
            average_monthly_expenses=avg_monthly_expenses,
            average_monthly_income=avg_monthly_income,
            best_month=best_month,
            worst_month=worst_month,
            total_income=sum(d["income"] for d in comparison_data),
            total_expenses=sum(d["expenses"] for d in comparison_data)
        )
    
    def get_cash_flow_analysis(self, date_range: DateRange, include_forecast: bool, db: Session) -> CashFlowAnalysisResponse:
        """
        Analyze cash flow patterns and trends.
        
        Args:
            date_range: Date range for analysis
            include_forecast: Whether to include cash flow forecasting
            db: Database session
            
        Returns:
            Cash flow analysis with patterns and insights
        """
        # Query daily cash flow
        daily_cash_flow = db.query(
            Transaction.date,
            func.sum(Transaction.amount).label('daily_flow'),
            func.count(Transaction.id).label('transaction_count')
        ).filter(
            and_(
                Transaction.date >= date_range.start_date,
                Transaction.date <= date_range.end_date
            )
        ).group_by(
            Transaction.date
        ).order_by(
            Transaction.date
        ).all()
        
        # Build cash flow data
        cash_flow_data = []
        running_balance = 0
        
        for day_data in daily_cash_flow:
            running_balance += day_data.daily_flow
            cash_flow_data.append({
                "date": day_data.date,
                "daily_flow": day_data.daily_flow or 0,
                "running_balance": running_balance,
                "transaction_count": day_data.transaction_count or 0
            })
        
        # Calculate cash flow statistics
        if cash_flow_data:
            positive_days = len([d for d in cash_flow_data if d["daily_flow"] > 0])
            negative_days = len([d for d in cash_flow_data if d["daily_flow"] < 0])
            avg_daily_flow = sum(d["daily_flow"] for d in cash_flow_data) / len(cash_flow_data)
            max_balance = max(d["running_balance"] for d in cash_flow_data)
            min_balance = min(d["running_balance"] for d in cash_flow_data)
        else:
            positive_days = 0
            negative_days = 0
            avg_daily_flow = 0
            max_balance = 0
            min_balance = 0
        
        # Generate forecast if requested
        forecast_data = None
        if include_forecast and cash_flow_data:
            # Simple linear regression forecast for next 30 days
            forecast_data = self._generate_cash_flow_forecast(cash_flow_data, 30)
        
        return CashFlowAnalysisResponse(
            period_start=date_range.start_date,
            period_end=date_range.end_date,
            cash_flow_data=cash_flow_data,
            positive_days=positive_days,
            negative_days=negative_days,
            average_daily_flow=avg_daily_flow,
            max_balance=max_balance,
            min_balance=min_balance,
            forecast_data=forecast_data
        )
    
    def get_budget_analysis(self, date_range: DateRange, include_alerts: bool, db: Session) -> BudgetAnalysisResponse:
        """
        Analyze budget performance and compliance.
        
        Args:
            date_range: Date range for analysis
            include_alerts: Whether to include budget alerts
            db: Database session
            
        Returns:
            Budget analysis with performance metrics and alerts
        """
        # Query active budgets
        active_budgets = db.query(Budget).filter(
            and_(
                Budget.is_active == True,
                or_(
                    and_(Budget.start_date <= date_range.end_date, Budget.end_date >= date_range.start_date)
                )
            )
        ).all()
        
        # Analyze each budget
        budget_performance = []
        total_budgeted = 0
        total_spent = 0
        over_budget_count = 0
        
        for budget in active_budgets:
            # Calculate budget performance for the period
            budget_start = max(budget.start_date, date_range.start_date)
            budget_end = min(budget.end_date, date_range.end_date)
            
            # Query spending for budget period
            spent_query = db.query(func.sum(Transaction.amount)).filter(
                and_(
                    Transaction.category_id == budget.category_id,
                    Transaction.date >= budget_start,
                    Transaction.date <= budget_end,
                    Transaction.amount < 0
                )
            )
            
            spent_amount = abs(spent_query.scalar() or 0)
            
            # Calculate performance metrics
            budget_amount = budget.amount
            if budget.period_type == "monthly":
                # Adjust for partial months
                days_in_budget = (budget.end_date - budget.start_date).days + 1
                days_in_period = (budget_end - budget_start).days + 1
                budget_amount = budget.amount * (days_in_period / days_in_budget)
            
            performance_percentage = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
            is_over_budget = spent_amount > budget_amount
            
            if is_over_budget:
                over_budget_count += 1
            
            total_budgeted += budget_amount
            total_spent += spent_amount
            
            budget_performance.append({
                "budget_id": budget.id,
                "budget_name": budget.name,
                "category_id": budget.category_id,
                "budgeted_amount": budget_amount,
                "spent_amount": spent_amount,
                "remaining_amount": budget_amount - spent_amount,
                "performance_percentage": performance_percentage,
                "is_over_budget": is_over_budget,
                "alert_level": "critical" if performance_percentage >= 100 else "warning" if performance_percentage >= budget.alert_threshold else "healthy"
            })
        
        # Calculate overall metrics
        overall_performance = (total_spent / total_budgeted * 100) if total_budgeted > 0 else 0
        
        # Generate alerts if requested
        alerts = []
        if include_alerts:
            for perf in budget_performance:
                if perf["alert_level"] == "critical":
                    alerts.append({
                        "type": "over_budget",
                        "budget_id": perf["budget_id"],
                        "message": f"Budget '{perf['budget_name']}' exceeded by {perf['spent_amount'] - perf['budgeted_amount']}",
                        "severity": "critical"
                    })
                elif perf["alert_level"] == "warning":
                    alerts.append({
                        "type": "threshold_warning",
                        "budget_id": perf["budget_id"],
                        "message": f"Budget '{perf['budget_name']}' is {perf['performance_percentage']:.1f}% used",
                        "severity": "warning"
                    })
        
        return BudgetAnalysisResponse(
            period_start=date_range.start_date,
            period_end=date_range.end_date,
            total_budgets=len(active_budgets),
            total_budgeted_amount=total_budgeted,
            total_spent_amount=total_spent,
            overall_performance_percentage=overall_performance,
            over_budget_count=over_budget_count,
            budget_performance=budget_performance,
            alerts=alerts
        )
    
    def get_spending_patterns(self, date_range: DateRange, pattern_type: str, db: Session) -> SpendingPatternResponse:
        """
        Analyze spending patterns and identify trends.
        
        Args:
            date_range: Date range for analysis
            pattern_type: Type of pattern to analyze
            db: Database session
            
        Returns:
            Spending patterns with insights and recommendations
        """
        # Query transactions for pattern analysis
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.date >= date_range.start_date,
                Transaction.date <= date_range.end_date,
                Transaction.amount < 0  # Only expenses
            )
        ).all()
        
        if pattern_type == "daily":
            patterns = self._analyze_daily_patterns(transactions)
        elif pattern_type == "weekly":
            patterns = self._analyze_weekly_patterns(transactions)
        elif pattern_type == "monthly":
            patterns = self._analyze_monthly_patterns(transactions)
        else:  # seasonal
            patterns = self._analyze_seasonal_patterns(transactions)
        
        # Generate insights and recommendations
        insights = self._generate_spending_insights(patterns, pattern_type)
        
        return SpendingPatternResponse(
            period_start=date_range.start_date,
            period_end=date_range.end_date,
            pattern_type=pattern_type,
            patterns=patterns,
            insights=insights
        )
    
    def get_financial_health(self, db: Session) -> FinancialHealthResponse:
        """
        Assess overall financial health and provide recommendations.
        
        Args:
            db: Database session
            
        Returns:
            Financial health assessment with score and recommendations
        """
        # Calculate financial health metrics
        current_date = date.today()
        last_month_start = current_date.replace(day=1) - timedelta(days=1)
        last_month_start = last_month_start.replace(day=1)
        
        # Get last month's data
        last_month_transactions = db.query(Transaction).filter(
            and_(
                Transaction.date >= last_month_start,
                Transaction.date <= current_date
            )
        ).all()
        
        # Calculate key metrics
        income = sum(t.amount for t in last_month_transactions if t.amount > 0)
        expenses = abs(sum(t.amount for t in last_month_transactions if t.amount < 0))
        savings = income - expenses
        savings_rate = (savings / income * 100) if income > 0 else 0
        
        # Calculate budget adherence
        active_budgets = db.query(Budget).filter(
            and_(
                Budget.is_active == True,
                Budget.start_date <= current_date,
                Budget.end_date >= current_date
            )
        ).all()
        
        budget_adherence = 0
        if active_budgets:
            total_adherence = 0
            for budget in active_budgets:
                # Get budget progress
                progress_query = db.query(func.sum(Transaction.amount)).filter(
                    and_(
                        Transaction.category_id == budget.category_id,
                        Transaction.date >= budget.start_date,
                        Transaction.date <= current_date,
                        Transaction.amount < 0
                    )
                )
                spent = abs(progress_query.scalar() or 0)
                adherence = max(0, 100 - (spent / budget.amount * 100)) if budget.amount > 0 else 100
                total_adherence += adherence
            
            budget_adherence = total_adherence / len(active_budgets)
        
        # Calculate financial health score (0-100)
        health_score = 0
        
        # Savings rate component (40% weight)
        if savings_rate >= 20:
            health_score += 40
        elif savings_rate >= 10:
            health_score += 30
        elif savings_rate >= 0:
            health_score += 20
        else:
            health_score += 0
        
        # Budget adherence component (30% weight)
        health_score += (budget_adherence / 100) * 30
        
        # Income stability component (20% weight)
        # This would require historical data analysis
        health_score += 15  # Placeholder
        
        # Emergency fund component (10% weight)
        # This would require account balance analysis
        health_score += 5  # Placeholder
        
        # Generate recommendations
        recommendations = []
        if savings_rate < 10:
            recommendations.append("Increase savings rate to at least 10% of income")
        if budget_adherence < 80:
            recommendations.append("Improve budget adherence by reviewing spending patterns")
        if savings < 0:
            recommendations.append("Reduce expenses to achieve positive cash flow")
        
        # Determine health level
        if health_score >= 80:
            health_level = "excellent"
        elif health_score >= 60:
            health_level = "good"
        elif health_score >= 40:
            health_level = "fair"
        else:
            health_level = "poor"
        
        return FinancialHealthResponse(
            health_score=health_score,
            health_level=health_level,
            savings_rate=savings_rate,
            budget_adherence=budget_adherence,
            monthly_income=income,
            monthly_expenses=expenses,
            monthly_savings=savings,
            recommendations=recommendations,
            assessment_date=current_date
        )
    
    def get_category_analysis(self, category_id: UUID, date_range: DateRange, db: Session) -> Optional[Dict[str, Any]]:
        """
        Get detailed analysis for a specific category.
        
        Args:
            category_id: Category unique identifier
            date_range: Date range for analysis
            db: Database session
            
        Returns:
            Category-specific analysis with spending patterns and insights
        """
        # Check if category exists
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None
        
        # Query transactions for the category
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.category_id == category_id,
                Transaction.date >= date_range.start_date,
                Transaction.date <= date_range.end_date
            )
        ).all()
        
        if not transactions:
            return {
                "category_id": category_id,
                "category_name": category.name,
                "total_transactions": 0,
                "total_amount": 0,
                "average_amount": 0,
                "spending_patterns": [],
                "insights": ["No transactions found for this category in the specified period"]
            }
        
        # Calculate basic metrics
        total_amount = sum(t.amount for t in transactions)
        avg_amount = total_amount / len(transactions)
        
        # Analyze spending patterns
        daily_patterns = self._analyze_daily_patterns(transactions)
        
        # Generate insights
        insights = []
        if total_amount < 0:  # Expenses
            insights.append(f"Total spending: {abs(total_amount)}")
            insights.append(f"Average transaction: {abs(avg_amount)}")
        else:  # Income
            insights.append(f"Total income: {total_amount}")
            insights.append(f"Average transaction: {avg_amount}")
        
        return {
            "category_id": category_id,
            "category_name": category.name,
            "total_transactions": len(transactions),
            "total_amount": total_amount,
            "average_amount": avg_amount,
            "spending_patterns": daily_patterns,
            "insights": insights
        }
    
    def export_analytics_report(self, report_type: str, date_range: DateRange, format: str, include_charts: bool, db: Session) -> Dict[str, Any]:
        """
        Export analytics report in various formats.
        
        Args:
            report_type: Type of report to generate
            date_range: Date range for report
            format: Export format
            include_charts: Whether to include chart data
            db: Database session
            
        Returns:
            Export report data
        """
        # Generate report data based on type
        if report_type == "summary":
            report_data = {
                "spending_summary": self.get_spending_summary(date_range, db).dict(),
                "category_breakdown": self.get_category_breakdown(date_range, 2, db).dict(),
                "budget_analysis": self.get_budget_analysis(date_range, True, db).dict()
            }
        elif report_type == "detailed":
            report_data = {
                "spending_summary": self.get_spending_summary(date_range, db).dict(),
                "category_breakdown": self.get_category_breakdown(date_range, 3, db).dict(),
                "trends": self.get_spending_trends("spending", 12, "month", db).dict(),
                "monthly_comparison": self.get_monthly_comparison(6, db).dict(),
                "budget_analysis": self.get_budget_analysis(date_range, True, db).dict(),
                "financial_health": self.get_financial_health(db).dict()
            }
        else:  # custom
            report_data = {
                "spending_summary": self.get_spending_summary(date_range, db).dict(),
                "category_breakdown": self.get_category_breakdown(date_range, 2, db).dict()
            }
        
        # Add chart data if requested
        if include_charts:
            report_data["charts"] = {
                "category_pie": self._generate_category_chart_data(date_range, db),
                "trend_line": self._generate_trend_chart_data(date_range, db)
            }
        
        return {
            "report_type": report_type,
            "format": format,
            "date_range": date_range.dict(),
            "generated_at": datetime.utcnow().isoformat(),
            "data": report_data
        }
    
    def get_insights_and_recommendations(self, date_range: DateRange, insight_type: str, db: Session) -> Dict[str, Any]:
        """
        Get personalized financial insights and recommendations.
        
        Args:
            date_range: Date range for analysis
            insight_type: Type of insights to generate
            db: Database session
            
        Returns:
            Financial insights and actionable recommendations
        """
        insights = []
        recommendations = []
        
        # Get spending summary
        summary = self.get_spending_summary(date_range, db)
        
        # Generate insights based on type
        if insight_type in ["spending", "all"]:
            if summary.savings_rate < 10:
                insights.append("Low savings rate detected")
                recommendations.append("Aim to save at least 10% of your income")
            
            if summary.total_expenses > summary.total_income:
                insights.append("Expenses exceed income")
                recommendations.append("Review and reduce non-essential expenses")
        
        if insight_type in ["saving", "all"]:
            if summary.savings_rate > 20:
                insights.append("Excellent savings rate")
                recommendations.append("Consider investing excess savings")
        
        if insight_type in ["investment", "all"]:
            if summary.savings_rate > 15:
                insights.append("Good savings rate for investment")
                recommendations.append("Consider diversifying investments")
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "metrics": {
                "savings_rate": summary.savings_rate,
                "income_expense_ratio": summary.total_expenses / summary.total_income if summary.total_income > 0 else 0
            }
        }
    
    def get_performance_benchmarks(self, date_range: DateRange, benchmark_type: str, db: Session) -> Dict[str, Any]:
        """
        Compare performance against benchmarks.
        
        Args:
            date_range: Date range for analysis
            benchmark_type: Type of benchmark comparison
            db: Database session
            
        Returns:
            Performance benchmarks and comparison data
        """
        # Get current performance
        summary = self.get_spending_summary(date_range, db)
        
        # Define benchmarks (these would typically come from external data)
        if benchmark_type == "personal":
            # Compare with previous periods
            previous_period_start = date_range.start_date - timedelta(days=(date_range.end_date - date_range.start_date).days)
            previous_period_end = date_range.start_date - timedelta(days=1)
            previous_summary = self.get_spending_summary(DateRange(start_date=previous_period_start, end_date=previous_period_end), db)
            
            benchmarks = {
                "savings_rate": {
                    "current": summary.savings_rate,
                    "previous": previous_summary.savings_rate,
                    "change": summary.savings_rate - previous_summary.savings_rate
                },
                "expense_ratio": {
                    "current": summary.total_expenses / summary.total_income if summary.total_income > 0 else 0,
                    "previous": previous_summary.total_expenses / previous_summary.total_income if previous_summary.total_income > 0 else 0
                }
            }
        else:
            # Placeholder for regional/national benchmarks
            benchmarks = {
                "savings_rate": {
                    "current": summary.savings_rate,
                    "benchmark": 15.0,  # Example benchmark
                    "difference": summary.savings_rate - 15.0
                }
            }
        
        return {
            "benchmark_type": benchmark_type,
            "current_performance": summary.dict(),
            "benchmarks": benchmarks,
            "recommendations": self._generate_benchmark_recommendations(benchmarks)
        }
    
    # Helper methods for pattern analysis
    def _analyze_daily_patterns(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """Analyze daily spending patterns."""
        daily_data = {}
        for transaction in transactions:
            day = transaction.date.strftime("%A")
            if day not in daily_data:
                daily_data[day] = {"count": 0, "total": 0}
            daily_data[day]["count"] += 1
            daily_data[day]["total"] += abs(transaction.amount)
        
        return [
            {
                "day": day,
                "transaction_count": data["count"],
                "total_amount": data["total"],
                "average_amount": data["total"] / data["count"] if data["count"] > 0 else 0
            }
            for day, data in daily_data.items()
        ]
    
    def _analyze_weekly_patterns(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """Analyze weekly spending patterns."""
        weekly_data = {}
        for transaction in transactions:
            week = transaction.date.isocalendar()[1]
            if week not in weekly_data:
                weekly_data[week] = {"count": 0, "total": 0}
            weekly_data[week]["count"] += 1
            weekly_data[week]["total"] += abs(transaction.amount)
        
        return [
            {
                "week": week,
                "transaction_count": data["count"],
                "total_amount": data["total"],
                "average_amount": data["total"] / data["count"] if data["count"] > 0 else 0
            }
            for week, data in weekly_data.items()
        ]
    
    def _analyze_monthly_patterns(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """Analyze monthly spending patterns."""
        monthly_data = {}
        for transaction in transactions:
            month = transaction.date.strftime("%B")
            if month not in monthly_data:
                monthly_data[month] = {"count": 0, "total": 0}
            monthly_data[month]["count"] += 1
            monthly_data[month]["total"] += abs(transaction.amount)
        
        return [
            {
                "month": month,
                "transaction_count": data["count"],
                "total_amount": data["total"],
                "average_amount": data["total"] / data["count"] if data["count"] > 0 else 0
            }
            for month, data in monthly_data.items()
        ]
    
    def _analyze_seasonal_patterns(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """Analyze seasonal spending patterns."""
        seasonal_data = {}
        for transaction in transactions:
            month = transaction.date.month
            if month in [12, 1, 2]:
                season = "Winter"
            elif month in [3, 4, 5]:
                season = "Spring"
            elif month in [6, 7, 8]:
                season = "Summer"
            else:
                season = "Fall"
            
            if season not in seasonal_data:
                seasonal_data[season] = {"count": 0, "total": 0}
            seasonal_data[season]["count"] += 1
            seasonal_data[season]["total"] += abs(transaction.amount)
        
        return [
            {
                "season": season,
                "transaction_count": data["count"],
                "total_amount": data["total"],
                "average_amount": data["total"] / data["count"] if data["count"] > 0 else 0
            }
            for season, data in seasonal_data.items()
        ]
    
    def _generate_spending_insights(self, patterns: List[Dict[str, Any]], pattern_type: str) -> List[str]:
        """Generate insights from spending patterns."""
        insights = []
        
        if not patterns:
            return ["No spending patterns detected"]
        
        # Find highest spending period
        highest_spending = max(patterns, key=lambda x: x["total_amount"])
        insights.append(f"Highest spending in {pattern_type}: {highest_spending[pattern_type.lower()]} (${highest_spending['total_amount']:.2f})")
        
        # Find lowest spending period
        lowest_spending = min(patterns, key=lambda x: x["total_amount"])
        insights.append(f"Lowest spending in {pattern_type}: {lowest_spending[pattern_type.lower()]} (${lowest_spending['total_amount']:.2f})")
        
        # Calculate variance
        amounts = [p["total_amount"] for p in patterns]
        avg_amount = sum(amounts) / len(amounts)
        variance = sum((a - avg_amount) ** 2 for a in amounts) / len(amounts)
        
        if variance > avg_amount * 0.5:
            insights.append("High spending variability detected - consider setting up recurring budgets")
        
        return insights
    
    def _generate_cash_flow_forecast(self, cash_flow_data: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
        """Generate simple cash flow forecast."""
        if len(cash_flow_data) < 2:
            return []
        
        # Simple linear regression
        x_values = list(range(len(cash_flow_data)))
        y_values = [d["daily_flow"] for d in cash_flow_data]
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
        intercept = (sum_y - slope * sum_x) / n
        
        # Generate forecast
        forecast = []
        last_date = cash_flow_data[-1]["date"]
        
        for i in range(1, days + 1):
            forecast_date = last_date + timedelta(days=i)
            forecast_value = slope * (len(cash_flow_data) + i) + intercept
            
            forecast.append({
                "date": forecast_date,
                "forecasted_flow": forecast_value,
                "confidence": max(0.1, 1.0 - (i * 0.05))  # Decreasing confidence over time
            })
        
        return forecast
    
    def _generate_category_chart_data(self, date_range: DateRange, db: Session) -> Dict[str, Any]:
        """Generate data for category pie chart."""
        breakdown = self.get_category_breakdown(date_range, 2, db)
        return {
            "labels": [cat["category_name"] for cat in breakdown.categories],
            "data": [float(cat["total_spent"]) for cat in breakdown.categories],
            "percentages": [float(cat["percentage"]) for cat in breakdown.categories]
        }
    
    def _generate_trend_chart_data(self, date_range: DateRange, db: Session) -> Dict[str, Any]:
        """Generate data for trend line chart."""
        trends = self.get_spending_trends("spending", 12, "month", db)
        return {
            "labels": [period["period"] for period in trends.trend_data],
            "data": [float(period["value"]) for period in trends.trend_data]
        }
    
    def _generate_benchmark_recommendations(self, benchmarks: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on benchmark comparisons."""
        recommendations = []
        
        for metric, data in benchmarks.items():
            if "change" in data:
                if data["change"] < -5:
                    recommendations.append(f"Improve {metric} - current performance declined by {abs(data['change']):.1f}%")
                elif data["change"] > 5:
                    recommendations.append(f"Maintain {metric} - current performance improved by {data['change']:.1f}%")
            
            if "difference" in data:
                if data["difference"] < -5:
                    recommendations.append(f"Work on improving {metric} to meet benchmark")
                elif data["difference"] > 5:
                    recommendations.append(f"Excellent {metric} performance above benchmark")
        
        return recommendations
