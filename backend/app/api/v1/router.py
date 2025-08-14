"""
Main API router for v1 endpoints.
"""
from fastapi import APIRouter

from .endpoints import transactions, categories, budgets, analytics, import_export, open_finance, ofb_accounts, ofb_payments, ofb_multi_bank, ofb_analytics

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["transactions"]
)

api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["categories"]
)

api_router.include_router(
    budgets.router,
    prefix="/budgets",
    tags=["budgets"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

api_router.include_router(
    import_export.router,
    prefix="/import-export",
    tags=["import-export"]
)

api_router.include_router(
    open_finance.router,
    prefix="/open-finance",
    tags=["open-finance"]
)

api_router.include_router(
    ofb_accounts.router,
    prefix="/open-finance",
    tags=["open-finance-accounts"]
)

# Phase 4: Full Integration endpoints
api_router.include_router(
    ofb_payments.router,
    prefix="/open-finance/payments",
    tags=["open-finance-payments"]
)

api_router.include_router(
    ofb_multi_bank.router,
    prefix="/open-finance/multi-bank",
    tags=["open-finance-multi-bank"]
)

api_router.include_router(
    ofb_analytics.router,
    prefix="/open-finance/analytics",
    tags=["open-finance-analytics"]
)
