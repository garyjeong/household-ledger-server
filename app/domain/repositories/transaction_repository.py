"""
Transaction Repository Interface
"""

from typing import Protocol, Optional, List
from datetime import datetime
from app.domain.models.transaction import Transaction


class TransactionRepository(Protocol):
    """Transaction repository interface"""
    
    async def find_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Find transaction by ID"""
        ...
    
    async def find_all(
        self,
        group_id: Optional[int],
        user_id: Optional[int],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        category_id: Optional[int],
        limit: int,
        offset: int
    ) -> List[Transaction]:
        """Find transactions with filters and pagination"""
        ...
    
    async def count_total(
        self,
        group_id: Optional[int],
        user_id: Optional[int],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        category_id: Optional[int]
    ) -> int:
        """Count total transactions with filters"""
        ...
    
    async def create(self, transaction: Transaction) -> Transaction:
        """Create new transaction"""
        ...
    
    async def update(self, transaction: Transaction) -> Transaction:
        """Update transaction"""
        ...
    
    async def delete(self, transaction_id: int) -> None:
        """Delete transaction"""
        ...

