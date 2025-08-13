"""
Main API router for v1 endpoints.
"""
from fastapi import APIRouter

from .endpoints import transactions, categories, budgets, analytics, import_export

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
