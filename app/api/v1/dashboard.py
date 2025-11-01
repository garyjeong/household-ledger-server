"""
Dashboard API Router
Dashboard endpoints for monthly stats
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from datetime import datetime
from app.dependencies import get_current_user
from app.domain.models.user import User
from app.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.services.dashboard_service import DashboardService
from app.infrastructure.repositories.statistics_repository_impl import StatisticsRepositoryImpl

router = APIRouter()


def get_dashboard_service(db: AsyncSession = Depends(get_session)) -> DashboardService:
    """Dependency injection for DashboardService"""
    repository = StatisticsRepositoryImpl(db)
    return DashboardService(repository)


@router.get("/monthly-stats", response_model=dict)
async def get_monthly_stats(
    year: int = Query(None, description="Year (e.g., 2025)"),
    month: int = Query(None, description="Month (1-12)"),
    group_id: Optional[int] = Query(None, description="Group ID filter"),
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get optimized monthly statistics for dashboard
    
    Returns:
        - Total income, expense, net amount
        - Transaction count
        - Top 5 expense categories
        - Daily trend
    """
    try:
        # Default to current month if not specified
        today = datetime.now().date()
        target_year = year or today.year
        target_month = month or today.month
        
        # Validate date
        if target_year < 2020 or target_year > 2030 or target_month < 1 or target_month > 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="올바르지 않은 날짜입니다"
            )
        
        stats = await service.get_monthly_stats(
            user_id=current_user.id,
            year=target_year,
            month=target_month,
            group_id=group_id
        )
        
        return {
            "success": True,
            "data": stats
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"월별 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )

