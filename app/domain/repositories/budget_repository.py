"""
Budget Repository Interface
"""

from typing import Protocol, Optional, List
from app.domain.models.budget import Budget, OwnerType, BudgetStatus


class BudgetRepository(Protocol):
    """Budget repository interface"""
    
    async def find_by_id(self, budget_id: int) -> Optional[Budget]:
        """Find budget by ID"""
        ...
    
    async def find_by_owner_and_period(
        self,
        owner_type: OwnerType,
        owner_id: int,
        period: str
    ) -> Optional[Budget]:
        """Find budget by owner and period (YYYY-MM)"""
        ...
    
    async def find_all(
        self,
        owner_type: Optional[OwnerType] = None,
        owner_id: Optional[int] = None,
        status: Optional[BudgetStatus] = None
    ) -> List[Budget]:
        """Find all budgets with filters"""
        ...
    
    async def create(self, budget: Budget) -> Budget:
        """Create new budget"""
        ...
    
    async def update(self, budget: Budget) -> Budget:
        """Update budget"""
        ...
    
    async def delete(self, budget_id: int) -> None:
        """Delete budget"""
        ...

