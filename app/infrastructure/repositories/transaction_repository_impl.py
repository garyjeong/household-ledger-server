"""
Transaction Repository Implementation
ORM-based repository for transactions
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.domain.models.transaction import Transaction
from app.domain.repositories.transaction_repository import TransactionRepository


class TransactionRepositoryImpl(TransactionRepository):
    """SQLAlchemy-based transaction repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Find transaction by ID with eager loading"""
        stmt = select(Transaction).where(Transaction.id == transaction_id).options(
            selectinload(Transaction.category),
            selectinload(Transaction.tag),
            selectinload(Transaction.owner),
            selectinload(Transaction.group),
            selectinload(Transaction.attachments)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_all(
        self,
        group_id: Optional[int],
        user_id: int: Optional[None],
        start_date: datetime: Optional[None],
        end_date: datetime: Optional[None],
        category_id: Optional[int],
        limit: int,
        offset: int
    ) -> list[Transaction]:
        """Find transactions with filters and pagination using ORM"""
        stmt = select(Transaction)
        
        # Build dynamic filters
        filters = []
        if group_id is not None:
            filters.append(Transaction.group_id == group_id)
        if user_id is not None:
            filters.append(Transaction.owner_user_id == user_id)
        if start_date is not None:
            filters.append(Transaction.date >= start_date)
        if end_date is not None:
            filters.append(Transaction.date <= end_date)
        if category_id is not None:
            filters.append(Transaction.category_id == category_id)
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        # Eager loading for performance
        stmt = stmt.options(
            selectinload(Transaction.category),
            selectinload(Transaction.tag),
            selectinload(Transaction.owner)
        )
        
        # Order and paginate
        stmt = stmt.order_by(Transaction.date.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def count_total(
        self,
        group_id: Optional[int],
        user_id: int: Optional[None],
        start_date: datetime: Optional[None],
        end_date: datetime: Optional[None],
        category_id: Optional[int]
    ) -> int:
        """Count total transactions with filters"""
        stmt = select(func.count(Transaction.id))
        
        filters = []
        if group_id is not None:
            filters.append(Transaction.group_id == group_id)
        if user_id is not None:
            filters.append(Transaction.owner_user_id == user_id)
        if start_date is not None:
            filters.append(Transaction.date >= start_date)
        if end_date is not None:
            filters.append(Transaction.date <= end_date)
        if category_id is not None:
            filters.append(Transaction.category_id == category_id)
        
        if filters:
            stmt = stmt.where(and_(*filters))
        
        result = await self.session.execute(stmt)
        return result.scalar_one()
    
    async def create(self, transaction: Transaction) -> Transaction:
        """Create new transaction with ORM"""
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction
    
    async def update(self, transaction: Transaction) -> Transaction:
        """Update transaction with ORM"""
        await self.session.merge(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction
    
    async def delete(self, transaction_id: int) -> None:
        """Delete transaction with ORM"""
        transaction = await self.find_by_id(transaction_id)
        if transaction:
            await self.session.delete(transaction)
            await self.session.commit()

