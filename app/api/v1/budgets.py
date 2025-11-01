"""
Budgets API Router
Budget management endpoints
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status, Path
from typing import Optional
from app.dependencies import get_current_user
from app.domain.models.user import User
from app.domain.models.budget import OwnerType, BudgetStatus
from app.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.services.budget_service import BudgetService
from app.infrastructure.repositories.budget_repository_impl import BudgetRepositoryImpl
from app.infrastructure.repositories.statistics_repository_impl import StatisticsRepositoryImpl
from app.schemas.budget import (
    BudgetCreateRequest,
    BudgetUpdateRequest,
    BudgetResponse,
    BudgetStatusResponse
)

router = APIRouter()


def get_budget_service(db: AsyncSession = Depends(get_session)) -> BudgetService:
    """Dependency injection for BudgetService"""
    budget_repo = BudgetRepositoryImpl(db)
    stats_repo = StatisticsRepositoryImpl(db)
    return BudgetService(budget_repo, stats_repo, db)


@router.get("", response_model=dict)
async def get_budgets(
    owner_type: OwnerType = Query(..., description="Owner type: USER or GROUP"),
    status_filter: Optional[BudgetStatus] = Query(None, alias="status", description="Filter by status"),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    """Get all budgets for the current user or group"""
    try:
        # Determine owner_id based on owner_type
        owner_id = current_user.group_id if owner_type == OwnerType.GROUP and current_user.group_id else current_user.id
        
        budgets = await service.get_budgets(
            owner_type=owner_type,
            owner_id=owner_id,
            status=status_filter
        )
        
        # Serialize budgets
        serialized_budgets = [
            {
                "id": budget.id,
                "owner_type": budget.owner_type.value,
                "owner_id": budget.owner_id,
                "period": budget.period,
                "total_amount": budget.total_amount,
                "status": budget.status.value,
                "created_at": budget.created_at.isoformat(),
                "updated_at": budget.updated_at.isoformat()
            }
            for budget in budgets
        ]
        
        return {
            "success": True,
            "data": serialized_budgets
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예산 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_or_update_budget(
    request: BudgetCreateRequest,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    """Create or update budget for a period"""
    try:
        # Determine owner_id based on owner_type
        owner_id = current_user.group_id if request.owner_type == OwnerType.GROUP and current_user.group_id else current_user.id
        
        budget = await service.create_or_update_budget(
            owner_type=request.owner_type,
            owner_id=owner_id,
            period=request.period,
            total_amount=request.total_amount,
            status=request.status
        )
        
        return {
            "success": True,
            "data": {
                "id": budget.id,
                "owner_type": budget.owner_type.value,
                "owner_id": budget.owner_id,
                "period": budget.period,
                "total_amount": budget.total_amount,
                "status": budget.status.value,
                "created_at": budget.created_at.isoformat(),
                "updated_at": budget.updated_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예산 생성/수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/status", response_model=dict)
async def get_budget_status(
    owner_type: OwnerType = Query(..., description="Owner type: USER or GROUP"),
    period: str = Query(..., pattern=r'^\d{4}-\d{2}$', description="Period in YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    """Get budget status with spending breakdown"""
    try:
        # Determine owner_id based on owner_type
        owner_id = current_user.group_id if owner_type == OwnerType.GROUP and current_user.group_id else current_user.id
        
        budget_status = await service.get_budget_status(
            owner_type=owner_type,
            owner_id=owner_id,
            period=period
        )
        
        return {
            "success": True,
            "data": {
                "period": period,
                "budget_status": budget_status
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예산 현황 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{budget_id}", response_model=dict)
async def get_budget(
    budget_id: int = Path(..., description="Budget ID"),
    owner_type: OwnerType = Query(..., description="Owner type: USER or GROUP"),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    """Get a specific budget by ID"""
    try:
        owner_id = current_user.group_id if owner_type == OwnerType.GROUP and current_user.group_id else current_user.id
        
        budget = await service.get_budget(budget_id, owner_type, owner_id)
        
        return {
            "success": True,
            "data": {
                "id": budget.id,
                "owner_type": budget.owner_type.value,
                "owner_id": budget.owner_id,
                "period": budget.period,
                "total_amount": budget.total_amount,
                "status": budget.status.value,
                "created_at": budget.created_at.isoformat(),
                "updated_at": budget.updated_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예산 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/{budget_id}", response_model=dict)
async def update_budget(
    budget_id: int = Path(..., description="Budget ID"),
    request: BudgetUpdateRequest = ...,
    owner_type: OwnerType = Query(..., description="Owner type: USER or GROUP"),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    """Update a budget"""
    try:
        owner_id = current_user.group_id if owner_type == OwnerType.GROUP and current_user.group_id else current_user.id
        
        budget = await service.get_budget(budget_id, owner_type, owner_id)
        
        # Update fields
        if request.total_amount is not None:
            budget.total_amount = request.total_amount
        if request.status is not None:
            budget.status = request.status
        
        updated_budget = await service.budget_repository.update(budget)
        
        return {
            "success": True,
            "data": {
                "id": updated_budget.id,
                "owner_type": updated_budget.owner_type.value,
                "owner_id": updated_budget.owner_id,
                "period": updated_budget.period,
                "total_amount": updated_budget.total_amount,
                "status": updated_budget.status.value,
                "created_at": updated_budget.created_at.isoformat(),
                "updated_at": updated_budget.updated_at.isoformat()
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예산 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: int = Path(..., description="Budget ID"),
    owner_type: OwnerType = Query(..., description="Owner type: USER or GROUP"),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    """Delete a budget"""
    try:
        owner_id = current_user.group_id if owner_type == OwnerType.GROUP and current_user.group_id else current_user.id
        
        await service.delete_budget(budget_id, owner_type, owner_id)
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in str(e).lower() else status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예산 삭제 중 오류가 발생했습니다: {str(e)}"
        )

