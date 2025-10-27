"""
Category Service
Business logic for category management use cases
"""

from typing import Optional
from app.domain.repositories.category_repository import CategoryRepository
from app.domain.models.category import Category


class CategoryService:
    """Category service with dependency injection"""
    
    def __init__(self, category_repository: CategoryRepository):
        self.category_repository = category_repository
    
    async def get_categories(
        self,
        group_id: Optional[int],
        type: str,
        include_default: bool = True
    ) -> list[Category]:
        """Get categories by group and type"""
        return await self.category_repository.find_by_group_and_type(
            group_id=group_id,
            type=type,
            include_default=include_default
        )
    
    async def create_category(self, category: Category) -> Category:
        """Create new category"""
        # Check for duplicate
        existing = await self.category_repository.find_by_group_and_type(
            group_id=category.group_id,
            type=category.type,
            include_default=False
        )
        
        for cat in existing:
            if cat.name == category.name and cat.group_id == category.group_id:
                raise ValueError("Category already exists")
        
        return await self.category_repository.create(category)
    
    async def update_category(self, category: Category) -> Category:
        """Update category"""
        return await self.category_repository.update(category)
    
    async def delete_category(self, category_id: int) -> None:
        """Delete category (only if no transactions use it)"""
        count = await self.category_repository.count_transactions(category_id)
        if count > 0:
            raise ValueError("Cannot delete category with existing transactions")
        
        await self.category_repository.delete(category_id)

