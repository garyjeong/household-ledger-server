"""
Balance Service
Business logic for balance use cases
"""

from typing import Optional
from datetime import date, timedelta
from app.domain.repositories.balance_repository import BalanceRepository
from app.domain.models.transaction import TransactionType
from app.domain.models.recurring_rule import RecurringFrequency
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.domain.models.recurring_rule import RecurringRule


class BalanceService:
    """Balance service with dependency injection"""

    def __init__(
        self,
        balance_repository: BalanceRepository,
        session: AsyncSession
    ):
        self.balance_repository = balance_repository
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
        return await self.balance_repository.calculate_balance(
            user_id=user_id,
            group_id=group_id,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id
        )

    async def get_amount_by_type(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        transaction_type: TransactionType = TransactionType.EXPENSE,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> int:
        """Get total amount by transaction type"""
        return await self.balance_repository.get_amount_by_type(
            user_id=user_id,
            group_id=group_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date
        )

    async def get_monthly_trend(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        months: int = 6
    ) -> list[dict]:
        """Get monthly balance trend"""
        return await self.balance_repository.get_monthly_trend(
            user_id=user_id,
            group_id=group_id,
            months=months
        )

    async def calculate_projected_balance(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        months: int = 3
    ) -> int:
        """Calculate projected balance including recurring transactions"""
        # Get current balance
        current_balance = await self.calculate_balance(
            user_id=user_id,
            group_id=group_id
        )

        # Get active recurring rules
        owner_id = group_id if group_id else user_id
        if not owner_id:
            return current_balance

        stmt = select(RecurringRule).where(
            and_(
                RecurringRule.created_by == owner_id if user_id else True,
                RecurringRule.group_id == group_id if group_id else True,
                RecurringRule.is_active == True
            )
        )

        result = await self.session.execute(stmt)
        recurring_rules = result.scalars().all()

        # Calculate projected amount from recurring rules
        projected_amount = 0

        for rule in recurring_rules:
            frequency = 0

            if rule.frequency == RecurringFrequency.MONTHLY:
                frequency = months
            elif rule.frequency == RecurringFrequency.WEEKLY:
                frequency = months * 4  # Approximately 4 weeks per month
            elif rule.frequency == RecurringFrequency.DAILY:
                frequency = months * 30  # Approximately 30 days per month

            # Amount is positive, but EXPENSE should be negative
            rule_amount = int(rule.amount)
            
            # Determine if rule is expense or income based on category
            # For simplicity, assume all recurring rules are expenses unless category says otherwise
            if rule.category and rule.category.type == "INCOME":
                projected_amount += rule_amount * frequency
            else:
                projected_amount -= rule_amount * frequency

        return current_balance + projected_amount

