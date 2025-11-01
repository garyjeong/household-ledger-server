"""
Balance Repository Protocol
Interface for balance-related data access
"""

from typing import Protocol, Optional
from datetime import date
from app.domain.models.transaction import TransactionType


class BalanceRepository(Protocol):
    """Balance repository interface"""

    async def calculate_balance(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None
    ) -> int:
        """Calculate current balance from transactions"""
        ...

    async def get_amount_by_type(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        transaction_type: TransactionType = TransactionType.EXPENSE,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> int:
        """Get total amount by transaction type"""
        ...

    async def get_monthly_trend(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        months: int = 6
    ) -> list[dict]:
        """Get monthly balance trend"""
        ...

