"""
Auth Repository Interface
"""

from typing import Protocol, Optional
from app.domain.models.user import User


class AuthRepository(Protocol):
    """Authentication repository interface"""
    
    async def find_user_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        ...
    
    async def find_user_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID"""
        ...
    
    async def create_user(self, email: str, password_hash: str, nickname: str) -> User:
        """Create new user"""
        ...
    
    async def update_user(self, user: User) -> User:
        """Update user information"""
        ...
    
    async def verify_user_password(self, email: str, password_hash: str) -> Optional[User]:
        """Verify user credentials"""
        ...

