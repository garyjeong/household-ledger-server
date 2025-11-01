"""
Recurring Scheduler Service
Business logic for processing recurring rules and generating transactions
"""

from typing import Optional
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.domain.models.recurring_rule import RecurringRule, RecurringFrequency
from app.domain.models.transaction import Transaction, TransactionType


class RecurringSchedulerService:
    """Service for processing recurring rules and generating transactions"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def should_create_transaction(
        self,
        day_rule: str,
        frequency: RecurringFrequency,
        target_date: date,
        start_date: date
    ) -> bool:
        """
        Check if transaction should be created for the given date
        
        Args:
            day_rule: Day rule string (e.g., "1", "매월 말일", "월요일")
            frequency: Recurring frequency (DAILY, WEEKLY, MONTHLY)
            target_date: Target date to check
            start_date: Rule start date
        
        Returns:
            True if transaction should be created
        """
        # Start date check
        if target_date < start_date:
            return False
        
        day = target_date.day
        day_of_week = target_date.weekday()  # 0: Monday, 6: Sunday
        is_weekend = day_of_week >= 5  # Saturday (5) or Sunday (6)
        is_weekday = not is_weekend
        
        if frequency == RecurringFrequency.DAILY:
            if day_rule == "매일":
                return True
            if day_rule == "평일만" and is_weekday:
                return True
            if day_rule == "주말만" and is_weekend:
                return True
            return False
        
        elif frequency == RecurringFrequency.WEEKLY:
            week_days = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
            day_name = week_days[day_of_week]
            return day_name in day_rule
        
        elif frequency == RecurringFrequency.MONTHLY:
            if day_rule == "매월 말일":
                # Check if it's the last day of the month
                next_month = target_date.replace(day=28) + timedelta(days=4)
                last_day = (next_month - timedelta(days=next_month.day)).day
                return day == last_day
            
            # "매월 5일" 형태 파싱
            if day_rule.startswith("매월"):
                try:
                    target_day = int(day_rule.replace("매월", "").replace("일", "").strip())
                    return day == target_day
                except ValueError:
                    pass
            
            return False
        
        return False
    
    async def process_recurring_rules(
        self,
        target_date: Optional[date] = None,
        rule_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> dict:
        """
        Process recurring rules for a specific date and generate transactions
        
        Args:
            target_date: Target date (default: today)
            rule_id: Specific rule ID (optional)
            user_id: Specific user ID (optional)
        
        Returns:
            Dictionary with created, skipped, and total counts
        """
        if target_date is None:
            target_date = date.today()
        
        # Build query filters
        filters = [
            RecurringRule.is_active == True,
            RecurringRule.start_date <= target_date
        ]
        
        if rule_id:
            filters.append(RecurringRule.id == rule_id)
        if user_id:
            filters.append(RecurringRule.created_by == user_id)
        
        # Get active recurring rules
        stmt = select(RecurringRule).where(and_(*filters)).options(
            selectinload(RecurringRule.category)
        )
        
        result = await self.session.execute(stmt)
        rules = result.scalars().all()
        
        created_count = 0
        skipped_count = 0
        
        for rule in rules:
            try:
                # Check if transaction should be created
                if not self.should_create_transaction(
                    rule.day_rule,
                    rule.frequency,
                    target_date,
                    rule.start_date
                ):
                    continue
                
                # Check for existing transaction
                existing_filters = [
                    Transaction.owner_user_id == rule.created_by,
                    Transaction.date == target_date,
                    Transaction.amount == rule.amount,
                    Transaction.category_id == rule.category_id,
                    Transaction.merchant == rule.merchant,
                ]
                # Add memo filter if exists
                if rule.memo:
                    existing_filters.append(Transaction.memo.like(f"%{rule.memo}%자동 생성%"))
                else:
                    existing_filters.append(Transaction.memo.like("%자동 생성%"))
                
                existing_stmt = select(Transaction).where(and_(*existing_filters))
                existing_result = await self.session.execute(existing_stmt)
                existing = existing_result.scalar_one_or_none()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Determine transaction type from category
                transaction_type = TransactionType.EXPENSE
                if rule.category and rule.category.type == "INCOME":
                    transaction_type = TransactionType.INCOME
                
                # Create transaction
                memo = f"{rule.memo or ''} (자동 생성)".strip()
                
                transaction = Transaction(
                    group_id=rule.group_id,
                    owner_user_id=rule.created_by,
                    type=transaction_type,
                    date=target_date,
                    amount=rule.amount,
                    category_id=rule.category_id,
                    merchant=rule.merchant,
                    memo=memo
                )
                
                self.session.add(transaction)
                created_count += 1
                
            except Exception as e:
                # Log error but continue processing other rules
                print(f"Error processing rule {rule.id}: {e}")
                continue
        
        # Commit all transactions
        await self.session.commit()
        
        return {
            "success": True,
            "created": created_count,
            "skipped": skipped_count,
            "total": len(rules),
            "date": target_date.isoformat()
        }
    
    async def generate_transaction_from_rule(
        self,
        rule_id: int,
        target_date: date,
        user_id: int
    ) -> Transaction:
        """
        Generate a single transaction from a specific recurring rule
        
        Args:
            rule_id: Recurring rule ID
            target_date: Target date for transaction
            user_id: User ID (for authorization)
        
        Returns:
            Created transaction
        """
        # Get rule
        stmt = select(RecurringRule).where(
            and_(
                RecurringRule.id == rule_id,
                RecurringRule.created_by == user_id,
                RecurringRule.is_active == True
            )
        ).options(selectinload(RecurringRule.category))
        
        result = await self.session.execute(stmt)
        rule = result.scalar_one_or_none()
        
        if not rule:
            raise ValueError("Recurring rule not found or inactive")
        
        # Check for existing transaction
        existing_stmt = select(Transaction).where(
            and_(
                Transaction.owner_user_id == user_id,
                Transaction.date == target_date,
                Transaction.amount == rule.amount,
                Transaction.category_id == rule.category_id,
                Transaction.merchant == rule.merchant
            )
        )
        existing_result = await self.session.execute(existing_stmt)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise ValueError("Transaction already exists for this date")
        
        # Determine transaction type
        transaction_type = TransactionType.EXPENSE
        if rule.category and rule.category.type == "INCOME":
            transaction_type = TransactionType.INCOME
        
        # Create transaction
        memo = f"{rule.memo or ''} (자동 생성)".strip()
        
        transaction = Transaction(
            group_id=rule.group_id,
            owner_user_id=rule.created_by,
            type=transaction_type,
            date=target_date,
            amount=rule.amount,
            category_id=rule.category_id,
            merchant=rule.merchant,
            memo=memo
        )
        
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        
        return transaction

