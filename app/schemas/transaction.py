"""
Transaction Schemas (DTO)
Pydantic models for transaction API
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from app.domain.models.transaction import TransactionType


class TransactionCreateRequest(BaseModel):
    """Create transaction request"""
    group_id: Optional[int] = None
    type: TransactionType
    date: date
    amount: int = Field(gt=0)
    category_id: Optional[int] = None
    tag_id: Optional[int] = None
    merchant: Optional[str] = Field(None, max_length=160)
    memo: Optional[str] = Field(None, max_length=1000)


class TransactionUpdateRequest(BaseModel):
    """Update transaction request"""
    type: Optional[TransactionType] = None
    date: Optional[date] = None
    amount: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = None
    tag_id: Optional[int] = None
    merchant: Optional[str] = None
    memo: Optional[str] = None


class TransactionResponse(BaseModel):
    """Transaction response"""
    id: int
    group_id: Optional[int] = None
    owner_user_id: int
    type: str
    date: date
    amount: int
    category_id: Optional[int] = None
    tag_id: Optional[int] = None
    merchant: Optional[str] = None
    memo: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TransactionFilters(BaseModel):
    """Transaction query filters"""
    group_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category_id: Optional[int] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: list
    total: int
    limit: int
    offset: int

