"""
Analytics-related Pydantic schemas for the CashFlow Monitor API.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


class SpendingSummaryResponse(BaseModel):
    """Schema for spending summary response."""
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    total_income: Decimal = Field(..., description="Total income for period")
    total_expenses: Decimal = Field(..., description="Total expenses for period")
    net_cash_flow: Decimal = Field(..., description="Net cash flow (income - expenses)")
    income_count: int = Field(..., description="Number of income transactions")
    expense_count: int = Field(..., description="Number of expense transactions")
    avg_income: Decimal = Field(..., description="Average income per transaction")
    avg_expense: Decimal = Field(..., description="Average expense per transaction")
    daily_avg_income: Decimal = Field(..., description="Daily average income")
    daily_avg_expense: Decimal = Field(..., description="Daily average expense")
    savings_rate: float = Field(..., description="Savings rate as percentage")


class CategoryBreakdownResponse(BaseModel):
    """Schema for category breakdown response."""
    period_start: date = Field(..., description="Period start date")
    period_end: date = Field(..., description="Period end date")
    category_level: int = Field(..., description="Category hierarchy level analyzed")
    total_spending: Decimal = Field(..., description="Total spending across all categories")
    categories: List[Dict[str, Any]] = Field(..., description="Category breakdown data")


class TrendAnalysisResponse(BaseModel):
    """Schema for trend analysis response."""
    metric: str = Field(..., description="Metric analyzed")
    period_type: str = Field(..., description="Period type for analysis")
    periods_analyzed: int = Field(..., description="Number of periods analyzed")
    start_date: date = Field(..., description="Analysis start date")
    end_date: date = Field(..., description="Analysis end date")
    trend_data: List[Dict[str, Any]] = Field(..., description="Period-by-period data")
    trend_direction: str = Field(..., description="Overall trend direction")
    average_change: Decimal = Field(..., description="Average change per period")
    total_value: Decimal = Field(..., description="Total value across all periods")


class MonthlyComparisonResponse(BaseModel):
    """Schema for monthly comparison response."""
    months_analyzed: int = Field(..., description="Number of months analyzed")
    start_date: date = Field(..., description="Analysis start date")
    end_date: date = Field(..., description="Analysis end date")
    monthly_data: List[Dict[str, Any]] = Field(..., description="Monthly data")
    average_monthly_expenses: Decimal = Field(..., description="Average monthly expenses")
    average_monthly_income: Decimal = Field(..., description="Average monthly income")
    best_month: Optional[Dict[str, Any]] = Field(None, description="Best performing month")
    worst_month: Optional[Dict[str, Any]] = Field(None, description="Worst performing month")
    total_income: Decimal = Field(..., description="Total income across all months")
    total_expenses: Decimal = Field(..., description="Total expenses across all months")


class CashFlowAnalysisResponse(BaseModel):
    """Schema for cash flow analysis response."""
    period_start: date = Field(..., description="Analysis period start")
    period_end: date = Field(..., description="Analysis period end")
    cash_flow_data: List[Dict[str, Any]] = Field(..., description="Daily cash flow data")
    positive_days: int = Field(..., description="Number of positive cash flow days")
    negative_days: int = Field(..., description="Number of negative cash flow days")
    average_daily_flow: Decimal = Field(..., description="Average daily cash flow")
    max_balance: Decimal = Field(..., description="Maximum balance reached")
    min_balance: Decimal = Field(..., description="Minimum balance reached")
    forecast_data: Optional[List[Dict[str, Any]]] = Field(None, description="Cash flow forecast")


class BudgetAnalysisResponse(BaseModel):
    """Schema for budget analysis response."""
    period_start: date = Field(..., description="Analysis period start")
    period_end: date = Field(..., description="Analysis period end")
    total_budgets: int = Field(..., description="Total number of budgets")
    active_budgets: int = Field(..., description="Number of active budgets")
    total_budgeted_amount: Decimal = Field(..., description="Total budgeted amount")
    total_spent_amount: Decimal = Field(..., description="Total amount spent")
    overall_performance_percentage: float = Field(..., description="Overall budget performance")
    over_budget_count: int = Field(..., description="Number of budgets over limit")
    budget_performance: List[Dict[str, Any]] = Field(..., description="Individual budget performance")
    alerts: List[Dict[str, Any]] = Field(..., description="Budget alerts and warnings")


class SpendingPatternResponse(BaseModel):
    """Schema for spending pattern response."""
    period_start: date = Field(..., description="Analysis period start")
    period_end: date = Field(..., description="Analysis period end")
    pattern_type: str = Field(..., description="Type of pattern analyzed")
    patterns: List[Dict[str, Any]] = Field(..., description="Pattern data")
    insights: List[str] = Field(..., description="Pattern insights and observations")


class FinancialHealthResponse(BaseModel):
    """Schema for financial health response."""
    health_score: float = Field(..., ge=0, le=100, description="Financial health score (0-100)")
    health_level: str = Field(..., description="Health level (poor, fair, good, excellent)")
    savings_rate: float = Field(..., description="Current savings rate percentage")
    budget_adherence: float = Field(..., description="Budget adherence percentage")
    monthly_income: Decimal = Field(..., description="Monthly income")
    monthly_expenses: Decimal = Field(..., description="Monthly expenses")
    monthly_savings: Decimal = Field(..., description="Monthly savings")
    recommendations: List[str] = Field(..., description="Financial health recommendations")
    assessment_date: date = Field(..., description="Assessment date")


class AnalyticsFilters(BaseModel):
    """Schema for analytics filtering criteria."""
    start_date: Optional[date] = Field(None, description="Analysis start date")
    end_date: Optional[date] = Field(None, description="Analysis end date")
    category_ids: Optional[List[UUID]] = Field(None, description="Filter by category IDs")
    transaction_types: Optional[List[str]] = Field(None, description="Filter by transaction types")
    min_amount: Optional[Decimal] = Field(None, description="Minimum transaction amount")
    max_amount: Optional[Decimal] = Field(None, description="Maximum transaction amount")
    include_inactive: bool = Field(False, description="Include inactive categories/budgets")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate that end date is after start date if both are provided."""
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v


class TrendAnalysisRequest(BaseModel):
    """Schema for trend analysis request."""
    metric: str = Field(..., description="Metric to analyze")
    periods: int = Field(..., ge=1, le=24, description="Number of periods to analyze")
    period_type: str = Field(..., description="Period type (day, week, month, quarter)")
    filters: Optional[AnalyticsFilters] = Field(None, description="Additional filters")
    
    @validator('metric')
    def validate_metric(cls, v):
        """Validate metric type."""
        valid_metrics = ["spending", "income", "net_flow", "category_spending"]
        if v not in valid_metrics:
            raise ValueError(f'Metric must be one of: {", ".join(valid_metrics)}')
        return v
    
    @validator('period_type')
    def validate_period_type(cls, v):
        """Validate period type."""
        valid_periods = ["day", "week", "month", "quarter"]
        if v not in valid_periods:
            raise ValueError(f'Period type must be one of: {", ".join(valid_periods)}')
        return v


class CategoryAnalysisRequest(BaseModel):
    """Schema for category analysis request."""
    category_id: UUID = Field(..., description="Category ID to analyze")
    date_range: Optional[Dict[str, date]] = Field(None, description="Date range for analysis")
    include_subcategories: bool = Field(True, description="Include subcategory analysis")
    include_trends: bool = Field(False, description="Include trend analysis")
    include_comparisons: bool = Field(False, description="Include period comparisons")


class ExportReportRequest(BaseModel):
    """Schema for analytics report export request."""
    report_type: str = Field(..., description="Report type")
    date_range: Dict[str, date] = Field(..., description="Date range for report")
    format: str = Field("json", description="Export format")
    include_charts: bool = Field(True, description="Include chart data")
    filters: Optional[AnalyticsFilters] = Field(None, description="Additional filters")
    
    @validator('report_type')
    def validate_report_type(cls, v):
        """Validate report type."""
        valid_types = ["summary", "detailed", "custom"]
        if v not in valid_types:
            raise ValueError(f'Report type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('format')
    def validate_format(cls, v):
        """Validate export format."""
        valid_formats = ["json", "csv", "pdf"]
        if v not in valid_formats:
            raise ValueError(f'Format must be one of: {", ".join(valid_formats)}')
        return v


class InsightsRequest(BaseModel):
    """Schema for insights and recommendations request."""
    date_range: Dict[str, date] = Field(..., description="Date range for analysis")
    insight_type: str = Field("all", description="Type of insights to generate")
    include_recommendations: bool = Field(True, description="Include actionable recommendations")
    include_benchmarks: bool = Field(False, description="Include benchmark comparisons")
    
    @validator('insight_type')
    def validate_insight_type(cls, v):
        """Validate insight type."""
        valid_types = ["spending", "saving", "investment", "all"]
        if v not in valid_types:
            raise ValueError(f'Insight type must be one of: {", ".join(valid_types)}')
        return v


class BenchmarkRequest(BaseModel):
    """Schema for benchmark analysis request."""
    date_range: Dict[str, date] = Field(..., description="Date range for analysis")
    benchmark_type: str = Field("personal", description="Benchmark type")
    include_regional_data: bool = Field(False, description="Include regional comparisons")
    include_historical_data: bool = Field(True, description="Include historical comparisons")
    
    @validator('benchmark_type')
    def validate_benchmark_type(cls, v):
        """Validate benchmark type."""
        valid_types = ["personal", "regional", "national"]
        if v not in valid_types:
            raise ValueError(f'Benchmark type must be one of: {", ".join(valid_types)}')
        return v


class AnalyticsSummaryResponse(BaseModel):
    """Schema for comprehensive analytics summary response."""
    period_start: date = Field(..., description="Analysis period start")
    period_end: date = Field(..., description="Analysis period end")
    spending_summary: SpendingSummaryResponse = Field(..., description="Spending summary")
    category_breakdown: CategoryBreakdownResponse = Field(..., description="Category breakdown")
    budget_analysis: Optional[BudgetAnalysisResponse] = Field(None, description="Budget analysis")
    financial_health: FinancialHealthResponse = Field(..., description="Financial health assessment")
    key_insights: List[str] = Field(..., description="Key insights and observations")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
    generated_at: datetime = Field(..., description="Report generation timestamp")


class ChartDataResponse(BaseModel):
    """Schema for chart data response."""
    chart_type: str = Field(..., description="Type of chart")
    labels: List[str] = Field(..., description="Chart labels")
    datasets: List[Dict[str, Any]] = Field(..., description="Chart datasets")
    options: Optional[Dict[str, Any]] = Field(None, description="Chart options")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional chart metadata")


class AnalyticsExportResponse(BaseModel):
    """Schema for analytics export response."""
    export_id: str = Field(..., description="Export unique identifier")
    filename: str = Field(..., description="Export filename")
    format: str = Field(..., description="Export format")
    file_size: int = Field(..., description="File size in bytes")
    download_url: str = Field(..., description="Download URL")
    expires_at: datetime = Field(..., description="Download expiration timestamp")
    status: str = Field(..., description="Export status")
    created_at: datetime = Field(..., description="Export creation timestamp")
