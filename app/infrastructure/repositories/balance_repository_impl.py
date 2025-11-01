"""
Balance Repository Implementation
SQLAlchemy implementation of balance repository
"""

from typing import Optional
from datetime import date, timedelta
from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.domain.repositories.balance_repository import BalanceRepository
from app.domain.models.transaction import Transaction, TransactionType


class BalanceRepositoryImpl:
    """SQLAlchemy implementation of BalanceRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def calculate_balance(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None
    ) -> int:
        """Calculate current balance from transactions"""
        # Build filters
        filters = []
        
        if user_id:
            filters.append(Transaction.owner_user_id == user_id)
        if group_id:
            filters.append(Transaction.group_id == group_id)
        if start_date:
            filters.append(Transaction.date >= start_date)
        if end_date:
            filters.append(Transaction.date <= end_date)
        if category_id:
            filters.append(Transaction.category_id == category_id)

        # Calculate balance: INCOME is positive, EXPENSE is negative
        # Amount is stored as positive, so we need to negate EXPENSE
        stmt = select(
            func.sum(
                case(
                    (Transaction.type == TransactionType.INCOME, Transaction.amount),
                    else_=-Transaction.amount
                )
            )
        ).where(and_(*filters) if filters else True)

        result = await self.session.execute(stmt)
        balance = result.scalar() or 0
        return int(balance)

    async def get_amount_by_type(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        transaction_type: TransactionType = TransactionType.EXPENSE,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> int:
        """Get total amount by transaction type"""
        # Build filters
        filters = [Transaction.type == transaction_type]
        
        if user_id:
            filters.append(Transaction.owner_user_id == user_id)
        if group_id:
            filters.append(Transaction.group_id == group_id)
        if start_date:
            filters.append(Transaction.date >= start_date)
        if end_date:
            filters.append(Transaction.date <= end_date)

        stmt = select(func.sum(Transaction.amount)).where(and_(*filters))
        result = await self.session.execute(stmt)
        total = result.scalar() or 0
        return int(total)

    async def get_monthly_trend(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        months: int = 6
    ) -> list[dict]:
        """Get monthly balance trend"""
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)

        # Build base filters
        filters = []
        if user_id:
            filters.append(Transaction.owner_user_id == user_id)
        if group_id:
            filters.append(Transaction.group_id == group_id)

        # Get all transactions in range
        stmt = select(Transaction).where(
            and_(
                *filters,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ) if filters else and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date
            )
        )
        
        result = await self.session.execute(stmt)
        transactions = result.scalars().all()

        # Group by month
        monthly_data: dict[str, dict] = {}
        
        for transaction in transactions:
            month_key = transaction.date.strftime('%Y-%m')
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'month': month_key,
                    'balance': 0,
                    'income': 0,
                    'expense': 0
                }
            
            amount = int(transaction.amount)
            
            if transaction.type == TransactionType.INCOME:
                monthly_data[month_key]['income'] += amount
                monthly_data[month_key]['balance'] += amount
            else:
                monthly_data[month_key]['expense'] += amount
                monthly_data[month_key]['balance'] -= amount

        # Convert to list and sort by month
        trend_list = sorted(monthly_data.values(), key=lambda x: x['month'])
        
        # Fill missing months with zero
        result_list = []
        current = start_date.replace(day=1)
        
        while current <= end_date:
            month_key = current.strftime('%Y-%m')
            
            if month_key in monthly_data:
                result_list.append(monthly_data[month_key])
            else:
                result_list.append({
                    'month': month_key,
                    'balance': 0,
                    'income': 0,
                    'expense': 0
                })
            
            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        # Return only last N months
        return result_list[-months:] if len(result_list) > months else result_list

