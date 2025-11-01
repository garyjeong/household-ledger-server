"""
RecurringRule Schemas (DTO)
Pydantic models for recurring rule API
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from app.domain.models.recurring_rule import RecurringFrequency


class RecurringRuleCreateRequest(BaseModel):
    """Create recurring rule request"""

    start_date: date
    frequency: RecurringFrequency
    day_rule: str = Field(
        ...,
        max_length=20,
        description="Day rule (e.g., '1' for 1st of month, 'MON' for Monday)",
    )
    amount: int = Field(..., gt=0, description="Amount in cents")
    category_id: Optional[int] = None
    merchant: Optional[str] = Field(None, max_length=160)
    memo: Optional[str] = Field(None, max_length=1000)


class RecurringRuleUpdateRequest(BaseModel):
    """Update recurring rule request"""

    frequency: Optional[RecurringFrequency] = None
    day_rule: Optional[str] = Field(None, max_length=20)
    amount: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = None
    merchant: Optional[str] = None
    memo: Optional[str] = None
    is_active: Optional[bool] = None


class ProcessRecurringRulesRequest(BaseModel):
    """Process recurring rules request"""

    target_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    rule_id: Optional[int] = None


class GenerateTransactionRequest(BaseModel):
    """Generate transaction from rule request"""

    transaction_date: date = Field(
        ..., description="Target date for transaction", alias="date"
    )

    class Config:
        populate_by_name = True


class CategoryInfo(BaseModel):
    """Category information"""

    id: int
    name: str
    type: str
    color: Optional[str] = None


class GroupInfo(BaseModel):
    """Group information"""

    id: int
    name: str


class RecurringRuleResponse(BaseModel):
    """Recurring rule response"""

    id: int
    group_id: Optional[int] = None
    created_by: int
    start_date: date
    frequency: str
    day_rule: str
    amount: int
    category_id: Optional[int] = None
    merchant: Optional[str] = None
    memo: Optional[str] = None
    is_active: bool
    category: Optional[CategoryInfo] = None
    group: Optional[GroupInfo] = None

    class Config:
        from_attributes = True
