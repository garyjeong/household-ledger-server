"""
Statistics Repository Implementation
ORM-based repository for statistics
"""

from typing import Optional, List
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, case, or_
from sqlalchemy.sql import text
from app.domain.models.transaction import Transaction, TransactionType
from app.domain.models.category import Category
from app.domain.repositories.statistics_repository import StatisticsRepository


class StatisticsRepositoryImpl(StatisticsRepository):
    """SQLAlchemy-based statistics repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_category_statistics(
        self,
        user_id: int,
        group_id: Optional[int],
        start_date: date,
        end_date: date,
        transaction_type: str
    ) -> List[dict]:
        """Get category-based statistics using ORM"""
        # Build base query filters
        filters = [
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.type == transaction_type
        ]
        
        # Group filter: include transactions from group or owned by user
        if group_id:
            filters.append(
                or_(
                    Transaction.group_id == group_id,
                    Transaction.owner_user_id == user_id
                )
            )
        else:
            filters.append(Transaction.owner_user_id == user_id)
        
        # Group by category with aggregate functions
        stmt = select(
            Transaction.category_id,
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count')
        ).where(
            and_(*filters),
            Transaction.category_id.isnot(None)
        ).group_by(Transaction.category_id)
        
        result = await self.session.execute(stmt)
        category_stats = result.all()
        
        # Get category details
        category_ids = [stat.category_id for stat in category_stats if stat.category_id]
        if not category_ids:
            return []
        
        categories_stmt = select(Category).where(Category.id.in_(category_ids))
        categories_result = await self.session.execute(categories_stmt)
        categories = {cat.id: cat for cat in categories_result.scalars().all()}
        
        # Format response
        formatted_stats = []
        total_amount = sum(stat.total_amount or 0 for stat in category_stats)
        
        for stat in category_stats:
            category = categories.get(stat.category_id)
            if category:
                amount = stat.total_amount or 0
                formatted_stats.append({
                    'category_id': stat.category_id,
                    'category_name': category.name,
                    'total_amount': int(amount),
                    'transaction_count': stat.transaction_count,
                    'percentage': (amount / total_amount * 100) if total_amount > 0 else 0,
                    'color': category.color
                })
        
        return formatted_stats
    
    async def get_summary_statistics(
        self,
        user_id: int,
        group_id: Optional[int],
        start_date: date,
        end_date: date
    ) -> dict:
        """Get summary statistics using ORM"""
        # Build base query filters
        base_filters = [
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ]
        
        # Group filter
        if group_id:
            base_filters.append(
                or_(
                    Transaction.group_id == group_id,
                    Transaction.owner_user_id == user_id
                )
            )
        else:
            base_filters.append(Transaction.owner_user_id == user_id)
        
        # Get transaction count
        count_stmt = select(func.count(Transaction.id)).where(and_(*base_filters))
        count_result = await self.session.execute(count_stmt)
        transaction_count = count_result.scalar_one() or 0
        
        # Get income sum
        income_filters = base_filters + [Transaction.type == TransactionType.INCOME]
        income_stmt = select(func.sum(Transaction.amount)).where(and_(*income_filters))
        income_result = await self.session.execute(income_stmt)
        total_income = int(income_result.scalar_one() or 0)
        
        # Get expense sum
        expense_filters = base_filters + [Transaction.type == TransactionType.EXPENSE]
        expense_stmt = select(func.sum(Transaction.amount)).where(and_(*expense_filters))
        expense_result = await self.session.execute(expense_stmt)
        total_expense = int(expense_result.scalar_one() or 0)
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'net_amount': total_income - total_expense,
            'transaction_count': transaction_count
        }
    
    async def get_daily_trend(
        self,
        user_id: int,
        group_id: Optional[int],
        start_date: date,
        end_date: date
    ) -> List[dict]:
        """Get daily trend data using raw SQL for better performance"""
        # Raw SQL for daily aggregation - build query conditionally for security
        if group_id:
            sql = text("""
                SELECT 
                    DATE(date) as date,
                    COALESCE(SUM(CASE WHEN type = 'INCOME' THEN amount ELSE 0 END), 0) as income,
                    COALESCE(SUM(CASE WHEN type = 'EXPENSE' THEN amount ELSE 0 END), 0) as expense
                FROM transactions 
                WHERE date >= :start_date
                    AND date <= :end_date
                    AND (group_id = :group_id OR owner_user_id = :user_id)
                GROUP BY DATE(date)
                ORDER BY date ASC
            """).bindparams(
                start_date=start_date,
                end_date=end_date,
                group_id=group_id,
                user_id=user_id
            )
        else:
            sql = text("""
                SELECT 
                    DATE(date) as date,
                    COALESCE(SUM(CASE WHEN type = 'INCOME' THEN amount ELSE 0 END), 0) as income,
                    COALESCE(SUM(CASE WHEN type = 'EXPENSE' THEN amount ELSE 0 END), 0) as expense
                FROM transactions 
                WHERE date >= :start_date
                    AND date <= :end_date
                    AND owner_user_id = :user_id
                GROUP BY DATE(date)
                ORDER BY date ASC
            """).bindparams(
                start_date=start_date,
                end_date=end_date,
                user_id=user_id
            )
        
        result = await self.session.execute(sql)
        rows = result.all()
        
        return [
            {
                'date': str(row.date),
                'income': int(row.income or 0),
                'expense': int(row.expense or 0),
                'net_amount': int((row.income or 0) - (row.expense or 0))
            }
            for row in rows
        ]
    
    async def get_monthly_comparison(
        self,
        user_id: int,
        group_id: Optional[int],
        months: int = 6
    ) -> List[dict]:
        """Get monthly comparison data"""
        from datetime import timedelta
        from calendar import month_name
        
        monthly_data = []
        today = datetime.now().date()
        
        for i in range(months - 1, -1, -1):  # Last 6 months, oldest first
            # Calculate month range
            month_date = today.replace(day=1)
            for _ in range(i):
                # Go back i months
                if month_date.month == 1:
                    month_date = month_date.replace(year=month_date.year - 1, month=12)
                else:
                    month_date = month_date.replace(month=month_date.month - 1)
            
            start_of_month = month_date
            if month_date.month == 12:
                end_of_month = month_date.replace(year=month_date.year + 1, month=1) - timedelta(days=1)
            else:
                end_of_month = month_date.replace(month=month_date.month + 1) - timedelta(days=1)
            
            # Build filters
            filters = [
                Transaction.date >= start_of_month,
                Transaction.date <= end_of_month
            ]
            
            if group_id:
                filters.append(
                    or_(
                        Transaction.group_id == group_id,
                        Transaction.owner_user_id == user_id
                    )
                )
            else:
                filters.append(Transaction.owner_user_id == user_id)
            
            # Get income
            income_filters = filters + [Transaction.type == TransactionType.INCOME]
            income_stmt = select(func.sum(Transaction.amount)).where(and_(*income_filters))
            income_result = await self.session.execute(income_stmt)
            total_income = int(income_result.scalar_one() or 0)
            
            # Get expense
            expense_filters = filters + [Transaction.type == TransactionType.EXPENSE]
            expense_stmt = select(func.sum(Transaction.amount)).where(and_(*expense_filters))
            expense_result = await self.session.execute(expense_stmt)
            total_expense = int(expense_result.scalar_one() or 0)
            
            # Format period string (e.g., "2025년 1월")
            period = f"{start_of_month.year}년 {start_of_month.month}월"
            
            monthly_data.append({
                'period': period,
                'total_income': total_income,
                'total_expense': total_expense,
                'net_amount': total_income - total_expense
            })
        
        return monthly_data

