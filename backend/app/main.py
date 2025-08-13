"""
Main FastAPI application for the CashFlow Monitor.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from .config import settings
from .database import init_db, close_db
from .api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting CashFlow Monitor Application...")
    print(f"📊 Open Finance Brasil Compliance: {settings.default_country} - {settings.default_currency}")
    
    # Initialize database
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🛑 Shutting down CashFlow Monitor Application...")
    close_db()
    print("✅ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Personal CashFlow Monitoring Application with Open Finance Brasil Integration",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint with application information."""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "open_finance_compliance": {
            "country": settings.default_country,
            "currency": settings.default_currency,
            "standard": "Open Finance Brasil v1.0"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-12-01T00:00:00Z",
        "version": settings.app_version
    }


@app.get("/open-finance-compliance")
async def open_finance_compliance():
    """Open Finance Brasil compliance information."""
    from .core.open_finance_standards import get_open_finance_compliance_info
    
    return {
        "compliance_info": get_open_finance_compliance_info(),
        "application_settings": {
            "default_currency": settings.default_currency,
            "default_country": settings.default_country,
            "supported_file_types": settings.allowed_file_types
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": "2024-12-01T00:00:00Z"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "code": 500,
                "message": "An internal server error occurred",
                "timestamp": "2024-12-01T00:00:00Z"
            }
        }
    )


def main():
    """Main function to run the application."""
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )


if __name__ == "__main__":
    main()
