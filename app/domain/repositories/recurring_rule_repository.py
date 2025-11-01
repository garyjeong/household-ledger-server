"""
RecurringRule Repository Interface
"""

from typing import Protocol, Optional, List
from datetime import date
from app.domain.models.recurring_rule import RecurringRule


class RecurringRuleRepository(Protocol):
    """RecurringRule repository interface"""
    
    async def find_by_id(self, rule_id: int) -> Optional[RecurringRule]:
        """Find recurring rule by ID"""
        ...
    
    async def find_all(
        self,
        user_id: Optional[int] = None,
        group_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[RecurringRule]:
        """Find all recurring rules with filters"""
        ...
    
    async def create(self, rule: RecurringRule) -> RecurringRule:
        """Create new recurring rule"""
        ...
    
    async def update(self, rule: RecurringRule) -> RecurringRule:
        """Update recurring rule"""
        ...
    
    async def delete(self, rule_id: int) -> None:
        """Delete recurring rule"""
        ...

