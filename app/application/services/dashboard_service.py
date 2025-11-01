"""
Dashboard Service
Business logic for dashboard use cases (optimized monthly stats)
"""

from typing import Optional
from datetime import date, datetime, timedelta
from app.domain.repositories.statistics_repository import StatisticsRepository


class DashboardService:
    """Dashboard service with dependency injection"""
    
    def __init__(self, statistics_repository: StatisticsRepository):
        self.statistics_repository = statistics_repository
    
    async def get_monthly_stats(
        self,
        user_id: int,
        year: int,
        month: int,
        group_id: Optional[int] = None
    ) -> dict:
        """
        Get optimized monthly statistics for dashboard
        
        Args:
            user_id: User ID
            year: Year (e.g., 2025)
            month: Month (1-12)
            group_id: Optional group ID filter
        
        Returns:
            Dictionary with monthly statistics
        """
        # Calculate month date range
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - datetime.timedelta(days=1)
        
        # Get summary statistics
        summary = await self.statistics_repository.get_summary_statistics(
            user_id=user_id,
            group_id=group_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get category breakdown for expenses
        expense_categories = await self.statistics_repository.get_category_statistics(
            user_id=user_id,
            group_id=group_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type='EXPENSE'
        )
        
        # Get daily trend
        daily_trend = await self.statistics_repository.get_daily_trend(
            user_id=user_id,
            group_id=group_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Additional metrics for dashboard (if needed for group transactions)
        # This can be extended based on requirements
        
        return {
            'year': year,
            'month': month,
            'total_income': summary['total_income'],
            'total_expense': summary['total_expense'],
            'net_amount': summary['net_amount'],
            'transaction_count': summary['transaction_count'],
            'expense_by_category': expense_categories[:5],  # Top 5 categories
            'daily_trend': daily_trend
        }

