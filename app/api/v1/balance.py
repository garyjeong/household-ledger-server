"""
Balance API Router
Balance management endpoints
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from datetime import date, timedelta
from app.dependencies import get_current_user
from app.domain.models.user import User
from app.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.services.balance_service import BalanceService
from app.infrastructure.repositories.balance_repository_impl import BalanceRepositoryImpl
from app.domain.models.transaction import TransactionType
from app.schemas.balance import BalanceResponse

router = APIRouter()


def get_balance_service(db: AsyncSession = Depends(get_session)) -> BalanceService:
    """Dependency injection for BalanceService"""
    balance_repo = BalanceRepositoryImpl(db)
    return BalanceService(balance_repo, db)


@router.get("", response_model=dict)
async def get_balance(
    group_id: Optional[int] = Query(None, description="Group ID"),
    include_projection: bool = Query(False, description="Include projected balance"),
    projection_months: int = Query(3, ge=1, le=12, description="Number of months for projection"),
    period: Optional[str] = Query(None, pattern=r'^\d{4}-\d{2}$', description="Period in YYYY-MM format"),
    current_user: User = Depends(get_current_user),
    service: BalanceService = Depends(get_balance_service)
):
    """
    Get current balance and optionally projected balance
    
    - Current balance: Sum of all transactions
    - Period data: Income/expense for a specific period
    - Monthly trend: Balance trend over time
    - Projected balance: Future balance including recurring transactions
    """
    try:
        # Calculate current balance
        current_balance = await service.calculate_balance(
            user_id=current_user.id,
            group_id=group_id or current_user.group_id
        )

        # Period data
        period_data = None
        if period:
            try:
                year, month = map(int, period.split('-'))
                start_date = date(year, month, 1)
                if month == 12:
                    end_date = date(year + 1, 1, 1) - timedelta(days=1)
                else:
                    end_date = date(year, month + 1, 1) - timedelta(days=1)

                income = await service.get_amount_by_type(
                    user_id=current_user.id,
                    group_id=group_id or current_user.group_id,
                    transaction_type=TransactionType.INCOME,
                    start_date=start_date,
                    end_date=end_date
                )

                expense = await service.get_amount_by_type(
                    user_id=current_user.id,
                    group_id=group_id or current_user.group_id,
                    transaction_type=TransactionType.EXPENSE,
                    start_date=start_date,
                    end_date=end_date
                )

                period_data = {
                    "period": period,
                    "income": income,
                    "expense": expense,
                    "net_amount": income - expense
                }
            except (ValueError, AttributeError) as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid period format: {str(e)}"
                )

        # Projected balance
        projected_balance = None
        monthly_trend = None

        if include_projection:
            projected_balance = await service.calculate_projected_balance(
                user_id=current_user.id,
                group_id=group_id or current_user.group_id,
                months=projection_months
            )

            monthly_trend = await service.get_monthly_trend(
                user_id=current_user.id,
                group_id=group_id or current_user.group_id,
                months=min(projection_months, 6)
            )

        # Build response
        response_data = {
            "balance": {
                "current": current_balance,
                "projected": projected_balance,
                "currency": "KRW"
            }
        }

        if period_data:
            response_data["period_data"] = period_data

        if monthly_trend:
            response_data["monthly_trend"] = monthly_trend

        return {
            "success": True,
            "data": response_data,
            "dev_info": {
                "include_projection": include_projection,
                "projection_months": projection_months,
                "last_calculated": date.today().isoformat()
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
            detail=f"잔액 계산 중 오류가 발생했습니다: {str(e)}"
        )

