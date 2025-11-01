"""
Budget Service
Business logic for budget use cases
"""

from typing import Optional, List
from datetime import date, datetime
from app.domain.repositories.budget_repository import BudgetRepository
from app.domain.repositories.statistics_repository import StatisticsRepository
from app.domain.models.budget import Budget, OwnerType, BudgetStatus
from app.domain.models.category import Category
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_


class BudgetService:
    """Budget service with dependency injection"""
    
    def __init__(
        self,
        budget_repository: BudgetRepository,
        statistics_repository: StatisticsRepository,
        session: AsyncSession
    ):
        self.budget_repository = budget_repository
        self.statistics_repository = statistics_repository
        self.session = session
    
    async def get_budgets(
        self,
        owner_type: OwnerType,
        owner_id: int,
        status: Optional[BudgetStatus] = None
    ) -> List[Budget]:
        """Get budgets with filters"""
        return await self.budget_repository.find_all(
            owner_type=owner_type,
            owner_id=owner_id,
            status=status
        )
    
    async def get_budget(
        self,
        budget_id: int,
        owner_type: OwnerType,
        owner_id: int
    ) -> Budget:
        """Get budget by ID"""
        budget = await self.budget_repository.find_by_id(budget_id)
        if not budget:
            raise ValueError("Budget not found")
        
        # Check ownership
        if budget.owner_type != owner_type or budget.owner_id != owner_id:
            raise ValueError("Unauthorized")
        
        return budget
    
    async def create_or_update_budget(
        self,
        owner_type: OwnerType,
        owner_id: int,
        period: str,
        total_amount: int,
        status: BudgetStatus = BudgetStatus.ACTIVE
    ) -> Budget:
        """Create or update budget for a period"""
        # Validate period format (YYYY-MM)
        try:
            datetime.strptime(period, "%Y-%m")
        except ValueError:
            raise ValueError("Period must be in YYYY-MM format")
        
        # Check if budget exists
        existing = await self.budget_repository.find_by_owner_and_period(
            owner_type=owner_type,
            owner_id=owner_id,
            period=period
        )
        
        if existing:
            # Update existing budget
            existing.total_amount = total_amount
            existing.status = status
            return await self.budget_repository.update(existing)
        else:
            # Create new budget
            budget = Budget(
                owner_type=owner_type,
                owner_id=owner_id,
                period=period,
                total_amount=total_amount,
                status=status
            )
            return await self.budget_repository.create(budget)
    
    async def delete_budget(
        self,
        budget_id: int,
        owner_type: OwnerType,
        owner_id: int
    ) -> None:
        """Delete budget"""
        budget = await self.budget_repository.find_by_id(budget_id)
        if not budget:
            raise ValueError("Budget not found")
        
        # Check ownership
        if budget.owner_type != owner_type or budget.owner_id != owner_id:
            raise ValueError("Unauthorized")
        
        await self.budget_repository.delete(budget_id)
    
    async def get_budget_status(
        self,
        owner_type: OwnerType,
        owner_id: int,
        period: str
    ) -> dict:
        """
        Get budget status with spending breakdown
        
        Returns:
            Dictionary with total budget, spent amount, remaining budget,
            usage percentage, and category breakdown
        """
        # Get budget
        budget = await self.budget_repository.find_by_owner_and_period(
            owner_type=owner_type,
            owner_id=owner_id,
            period=period
        )
        
        total_budget = int(budget.total_amount) if budget else 0
        
        # Parse period to get date range
        try:
            year, month = map(int, period.split('-'))
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            end_date = end_date.replace(day=1)
            from datetime import timedelta
            end_date = end_date - timedelta(days=1)
        except (ValueError, AttributeError):
            raise ValueError("Invalid period format")
        
        # Get total spent amount
        group_id = owner_id if owner_type == OwnerType.GROUP else None
        user_id = owner_id if owner_type == OwnerType.USER else None
        
        summary = await self.statistics_repository.get_summary_statistics(
            user_id=user_id or 0,
            group_id=group_id,
            start_date=start_date,
            end_date=end_date
        )
        
        total_spent = summary['total_expense']
        remaining_budget = total_budget - total_spent
        usage_percent = (total_spent / total_budget * 100) if total_budget > 0 else 0
        
        # Get category breakdown
        from app.domain.models.transaction import Transaction, TransactionType
        
        # Get categories with budget (Category.type is stored as string)
        category_stmt = select(Category).where(
            and_(
                Category.budget_amount > 0,
                Category.type == "EXPENSE"
            )
        )
        
        if owner_type == OwnerType.GROUP:
            category_stmt = category_stmt.where(Category.group_id == owner_id)
        else:
            # For user, we need to check created_by or find through group
            category_stmt = category_stmt.where(Category.created_by == owner_id)
        
        category_result = await self.session.execute(category_stmt)
        categories = category_result.scalars().all()
        
        # Get spending per category
        category_breakdown = []
        for category in categories:
            # Get transactions for this category in the period
            tx_stmt = select(func.sum(Transaction.amount)).where(
                and_(
                    Transaction.category_id == category.id,
                    Transaction.type == TransactionType.EXPENSE,
                    Transaction.date >= start_date,
                    Transaction.date <= end_date
                )
            )
            
            tx_result = await self.session.execute(tx_stmt)
            spent = int(tx_result.scalar_one() or 0)
            category_budget = int(category.budget_amount or 0)
            remaining = category_budget - spent
            usage = (spent / category_budget * 100) if category_budget > 0 else 0
            
            category_breakdown.append({
                'category_id': category.id,
                'category_name': category.name,
                'budget': category_budget,
                'spent': spent,
                'remaining': remaining,
                'usage_percent': usage
            })
        
        return {
            'total_budget': total_budget,
            'total_spent': total_spent,
            'remaining_budget': remaining_budget,
            'usage_percent': usage_percent,
            'category_breakdown': category_breakdown
        }

