"""
Budget Repository Implementation
ORM-based repository for budgets
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.domain.models.budget import Budget, OwnerType, BudgetStatus
from app.domain.repositories.budget_repository import BudgetRepository


class BudgetRepositoryImpl(BudgetRepository):
    """SQLAlchemy-based budget repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_id(self, budget_id: int) -> Optional[Budget]:
        """Find budget by ID"""
        stmt = select(Budget).where(Budget.id == budget_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_by_owner_and_period(
        self,
        owner_type: OwnerType,
        owner_id: int,
        period: str
    ) -> Optional[Budget]:
        """Find budget by owner and period"""
        stmt = select(Budget).where(
            and_(
                Budget.owner_type == owner_type,
                Budget.owner_id == owner_id,
                Budget.period == period
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_all(
        self,
        owner_type: Optional[OwnerType] = None,
        owner_id: Optional[int] = None,
        status: Optional[BudgetStatus] = None
    ) -> List[Budget]:
        """Find all budgets with filters using ORM"""
        stmt = select(Budget)
        
        filters = []
        if owner_type is not None:
            filters.append(Budget.owner_type == owner_type)
        if owner_id is not None:
            filters.append(Budget.owner_id == owner_id)
        if status is not None:
            filters.append(Budget.status == status)
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        # Order by period (descending)
        stmt = stmt.order_by(Budget.period.desc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, budget: Budget) -> Budget:
        """Create new budget with ORM"""
        self.session.add(budget)
        await self.session.commit()
        await self.session.refresh(budget)
        return budget
    
    async def update(self, budget: Budget) -> Budget:
        """Update budget with ORM"""
        await self.session.merge(budget)
        await self.session.commit()
        await self.session.refresh(budget)
        return budget
    
    async def delete(self, budget_id: int) -> None:
        """Delete budget with ORM"""
        budget = await self.find_by_id(budget_id)
        if budget:
            await self.session.delete(budget)
            await self.session.commit()

