"""
Auth Repository Implementation
ORM-based repository for authentication
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.domain.models.user import User
from app.domain.repositories.auth_repository import AuthRepository


class AuthRepositoryImpl(AuthRepository):
    """SQLAlchemy-based authentication repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_user_by_email(self, email: str) -> Optional[User]:
        """Find user by email using ORM query"""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_user_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID using ORM query"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_user(self, email: str, password_hash: str, nickname: str) -> User:
        """Create new user with ORM"""
        user = User(
            email=email,
            password_hash=password_hash,
            nickname=nickname
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update_user(self, user: User) -> User:
        """Update user with ORM"""
        await self.session.merge(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def verify_user_password(self, email: str, password_hash: str) -> Optional[User]:
        """Verify user credentials"""
        # This is handled by service layer with password_hasher
        # Just find user by email here
        return await self.find_user_by_email(email)

