"""
Statistics Repository Interface
"""

from typing import Protocol, Optional, List
from datetime import datetime, date


class StatisticsRepository(Protocol):
    """Statistics repository interface"""

    async def get_category_statistics(
        self,
        user_id: int,
        group_id: Optional[int],
        start_date: date,
        end_date: date,
        transaction_type: str,
    ) -> List[dict]:
        """Get category-based statistics"""
        ...

    async def get_summary_statistics(
        self, user_id: int, group_id: Optional[int], start_date: date, end_date: date
    ) -> dict:
        """Get summary statistics (total income, expense, count)"""
        ...

    async def get_daily_trend(
        self, user_id: int, group_id: Optional[int], start_date: date, end_date: date
    ) -> List[dict]:
        """Get daily trend data"""
        ...

    async def get_monthly_comparison(
        self, user_id: int, group_id: Optional[int], months: int = 6
    ) -> List[dict]:
        """Get monthly comparison data"""
        ...
