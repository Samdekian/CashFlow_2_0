"""
Analytics endpoints for financial insights and reporting.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from uuid import UUID

from ....database import get_db
from ....schemas.common import DateRange, PaginationParams
from ....schemas.analytics import (
    SpendingSummaryResponse,
    CategoryBreakdownResponse,
    TrendAnalysisResponse,
    MonthlyComparisonResponse,
    CashFlowAnalysisResponse,
    BudgetAnalysisResponse,
    SpendingPatternResponse,
    FinancialHealthResponse
)
from ....services.analytics_service import AnalyticsService
from ....core.open_finance_standards import validate_date_range

# Create router
router = APIRouter()

# Initialize service
analytics_service = AnalyticsService()


@router.get("/summary", response_model=SpendingSummaryResponse)
async def get_spending_summary(
    date_range: DateRange = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive spending summary for a date range.
    
    Args:
        date_range: Date range for analysis
        db: Database session
        
    Returns:
        Spending summary with income, expenses, and net cash flow
        
    Raises:
        HTTPException: If date range is invalid
    """
    try:
        if not validate_date_range(date_range):
            raise HTTPException(status_code=400, detail="Invalid date range")
        
        summary = analytics_service.get_spending_summary(date_range, db)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate spending summary: {str(e)}")


@router.get("/categories/breakdown", response_model=CategoryBreakdownResponse)
async def get_category_breakdown(
    date_range: DateRange = Depends(),
    category_level: int = Query(2, ge=1, le=3, description="Category hierarchy level"),
    db: Session = Depends(get_db)
):
    """
    Get spending breakdown by category hierarchy level.
    
    Args:
        date_range: Date range for analysis
        category_level: Category hierarchy level (1-3)
        db: Database session
        
    Returns:
        Category breakdown with spending amounts and percentages
        
    Raises:
        HTTPException: If parameters are invalid
    """
    try:
        if not validate_date_range(date_range):
            raise HTTPException(status_code=400, detail="Invalid date range")
        
        if category_level not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="Category level must be 1, 2, or 3")
        
        breakdown = analytics_service.get_category_breakdown(date_range, category_level, db)
        return breakdown
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate category breakdown: {str(e)}")


@router.get("/trends", response_model=TrendAnalysisResponse)
async def get_spending_trends(
    metric: str = Query(..., description="Metric to analyze (spending, income, net_flow)"),
    periods: int = Query(12, ge=1, le=24, description="Number of periods to analyze"),
    period_type: str = Query("month", description="Period type (day, week, month, quarter)"),
    db: Session = Depends(get_db)
):
    """
    Analyze spending trends over time.
    
    Args:
        metric: Metric to analyze (spending, income, net_flow)
        periods: Number of periods to analyze
        period_type: Type of period for analysis
        db: Database session
        
    Returns:
        Trend analysis with period data and insights
        
    Raises:
        HTTPException: If parameters are invalid
    """
    try:
        if metric not in ["spending", "income", "net_flow", "category_spending"]:
            raise HTTPException(status_code=400, detail="Invalid metric. Must be spending, income, net_flow, or category_spending")
        
        if period_type not in ["day", "week", "month", "quarter"]:
            raise HTTPException(status_code=400, detail="Invalid period type. Must be day, week, month, or quarter")
        
        trends = analytics_service.get_spending_trends(metric, periods, period_type, db)
        return trends
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate trend analysis: {str(e)}")


@router.get("/monthly/comparison", response_model=MonthlyComparisonResponse)
async def get_monthly_comparison(
    months: int = Query(6, ge=2, le=24, description="Number of months to compare"),
    db: Session = Depends(get_db)
):
    """
    Compare monthly spending patterns.
    
    Args:
        months: Number of months to compare
        db: Database session
        
    Returns:
        Monthly comparison with spending patterns and insights
        
    Raises:
        HTTPException: If parameters are invalid
    """
    try:
        if months < 2:
            raise HTTPException(status_code=400, detail="Must compare at least 2 months")
        
        comparison = analytics_service.get_monthly_comparison(months, db)
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate monthly comparison: {str(e)}")


@router.get("/cash-flow", response_model=CashFlowAnalysisResponse)
async def get_cash_flow_analysis(
    date_range: DateRange = Depends(),
    include_forecast: bool = Query(False, description="Include cash flow forecasting"),
    db: Session = Depends(get_db)
):
    """
    Analyze cash flow patterns and trends.
    
    Args:
        date_range: Date range for analysis
        include_forecast: Whether to include cash flow forecasting
        db: Database session
        
    Returns:
        Cash flow analysis with patterns and insights
        
    Raises:
        HTTPException: If date range is invalid
    """
    try:
        if not validate_date_range(date_range):
            raise HTTPException(status_code=400, detail="Invalid date range")
        
        cash_flow = analytics_service.get_cash_flow_analysis(date_range, include_forecast, db)
        return cash_flow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate cash flow analysis: {str(e)}")


@router.get("/budgets/analysis", response_model=BudgetAnalysisResponse)
async def get_budget_analysis(
    date_range: DateRange = Depends(),
    include_alerts: bool = Query(True, description="Include budget alerts and warnings"),
    db: Session = Depends(get_db)
):
    """
    Analyze budget performance and compliance.
    
    Args:
        date_range: Date range for analysis
        include_alerts: Whether to include budget alerts
        db: Database session
        
    Returns:
        Budget analysis with performance metrics and alerts
        
    Raises:
        HTTPException: If date range is invalid
    """
    try:
        if not validate_date_range(date_range):
            raise HTTPException(status_code=400, detail="Invalid date range")
        
        analysis = analytics_service.get_budget_analysis(date_range, include_alerts, db)
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate budget analysis: {str(e)}")


@router.get("/patterns/spending", response_model=SpendingPatternResponse)
async def get_spending_patterns(
    date_range: DateRange = Depends(),
    pattern_type: str = Query("daily", description="Pattern type (daily, weekly, monthly, seasonal)"),
    db: Session = Depends(get_db)
):
    """
    Analyze spending patterns and identify trends.
    
    Args:
        date_range: Date range for analysis
        pattern_type: Type of pattern to analyze
        db: Database session
        
    Returns:
        Spending patterns with insights and recommendations
        
    Raises:
        HTTPException: If parameters are invalid
    """
    try:
        if not validate_date_range(date_range):
            raise HTTPException(status_code=400, detail="Invalid date range")
        
        if pattern_type not in ["daily", "weekly", "monthly", "seasonal"]:
            raise HTTPException(status_code=400, detail="Invalid pattern type. Must be daily, weekly, monthly, or seasonal")
        
        patterns = analytics_service.get_spending_patterns(date_range, pattern_type, db)
        return patterns
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate spending patterns: {str(e)}")


@router.get("/health/financial", response_model=FinancialHealthResponse)
async def get_financial_health(
    db: Session = Depends(get_db)
):
    """
    Assess overall financial health and provide recommendations.
    
    Args:
        db: Database session
        
    Returns:
        Financial health assessment with score and recommendations
    """
    try:
        health = analytics_service.get_financial_health(db)
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assess financial health: {str(e)}")


@router.get("/category/{category_id}/analysis", response_model=dict)
async def get_category_analysis(
    category_id: UUID,
    date_range: DateRange = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get detailed analysis for a specific category.
    
    Args:
        category_id: Category unique identifier
        date_range: Date range for analysis
        db: Database session
        
    Returns:
        Category-specific analysis with spending patterns and insights
        
    Raises:
        HTTPException: If category not found or date range invalid
    """
    try:
        if not validate_date_range(date_range):
            raise HTTPException(status_code=400, detail="Invalid date range")
        
        analysis = analytics_service.get_category_analysis(category_id, date_range, db)
        if not analysis:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate category analysis: {str(e)}")


@router.get("/export/report", response_model=dict)
async def export_analytics_report(
    report_type: str = Query(..., description="Report type (summary, detailed, custom)"),
    date_range: DateRange = Depends(),
    format: str = Query("json", description="Export format (json, csv, pdf)"),
    include_charts: bool = Query(True, description="Include chart data in export"),
    db: Session = Depends(get_db)
):
    """
    Export analytics report in various formats.
    
    Args:
        report_type: Type of report to generate
        date_range: Date range for report
        format: Export format
        include_charts: Whether to include chart data
        db: Database session
        
    Returns:
        Export report data or file download
        
    Raises:
        HTTPException: If parameters are invalid
    """
    try:
        if not validate_date_range(date_range):
            raise HTTPException(status_code=400, detail="Invalid date range")
        
        if report_type not in ["summary", "detailed", "custom"]:
            raise HTTPException(status_code=400, detail="Invalid report type. Must be summary, detailed, or custom")
        
        if format not in ["json", "csv", "pdf"]:
            raise HTTPException(status_code=400, detail="Invalid format. Must be json, csv, or pdf")
        
        report = analytics_service.export_analytics_report(report_type, date_range, format, include_charts, db)
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export analytics report: {str(e)}")


@router.get("/insights/recommendations", response_model=dict)
async def get_insights_and_recommendations(
    date_range: DateRange = Depends(),
    insight_type: str = Query("all", description="Type of insights (spending, saving, investment, all)"),
    db: Session = Depends(get_db)
):
    """
    Get personalized financial insights and recommendations.
    
    Args:
        date_range: Date range for analysis
        insight_type: Type of insights to generate
        db: Database session
        
    Returns:
        Financial insights and actionable recommendations
        
    Raises:
        HTTPException: If parameters are invalid
    """
    try:
        if not validate_date_range(date_range):
            raise HTTPException(status_code=400, detail="Invalid date range")
        
        if insight_type not in ["spending", "saving", "investment", "all"]:
            raise HTTPException(status_code=400, detail="Invalid insight type. Must be spending, saving, investment, or all")
        
        insights = analytics_service.get_insights_and_recommendations(date_range, insight_type, db)
        return insights
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")


@router.get("/performance/benchmarks", response_model=dict)
async def get_performance_benchmarks(
    date_range: DateRange = Depends(),
    benchmark_type: str = Query("personal", description="Benchmark type (personal, regional, national)"),
    db: Session = Depends(get_db)
):
    """
    Compare performance against benchmarks.
    
    Args:
        date_range: Date range for analysis
        benchmark_type: Type of benchmark comparison
        db: Database session
        
    Returns:
        Performance benchmarks and comparison data
        
    Raises:
        HTTPException: If parameters are invalid
    """
    try:
        if not validate_date_range(date_range):
            raise HTTPException(status_code=400, detail="Invalid date range")
        
        if benchmark_type not in ["personal", "regional", "national"]:
            raise HTTPException(status_code=400, detail="Invalid benchmark type. Must be personal, regional, or national")
        
        benchmarks = analytics_service.get_performance_benchmarks(date_range, benchmark_type, db)
        return benchmarks
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate performance benchmarks: {str(e)}")
