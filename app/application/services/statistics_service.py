"""
Statistics Service
Business logic for statistics use cases
"""

from typing import Optional
from datetime import datetime, date, timedelta
from app.domain.repositories.statistics_repository import StatisticsRepository


class StatisticsService:
    """Statistics service with dependency injection"""
    
    def __init__(self, statistics_repository: StatisticsRepository):
        self.statistics_repository = statistics_repository
    
    def calculate_date_range(
        self,
        period: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> tuple[date, date]:
        """
        Calculate date range based on period or custom dates
        
        Args:
            period: One of 'current-month', 'last-month', 'last-3-months', 'last-6-months', 'year'
            start_date: Custom start date (optional)
            end_date: Custom end date (optional)
        
        Returns:
            Tuple of (start_date, end_date)
        """
        today = date.today()
        
        # Custom date range takes precedence
        if start_date and end_date:
            return start_date, end_date
        
        # Calculate based on period
        if period == 'current-month':
            start = date(today.year, today.month, 1)
            if today.month == 12:
                end = date(today.year + 1, 1, 1)
            else:
                end = date(today.year, today.month + 1, 1)
            end = end.replace(day=1) - timedelta(days=1)
            return start, end
        
        elif period == 'last-month':
            if today.month == 1:
                start = date(today.year - 1, 12, 1)
                end = date(today.year, 1, 1) - timedelta(days=1)
            else:
                start = date(today.year, today.month - 1, 1)
                end = date(today.year, today.month, 1) - timedelta(days=1)
            return start, end
        
        elif period == 'last-3-months':
            if today.month <= 3:
                start = date(today.year - 1, today.month + 9, 1)
            else:
                start = date(today.year, today.month - 2, 1)
            if today.month == 12:
                end = date(today.year + 1, 1, 1)
            else:
                end = date(today.year, today.month + 1, 1)
            end = end.replace(day=1) - timedelta(days=1)
            return start, end
        
        elif period == 'last-6-months':
            if today.month <= 6:
                start = date(today.year - 1, today.month + 6, 1)
            else:
                start = date(today.year, today.month - 5, 1)
            if today.month == 12:
                end = date(today.year + 1, 1, 1)
            else:
                end = date(today.year, today.month + 1, 1)
            end = end.replace(day=1) - timedelta(days=1)
            return start, end
        
        elif period == 'year':
            start = date(today.year, 1, 1)
            end = date(today.year, 12, 31)
            return start, end
        
        else:
            # Default: current month
            start = date(today.year, today.month, 1)
            if today.month == 12:
                end = date(today.year + 1, 1, 1)
            else:
                end = date(today.year, today.month + 1, 1)
            end = end.replace(day=1) - timedelta(days=1)
            return start, end
    
    async def get_statistics(
        self,
        user_id: int,
        group_id: Optional[int],
        period: str = 'current-month',
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Get comprehensive statistics
        
        Returns:
            Dictionary with summary, category breakdown, daily trend, and monthly comparison
        """
        # Calculate date range
        start, end = self.calculate_date_range(period, start_date, end_date)
        
        # Get all statistics in parallel
        summary = await self.statistics_repository.get_summary_statistics(
            user_id=user_id,
            group_id=group_id,
            start_date=start,
            end_date=end
        )
        
        income_categories = await self.statistics_repository.get_category_statistics(
            user_id=user_id,
            group_id=group_id,
            start_date=start,
            end_date=end,
            transaction_type='INCOME'
        )
        
        expense_categories = await self.statistics_repository.get_category_statistics(
            user_id=user_id,
            group_id=group_id,
            start_date=start,
            end_date=end,
            transaction_type='EXPENSE'
        )
        
        daily_trend = await self.statistics_repository.get_daily_trend(
            user_id=user_id,
            group_id=group_id,
            start_date=start,
            end_date=end
        )
        
        monthly_comparison = await self.statistics_repository.get_monthly_comparison(
            user_id=user_id,
            group_id=group_id,
            months=6
        )
        
        # Sort categories by amount (descending)
        income_categories.sort(key=lambda x: x['total_amount'], reverse=True)
        expense_categories.sort(key=lambda x: x['total_amount'], reverse=True)
        
        return {
            'period': period,
            'date_range': {
                'start_date': start.isoformat(),
                'end_date': end.isoformat()
            },
            'summary': summary,
            'category_breakdown': {
                'income': income_categories,
                'expense': expense_categories
            },
            'monthly_comparison': monthly_comparison,
            'daily_trend': daily_trend
        }

