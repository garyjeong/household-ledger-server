"""
Balance Schemas (DTO)
Pydantic models for balance API
"""

from pydantic import BaseModel, Field
from typing import Optional


class BalanceResponse(BaseModel):
    """Balance response"""
    balance: dict
    period_data: Optional[dict] = None
    monthly_trend: Optional[list] = None


class BalanceQueryParams(BaseModel):
    """Balance query parameters"""
    group_id: Optional[int] = None
    include_projection: bool = Field(default=False)
    projection_months: int = Field(default=3, ge=1, le=12)
    period: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}$', description="Period in YYYY-MM format")


class MonthlyTrendItem(BaseModel):
    """Monthly trend item"""
    month: str
    balance: int
    income: int
    expense: int


class PeriodData(BaseModel):
    """Period data"""
    period: str
    income: int
    expense: int
    net_amount: int

