"""
RecurringRule Service
Business logic for recurring rule use cases
"""

from typing import Optional, List
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.domain.repositories.recurring_rule_repository import RecurringRuleRepository
from app.domain.models.recurring_rule import RecurringRule, RecurringFrequency
from app.domain.models.transaction import Transaction, TransactionType
from app.domain.models.category import Category


class RecurringRuleService:
    """RecurringRule service with dependency injection"""
    
    def __init__(self, recurring_rule_repository: RecurringRuleRepository):
        self.recurring_rule_repository = recurring_rule_repository
    
    async def get_recurring_rules(
        self,
        user_id: int,
        group_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[RecurringRule]:
        """Get recurring rules with filters"""
        return await self.recurring_rule_repository.find_all(
            user_id=user_id,
            group_id=group_id,
            is_active=is_active
        )
    
    async def get_recurring_rule(self, rule_id: int, user_id: int) -> RecurringRule:
        """Get recurring rule by ID"""
        rule = await self.recurring_rule_repository.find_by_id(rule_id)
        if not rule:
            raise ValueError("Recurring rule not found")
        
        # Check ownership
        if rule.created_by != user_id:
            raise ValueError("Unauthorized")
        
        return rule
    
    async def create_recurring_rule(
        self,
        rule: RecurringRule
    ) -> RecurringRule:
        """Create new recurring rule"""
        # Validate rule data
        if rule.amount <= 0:
            raise ValueError("Amount must be positive")
        
        if rule.start_date > date.today():
            raise ValueError("Start date cannot be in the future")
        
        return await self.recurring_rule_repository.create(rule)
    
    async def update_recurring_rule(
        self,
        rule_id: int,
        user_id: int,
        updated_data: dict
    ) -> RecurringRule:
        """Update recurring rule"""
        rule = await self.recurring_rule_repository.find_by_id(rule_id)
        if not rule:
            raise ValueError("Recurring rule not found")
        
        # Check ownership
        if rule.created_by != user_id:
            raise ValueError("Unauthorized")
        
        # Update fields
        for key, value in updated_data.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        return await self.recurring_rule_repository.update(rule)
    
    async def delete_recurring_rule(self, rule_id: int, user_id: int) -> None:
        """Delete recurring rule"""
        rule = await self.recurring_rule_repository.find_by_id(rule_id)
        if not rule:
            raise ValueError("Recurring rule not found")
        
        # Check ownership
        if rule.created_by != user_id:
            raise ValueError("Unauthorized")
        
        await self.recurring_rule_repository.delete(rule_id)

