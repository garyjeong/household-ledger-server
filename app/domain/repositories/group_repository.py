"""
Group Repository Interface
"""

from typing import Protocol, Optional, List
from app.domain.models.group import Group, GroupInvite


class GroupRepository(Protocol):
    """Group repository interface"""
    
    async def find_group_by_id(self, group_id: int) -> Optional[Group]:
        """Find group by ID"""
        ...
    
    async def find_user_groups(self, user_id: int) -> List[Group]:
        """Find all groups for a user"""
        ...
    
    async def create_group(self, name: str, owner_id: int) -> Group:
        """Create new group"""
        ...
    
    async def update_group(self, group: Group) -> Group:
        """Update group information"""
        ...
    
    async def delete_group(self, group_id: int) -> None:
        """Delete group"""
        ...
    
    async def create_invite(self, group_id: int, code: str, created_by: int, expires_at) -> GroupInvite:
        """Create group invite code"""
        ...
    
    async def find_invite_by_code(self, code: str) -> Optional[GroupInvite]:
        """Find invite by code"""
        ...
    
    async def add_user_to_group(self, user_id: int, group_id: int) -> None:
        """Add user to group"""
        ...
    
    async def remove_user_from_group(self, user_id: int) -> None:
        """Remove user from group"""
        ...

