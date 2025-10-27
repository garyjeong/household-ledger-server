"""
Group Service
Business logic for group management use cases
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional
from app.domain.repositories.group_repository import GroupRepository
from app.domain.models.group import Group, GroupInvite


class GroupService:
    """Group service with dependency injection"""
    
    def __init__(self, group_repository: GroupRepository):
        self.group_repository = group_repository
    
    async def get_user_groups(self, user_id: int) -> list[Group]:
        """Get all groups for a user"""
        return await self.group_repository.find_user_groups(user_id)
    
    async def create_group(self, user_id: int, name: str) -> Group:
        """Create new group"""
        group = await self.group_repository.create_group(
            name=name,
            owner_id=user_id
        )
        return group
    
    async def get_group(self, group_id: int) -> Group:
        """Get group by ID"""
        group = await self.group_repository.find_group_by_id(group_id)
        if not group:
            raise ValueError("Group not found")
        return group
    
    async def update_group(self, group_id: int, user_id: int, name: str) -> Group:
        """Update group (only owner can update)"""
        group = await self.group_repository.find_group_by_id(group_id)
        if not group:
            raise ValueError("Group not found")
        if group.owner_id != user_id:
            raise ValueError("Only group owner can update")
        
        group.name = name
        return await self.group_repository.update_group(group)
    
    async def delete_group(self, group_id: int, user_id: int) -> None:
        """Delete group (only owner can delete)"""
        group = await self.group_repository.find_group_by_id(group_id)
        if not group:
            raise ValueError("Group not found")
        if group.owner_id != user_id:
            raise ValueError("Only group owner can delete")
        
        await self.group_repository.delete_group(group_id)
    
    async def generate_invite_code(self, group_id: int, user_id: int) -> str:
        """Generate invite code for group"""
        # Check if user is group owner
        group = await self.group_repository.find_group_by_id(group_id)
        if not group:
            raise ValueError("Group not found")
        if group.owner_id != user_id:
            raise ValueError("Only group owner can generate invite")
        
        # Generate random code
        code = ''.join(secrets.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(10))
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # Create invite
        invite = await self.group_repository.create_invite(
            group_id=group_id,
            code=code,
            created_by=user_id,
            expires_at=expires_at
        )
        
        return code
    
    async def join_group(self, user_id: int, code: str) -> Group:
        """Join group using invite code"""
        # Find invite
        invite = await self.group_repository.find_invite_by_code(code)
        if not invite:
            raise ValueError("Invalid invite code")
        
        # Check expiration
        if invite.expires_at < datetime.utcnow():
            raise ValueError("Invite code expired")
        
        # Add user to group
        await self.group_repository.add_user_to_group(user_id, invite.group_id)
        
        # Return group
        return await self.group_repository.find_group_by_id(invite.group_id)
    
    async def leave_group(self, user_id: int) -> None:
        """Leave group"""
        await self.group_repository.remove_user_from_group(user_id)

