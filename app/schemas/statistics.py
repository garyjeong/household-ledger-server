"""
Statistics Schemas (DTO)
Pydantic models for statistics API
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class CategoryStatistics(BaseModel):
    """Category-based statistics"""
    category_id: int
    category_name: str
    total_amount: int
    transaction_count: int
    percentage: float
    color: Optional[str] = None


class MonthlyComparison(BaseModel):
    """Monthly comparison data"""
    period: str
    total_income: int
    total_expense: int
    net_amount: int


class DailyTrend(BaseModel):
    """Daily trend data"""
    date: str
    income: int
    expense: int
    net_amount: int


class SummaryStatistics(BaseModel):
    """Summary statistics"""
    total_income: int
    total_expense: int
    net_amount: int
    transaction_count: int


class StatisticsResponse(BaseModel):
    """Complete statistics response"""
    period: str
    date_range: dict
    summary: SummaryStatistics
    category_breakdown: dict
    monthly_comparison: List[MonthlyComparison]
    daily_trend: List[DailyTrend]
    
    class Config:
        from_attributes = True


class StatisticsQueryParams(BaseModel):
    """Statistics query parameters"""
    period: str = Field(
        default='current-month',
        description="Period: current-month, last-month, last-3-months, last-6-months, year"
    )
    start_date: Optional[date] = Field(None, description="Custom start date")
    end_date: Optional[date] = Field(None, description="Custom end date")
    group_id: Optional[int] = Field(None, description="Group ID filter")

