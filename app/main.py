"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import auth, groups, categories, statistics, dashboard, recurring_rules, budgets, balance
from app.api.v1 import settings as settings_api
from app.api.v1.transactions import router as transactions_router

# Create FastAPI app
app = FastAPI(
    title="Household Ledger API",
    description="신혼부부 가계부 서비스 백엔드 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(groups.router, prefix="/api/v1/groups", tags=["Groups"])
app.include_router(transactions_router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(statistics.router, prefix="/api/v1/statistics", tags=["Statistics"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(recurring_rules.router, prefix="/api/v1/recurring-rules", tags=["RecurringRules"])
app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["Budgets"])
app.include_router(balance.router, prefix="/api/v1/balance", tags=["Balance"])
app.include_router(settings_api.router, prefix="/api/v1/settings", tags=["Settings"])


@app.get("/")
async def root():
    """Health check"""
    return {
        "message": "Household Ledger API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "household-ledger-api",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

