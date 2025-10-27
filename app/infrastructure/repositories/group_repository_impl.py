"""
Group Repository Implementation
ORM-based repository for group management
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.domain.models.group import Group, GroupInvite
from app.domain.models.user import User
from app.domain.repositories.group_repository import GroupRepository


class GroupRepositoryImpl(GroupRepository):
    """SQLAlchemy-based group repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_group_by_id(self, group_id: int) -> Optional[Group]:
        """Find group by ID with eager loading"""
        stmt = select(Group).where(Group.id == group_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_user_groups(self, user_id: int) -> list[Group]:
        """Find all groups for a user (owned or member)"""
        # Find groups where user is owner
        stmt_owned = select(Group).where(Group.owner_id == user_id)
        
        # Find groups where user is a member
        stmt_member = select(Group).join(User).where(User.id == user_id)
        
        result_owned = await self.session.execute(stmt_owned)
        result_member = await self.session.execute(stmt_member)
        
        owned_groups = result_owned.scalars().all()
        member_groups = result_member.scalars().all()
        
        # Combine and remove duplicates
        all_groups = {g.id: g for g in owned_groups + member_groups}
        return list(all_groups.values())
    
    async def create_group(self, name: str, owner_id: int) -> Group:
        """Create new group with ORM"""
        group = Group(
            name=name,
            owner_id=owner_id
        )
        self.session.add(group)
        await self.session.commit()
        await self.session.refresh(group)
        return group
    
    async def update_group(self, group: Group) -> Group:
        """Update group with ORM"""
        await self.session.merge(group)
        await self.session.commit()
        await self.session.refresh(group)
        return group
    
    async def delete_group(self, group_id: int) -> None:
        """Delete group with ORM (cascade will handle related records)"""
        stmt = select(Group).where(Group.id == group_id)
        result = await self.session.execute(stmt)
        group = result.scalar_one_or_none()
        if group:
            await self.session.delete(group)
            await self.session.commit()
    
    async def create_invite(
        self,
        group_id: int,
        code: str,
        created_by: int,
        expires_at: datetime
    ) -> GroupInvite:
        """Create group invite code"""
        invite = GroupInvite(
            group_id=group_id,
            code=code,
            created_by=created_by,
            expires_at=expires_at
        )
        self.session.add(invite)
        await self.session.commit()
        await self.session.refresh(invite)
        return invite
    
    async def find_invite_by_code(self, code: str) -> Optional[GroupInvite]:
        """Find invite by code"""
        stmt = select(GroupInvite).where(GroupInvite.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def add_user_to_group(self, user_id: int, group_id: int) -> None:
        """Add user to group"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one()
        user.group_id = group_id
        await self.session.commit()
    
    async def remove_user_from_group(self, user_id: int) -> None:
        """Remove user from group"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one()
        user.group_id = None
        await self.session.commit()

