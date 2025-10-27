"""
Category Repository Interface
"""

from typing import Protocol, Optional, List
from app.domain.models.category import Category


class CategoryRepository(Protocol):
    """Category repository interface"""
    
    async def find_by_id(self, category_id: int) -> Optional[Category]:
        """Find category by ID"""
        ...
    
    async def find_by_group_and_type(
        self,
        group_id: Optional[int],
        type: str,
        include_default: bool = True
    ) -> List[Category]:
        """Find categories by group and type"""
        ...
    
    async def create(self, category: Category) -> Category:
        """Create new category"""
        ...
    
    async def update(self, category: Category) -> Category:
        """Update category"""
        ...
    
    async def delete(self, category_id: int) -> None:
        """Delete category"""
        ...
    
    async def count_transactions(self, category_id: int) -> int:
        """Count transactions using this category"""
        ...

