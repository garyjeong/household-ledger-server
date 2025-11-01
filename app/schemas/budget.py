"""
Budget Schemas (DTO)
Pydantic models for budget API
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from app.domain.models.budget import OwnerType, BudgetStatus


class BudgetCreateRequest(BaseModel):
    """Create budget request"""
    owner_type: OwnerType
    period: str = Field(..., pattern=r'^\d{4}-\d{2}$', description="Period in YYYY-MM format")
    total_amount: int = Field(..., gt=0, description="Total budget amount in cents")
    status: BudgetStatus = Field(default=BudgetStatus.ACTIVE)


class BudgetUpdateRequest(BaseModel):
    """Update budget request"""
    total_amount: Optional[int] = Field(None, gt=0)
    status: Optional[BudgetStatus] = None


class CategoryBudgetBreakdown(BaseModel):
    """Category budget breakdown"""
    category_id: int
    category_name: str
    budget: int
    spent: int
    remaining: int
    usage_percent: float


class BudgetStatusResponse(BaseModel):
    """Budget status response"""
    total_budget: int
    total_spent: int
    remaining_budget: int
    usage_percent: float
    category_breakdown: List[CategoryBudgetBreakdown]


class BudgetResponse(BaseModel):
    """Budget response"""
    id: int
    owner_type: str
    owner_id: int
    period: str
    total_amount: int
    status: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

