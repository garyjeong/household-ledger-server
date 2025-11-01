"""
Transaction Service
Business logic for transaction use cases
"""

from typing import Optional
from datetime import datetime
from app.domain.repositories.transaction_repository import TransactionRepository
from app.domain.models.transaction import Transaction
from app.domain.models.category import Category


class TransactionService:
    """Transaction service with dependency injection"""
    
    def __init__(self, transaction_repository: TransactionRepository):
        self.transaction_repository = transaction_repository
    
    async def get_transactions(
        self,
        group_id: Optional[int],
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[Transaction], int]:
        """
        Get transactions with filters and pagination
        
        Returns:
            (transactions, total_count)
        """
        transactions = await self.transaction_repository.find_all(
            group_id=group_id,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            search=search,
            limit=limit,
            offset=offset
        )
        
        total_count = await self.transaction_repository.count_total(
            group_id=group_id,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            search=search
        )
        
        return transactions, total_count
    
    async def create_transaction(self, transaction: Transaction) -> Transaction:
        """Create new transaction"""
        # Validate transaction data
        if transaction.amount <= 0:
            raise ValueError("Amount must be positive")
        
        return await self.transaction_repository.create(transaction)
    
    async def get_transaction(self, transaction_id: int, user_id: int) -> Transaction:
        """Get transaction by ID"""
        transaction = await self.transaction_repository.find_by_id(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")
        
        # Check ownership
        if transaction.owner_user_id != user_id:
            raise ValueError("Unauthorized")
        
        return transaction
    
    async def update_transaction(
        self,
        transaction_id: int,
        user_id: int,
        updated_data: dict
    ) -> Transaction:
        """Update transaction"""
        transaction = await self.transaction_repository.find_by_id(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")
        
        # Check ownership
        if transaction.owner_user_id != user_id:
            raise ValueError("Unauthorized")
        
        # Update fields
        for key, value in updated_data.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)
        
        return await self.transaction_repository.update(transaction)
    
    async def delete_transaction(self, transaction_id: int, user_id: int) -> None:
        """Delete transaction"""
        transaction = await self.transaction_repository.find_by_id(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")
        
        # Check ownership
        if transaction.owner_user_id != user_id:
            raise ValueError("Unauthorized")
        
        await self.transaction_repository.delete(transaction_id)

