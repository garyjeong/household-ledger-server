"""
Statistics API Router
Statistics endpoints
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from datetime import date
from app.dependencies import get_current_user
from app.domain.models.user import User
from app.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.services.statistics_service import StatisticsService
from app.infrastructure.repositories.statistics_repository_impl import StatisticsRepositoryImpl

router = APIRouter()


def get_statistics_service(db: AsyncSession = Depends(get_session)) -> StatisticsService:
    """Dependency injection for StatisticsService"""
    repository = StatisticsRepositoryImpl(db)
    return StatisticsService(repository)


@router.get("", response_model=dict)
async def get_statistics(
    period: str = Query(default='current-month', description="Period: current-month, last-month, last-3-months, last-6-months, year"),
    start_date: Optional[date] = Query(None, description="Custom start date"),
    end_date: Optional[date] = Query(None, description="Custom end date"),
    group_id: Optional[int] = Query(None, description="Group ID filter"),
    current_user: User = Depends(get_current_user),
    service: StatisticsService = Depends(get_statistics_service)
):
    """
    Get comprehensive statistics
    
    Returns:
        - Summary statistics (total income, expense, net amount, count)
        - Category breakdown (income and expense)
        - Daily trend data
        - Monthly comparison (last 6 months)
    """
    try:
        statistics = await service.get_statistics(
            user_id=current_user.id,
            group_id=group_id,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "data": statistics
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        )

