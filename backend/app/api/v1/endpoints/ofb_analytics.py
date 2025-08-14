"""
Open Finance Brasil Advanced Analytics API endpoints
Provides advanced analytics and insights based on aggregated OFB data.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ....services.ofb_advanced_analytics_service import OFBAdvancedAnalyticsService
from ....core.open_finance_brasil import OpenFinanceBrasilIntegration
from ....database import get_db

router = APIRouter()


# Request/Response models
class CashFlowAnalysisRequest(BaseModel):
    user_id: str
    period: str = "monthly"
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class SpendingPatternsRequest(BaseModel):
    user_id: str
    category_level: str = "PRIMARY"
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class BankPerformanceRequest(BaseModel):
    user_id: str
    analysis_period: str = "30_days"


class FinancialHealthRequest(BaseModel):
    user_id: str


@router.post("/cash-flow", response_model=dict)
async def analyze_cash_flow(
    request: CashFlowAnalysisRequest,
    db=Depends(get_db)
):
    """Analyze cash flow patterns across all connected banks."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        result = await analytics_service.get_cash_flow_analysis(
            user_id=request.user_id,
            period=request.period,
            from_date=request.from_date,
            to_date=request.to_date
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Cash flow analysis failed: {str(e)}"
        )


@router.post("/spending-patterns", response_model=dict)
async def analyze_spending_patterns(
    request: SpendingPatternsRequest,
    db=Depends(get_db)
):
    """Analyze spending patterns by category and bank."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        result = await analytics_service.get_spending_patterns(
            user_id=request.user_id,
            category_level=request.category_level,
            from_date=request.from_date,
            to_date=request.to_date
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Spending pattern analysis failed: {str(e)}"
        )


@router.post("/bank-performance", response_model=dict)
async def analyze_bank_performance(
    request: BankPerformanceRequest,
    db=Depends(get_db)
):
    """Analyze performance and efficiency of connected banks."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        result = await analytics_service.get_bank_performance_analysis(
            user_id=request.user_id,
            analysis_period=request.analysis_period
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Bank performance analysis failed: {str(e)}"
        )


@router.post("/financial-health", response_model=dict)
async def calculate_financial_health_score(
    request: FinancialHealthRequest,
    db=Depends(get_db)
):
    """Calculate overall financial health score based on OFB data."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        result = await analytics_service.get_financial_health_score(
            user_id=request.user_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Financial health score calculation failed: {str(e)}"
        )


@router.get("/insights/summary", response_model=dict)
async def get_analytics_insights_summary(
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db)
):
    """Get a summary of key insights from all analytics."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        # Get all analytics data
        cash_flow = await analytics_service.get_cash_flow_analysis(user_id, "monthly")
        spending_patterns = await analytics_service.get_spending_patterns(user_id)
        bank_performance = await analytics_service.get_bank_performance_analysis(user_id)
        financial_health = await analytics_service.get_financial_health_score(user_id)
        
        # Extract key insights
        key_insights = []
        
        # Cash flow insights
        if cash_flow["cash_flow_metrics"]["savings_rate"] < 20:
            key_insights.append({
                "type": "CASH_FLOW",
                "priority": "HIGH",
                "message": "Low savings rate detected",
                "details": f"Current savings rate: {cash_flow['cash_flow_metrics']['savings_rate']:.1f}%"
            })
        
        # Spending pattern insights
        if spending_patterns["top_categories"]:
            top_category = spending_patterns["top_categories"][0]
            if top_category[1] > spending_patterns["total_expenses"] * 0.4:
                key_insights.append({
                    "type": "SPENDING",
                    "priority": "MEDIUM",
                    "message": "High concentration in single category",
                    "details": f"{top_category[0]} represents {top_category[1]/spending_patterns['total_expenses']*100:.1f}% of expenses"
                })
        
        # Bank performance insights
        if bank_performance["overall_performance_score"] < 70:
            key_insights.append({
                "type": "BANK_PERFORMANCE",
                "priority": "MEDIUM",
                "message": "Bank performance needs attention",
                "details": f"Overall performance score: {bank_performance['overall_performance_score']:.1f}"
            })
        
        # Financial health insights
        if financial_health["health_level"] in ["POOR", "CRITICAL"]:
            key_insights.append({
                "type": "FINANCIAL_HEALTH",
                "priority": "HIGH",
                "message": "Financial health requires immediate attention",
                "details": f"Current health level: {financial_health['health_level']}"
            })
        
        # Generate recommendations
        recommendations = []
        for insight in key_insights:
            if insight["type"] == "CASH_FLOW":
                recommendations.append("Focus on increasing income or reducing expenses to improve savings rate")
            elif insight["type"] == "SPENDING":
                recommendations.append("Consider diversifying spending across more categories")
            elif insight["type"] == "BANK_PERFORMANCE":
                recommendations.append("Review bank connections and sync schedules")
            elif insight["type"] == "FINANCIAL_HEALTH":
                recommendations.append("Implement comprehensive financial planning and monitoring")
        
        summary = {
            "user_id": user_id,
            "analysis_date": datetime.utcnow().isoformat(),
            "key_insights": key_insights,
            "recommendations": recommendations,
            "metrics_summary": {
                "savings_rate": cash_flow["cash_flow_metrics"]["savings_rate"],
                "total_expenses": spending_patterns["total_expenses"],
                "bank_performance_score": bank_performance["overall_performance_score"],
                "financial_health_level": financial_health["health_level"]
            },
            "insight_count": len(key_insights),
            "priority_breakdown": {
                "high": len([i for i in key_insights if i["priority"] == "HIGH"]),
                "medium": len([i for i in key_insights if i["priority"] == "MEDIUM"]),
                "low": len([i for i in key_insights if i["priority"] == "LOW"])
            }
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Analytics insights summary failed: {str(e)}"
        )


@router.get("/metrics/overview", response_model=dict)
async def get_analytics_metrics_overview(
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db)
):
    """Get an overview of key analytics metrics."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        # Get key metrics
        cash_flow = await analytics_service.get_cash_flow_analysis(user_id, "monthly")
        financial_health = await analytics_service.get_financial_health_score(user_id)
        
        overview = {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "cash_flow_metrics": {
                "total_income": cash_flow["cash_flow_metrics"]["total_income"],
                "total_expenses": cash_flow["cash_flow_metrics"]["total_expenses"],
                "net_cash_flow": cash_flow["cash_flow_metrics"]["net_cash_flow"],
                "savings_rate": cash_flow["cash_flow_metrics"]["savings_rate"],
                "current_balance": cash_flow["current_balance"]
            },
            "financial_health": {
                "overall_score": financial_health["overall_score"],
                "health_level": financial_health["health_level"],
                "component_scores": financial_health["component_scores"]
            },
            "trends": {
                "income_trend": cash_flow["trends"]["income_trend"],
                "expense_trend": cash_flow["trends"]["expense_trend"]
            },
            "currency": "BRL",
            "period": "monthly"
        }
        
        return overview
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Analytics metrics overview failed: {str(e)}"
        )


@router.get("/export/report", response_model=dict)
async def export_analytics_report(
    user_id: str = Query(..., description="User ID"),
    format: str = Query("json", description="Export format (json, csv, pdf)"),
    include_charts: bool = Query(True, description="Include chart data"),
    db=Depends(get_db)
):
    """Export comprehensive analytics report."""
    try:
        ofb_integration = OpenFinanceBrasilIntegration()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        # Get all analytics data
        cash_flow = await analytics_service.get_cash_flow_analysis(user_id, "monthly")
        spending_patterns = await analytics_service.get_spending_patterns(user_id)
        bank_performance = await analytics_service.get_bank_performance_analysis(user_id)
        financial_health = await analytics_service.get_financial_health_score(user_id)
        
        # Prepare export data
        export_data = {
            "report_metadata": {
                "user_id": user_id,
                "generated_at": datetime.utcnow().isoformat(),
                "format": format,
                "version": "1.0"
            },
            "cash_flow_analysis": cash_flow,
            "spending_patterns": spending_patterns,
            "bank_performance": bank_performance,
            "financial_health": financial_health,
            "summary": {
                "total_income": cash_flow["cash_flow_metrics"]["total_income"],
                "total_expenses": cash_flow["cash_flow_metrics"]["total_expenses"],
                "savings_rate": cash_flow["cash_flow_metrics"]["savings_rate"],
                "financial_health_score": financial_health["overall_score"],
                "bank_performance_score": bank_performance["overall_performance_score"]
            }
        }
        
        if include_charts:
            export_data["chart_data"] = {
                "spending_by_category": spending_patterns["category_breakdown"],
                "cash_flow_trends": cash_flow["trends"]["period_data"],
                "bank_performance_scores": [
                    {
                        "bank": bp["bank_name"],
                        "score": bp["performance_score"]
                    }
                    for bp in bank_performance["bank_performance"]
                ]
            }
        
        return {
            "status": "success",
            "format": format,
            "data": export_data,
            "export_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Analytics report export failed: {str(e)}"
        )
