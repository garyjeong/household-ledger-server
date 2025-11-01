"""
RecurringRule Repository Implementation
ORM-based repository for recurring rules
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from app.domain.models.recurring_rule import RecurringRule
from app.domain.repositories.recurring_rule_repository import RecurringRuleRepository


class RecurringRuleRepositoryImpl(RecurringRuleRepository):
    """SQLAlchemy-based recurring rule repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_id(self, rule_id: int) -> Optional[RecurringRule]:
        """Find recurring rule by ID with eager loading"""
        stmt = select(RecurringRule).where(
            RecurringRule.id == rule_id
        ).options(
            selectinload(RecurringRule.category),
            selectinload(RecurringRule.creator),
            selectinload(RecurringRule.group)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_all(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[RecurringRule]:
        """Find all recurring rules with filters using ORM"""
        stmt = select(RecurringRule)
        
        filters = []
        if user_id is not None:
            filters.append(RecurringRule.created_by == user_id)
        if group_id is not None:
            filters.append(RecurringRule.group_id == group_id)
        if is_active is not None:
            filters.append(RecurringRule.is_active == is_active)
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        # Eager loading for performance
        stmt = stmt.options(
            selectinload(RecurringRule.category),
            selectinload(RecurringRule.creator),
            selectinload(RecurringRule.group)
        )
        
        # Order by active status and creation date
        stmt = stmt.order_by(
            RecurringRule.is_active.desc(),
            RecurringRule.created_at.desc()
        )
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, rule: RecurringRule) -> RecurringRule:
        """Create new recurring rule with ORM"""
        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        return rule
    
    async def update(self, rule: RecurringRule) -> RecurringRule:
        """Update recurring rule with ORM"""
        await self.session.merge(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        return rule
    
    async def delete(self, rule_id: int) -> None:
        """Delete recurring rule with ORM"""
        rule = await self.find_by_id(rule_id)
        if rule:
            await self.session.delete(rule)
            await self.session.commit()

