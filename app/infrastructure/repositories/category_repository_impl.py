"""
Category Repository Implementation
ORM-based repository for categories
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.domain.models.category import Category
from app.domain.repositories.category_repository import CategoryRepository


class CategoryRepositoryImpl(CategoryRepository):
    """SQLAlchemy-based category repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_id(self, category_id: int) -> Optional[Category]:
        """Find category by ID"""
        stmt = select(Category).where(Category.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_by_group_and_type(
        self,
        group_id: Optional[int],
        type: str,
        include_default: bool = True
    ) -> list[Category]:
        """Find categories by group and type"""
        stmt = select(Category).where(
            and_(
                Category.type == type,
                (Category.group_id == group_id) | (Category.group_id.is_(None)),
                (Category.is_default == True) if include_default else True
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def create(self, category: Category) -> Category:
        """Create new category with ORM"""
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category
    
    async def update(self, category: Category) -> Category:
        """Update category with ORM"""
        await self.session.merge(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category
    
    async def delete(self, category_id: int) -> None:
        """Delete category with ORM"""
        stmt = select(Category).where(Category.id == category_id)
        result = await self.session.execute(stmt)
        category = result.scalar_one_or_none()
        if category:
            await self.session.delete(category)
            await self.session.commit()
    
    async def count_transactions(self, category_id: int) -> int:
        """Count transactions using this category"""
        from app.domain.models.transaction import Transaction
        stmt = select(func.count(Transaction.id)).where(
            Transaction.category_id == category_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

