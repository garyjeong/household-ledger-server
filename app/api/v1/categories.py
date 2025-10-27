"""
Category API Router
Category management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.domain.models.category import Category
from app.dependencies import get_current_user
from app.domain.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.application.services.category_service import CategoryService
from app.infrastructure.repositories.category_repository_impl import CategoryRepositoryImpl
from typing import Optional

router = APIRouter()


@router.get("", response_model=list)
async def get_categories(
    type: str = Query(..., description="Transaction type: EXPENSE, INCOME, TRANSFER"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get categories by type"""
    category_repo = CategoryRepositoryImpl(db)
    category_service = CategoryService(category_repo)
    
    # Get user's group_id
    group_id = current_user.group_id
    
    categories = await category_service.get_categories(
        group_id=group_id,
        type=type
    )
    return categories


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_category(
    name: str,
    type: str,
    color: Optional[str] = None,
    budget_amount: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Create new category"""
    category_repo = CategoryRepositoryImpl(db)
    category_service = CategoryService(category_repo)
    
    category = Category(
        group_id=current_user.group_id,
        created_by=current_user.id,
        name=name,
        type=type,
        color=color,
        budget_amount=budget_amount
    )
    
    try:
        result = await category_service.create_category(category)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{category_id}")
async def update_category(
    category_id: int,
    name: Optional[str] = None,
    color: Optional[str] = None,
    budget_amount: Optional[int] = None,
    db: AsyncSession = Depends(get_session)
):
    """Update category"""
    # TODO: Implement update logic
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_session)
):
    """Delete category"""
    # TODO: Implement delete logic
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)

