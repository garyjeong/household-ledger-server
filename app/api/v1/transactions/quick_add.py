"""
Quick Add Transaction API
Fast transaction creation with category auto-creation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from app.dependencies import get_current_user
from app.domain.models.user import User
from app.domain.models.transaction import Transaction as TransactionModel, TransactionType
from app.domain.models.category import Category
from app.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

router = APIRouter()


class QuickAddTransactionRequest(BaseModel):
    """Quick add transaction request"""
    type: TransactionType = Field(..., description="Transaction type: EXPENSE or INCOME")
    amount: int = Field(..., gt=0, description="Amount in cents")
    category_name: str = Field(..., min_length=1, max_length=50, description="Category name (will be created if not exists)")
    memo: Optional[str] = Field(None, max_length=1000, description="Transaction memo")
    transaction_date: date = Field(..., description="Transaction date", alias="date")
    group_id: Optional[int] = Field(None, description="Group ID")
    
    class Config:
        populate_by_name = True


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def quick_add_transaction(
    request: QuickAddTransactionRequest = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Quick add transaction with automatic category creation
    
    This endpoint allows fast transaction creation without requiring
    a category ID. If the category doesn't exist, it will be created automatically.
    """
    try:
        # Verify group membership if group_id is provided
        group_id = request.group_id or current_user.group_id
        if group_id and current_user.group_id != group_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="그룹에 접근 권한이 없습니다"
            )

        # Find or create category
        category_stmt = select(Category).where(
            Category.name == request.category_name,
            Category.type == request.type.value,
            Category.group_id == group_id
        )
        
        category_result = await db.execute(category_stmt)
        category = category_result.scalar_one_or_none()

        if not category:
            # Create new category with random color
            colors = [
                '#ef4444', '#f97316', '#eab308', '#22c55e',
                '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899'
            ]
            import random
            random_color = random.choice(colors)

            category = Category(
                name=request.category_name,
                type=request.type.value,
                color=random_color,
                group_id=group_id,
                created_by=current_user.id,
                is_default=False
            )
            db.add(category)
            await db.commit()
            await db.refresh(category)

        # Create transaction
        transaction = TransactionModel(
            group_id=group_id,
            owner_user_id=current_user.id,
            type=request.type.value,
            date=request.transaction_date,
            amount=request.amount,
            category_id=category.id,
            merchant=None,
            memo=request.memo
        )

        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)

        # Load category for response
        await db.refresh(category)

        # Format response
        transaction_dict = {
            "id": transaction.id,
            "type": transaction.type,
            "date": transaction.date.isoformat(),
            "amount": str(transaction.amount),
            "category": {
                "id": category.id,
                "name": category.name,
                "color": category.color,
                "type": category.type
            },
            "memo": transaction.memo,
            "created_at": transaction.created_at.isoformat(),
            "updated_at": transaction.updated_at.isoformat()
        }

        return {
            "success": True,
            "transaction": transaction_dict,
            "message": "거래가 성공적으로 추가되었습니다"
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"거래 생성 중 오류가 발생했습니다: {str(e)}"
        )

