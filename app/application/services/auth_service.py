"""
Authentication Service
Business logic for authentication use cases
"""

from typing import Optional
from app.domain.repositories.auth_repository import AuthRepository
from app.infrastructure.security.password_hasher import hash_password, verify_password
from app.application.factories.token_factory import TokenFactory
from app.domain.models.user import User
from datetime import datetime, timedelta


class AuthService:
    """Authentication service with dependency injection"""
    
    def __init__(
        self,
        auth_repository: AuthRepository
    ):
        self.auth_repository = auth_repository
        self.token_factory = TokenFactory()
    
    async def signup(
        self,
        email: str,
        password: str,
        nickname: str
    ) -> tuple[User, dict]:
        """
        Sign up new user
        
        Returns:
            (User, AuthTokens dict)
        """
        # Check if user already exists
        existing_user = await self.auth_repository.find_user_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        user = await self.auth_repository.create_user(
            email=email,
            password_hash=password_hash,
            nickname=nickname
        )
        
        # Create tokens
        tokens = self.token_factory.create_tokens(user.id, user.email)
        
        return user, {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type
        }
    
    async def login(self, email: str, password: str) -> dict:
        """
        Login existing user
        
        Returns:
            AuthTokens dict
        """
        # Find user
        user = await self.auth_repository.find_user_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        # Create tokens
        tokens = self.token_factory.create_tokens(user.id, user.email)
        
        return {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
            "user": {
                "id": user.id,
                "email": user.email,
                "nickname": user.nickname
            }
        }
    
    async def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh access token
        
        Returns:
            New access token
        """
        # Verify and decode refresh token
        payload = self.token_factory.get_user_from_token(refresh_token, "refresh")
        user_id = int(payload["sub"])
        
        # Find user
        user = await self.auth_repository.find_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Create new access token
        tokens = self.token_factory.create_tokens(user.id, user.email)
        
        return {
            "access_token": tokens.access_token,
            "token_type": tokens.token_type
        }
    
    async def get_current_user(self, token: str) -> User:
        """
        Get current user from access token
        
        Returns:
            User
        """
        payload = self.token_factory.get_user_from_token(token, "access")
        user_id = int(payload["sub"])
        
        user = await self.auth_repository.find_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return user
    
    async def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> None:
        """Change user password"""
        user = await self.auth_repository.find_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify old password
        if not verify_password(old_password, user.password_hash):
            raise ValueError("Invalid password")
        
        # Update password
        new_hash = hash_password(new_password)
        user.password_hash = new_hash
        await self.auth_repository.update_user(user)
    
    async def forgot_password(self, email: str) -> str:
        """
        Generate password reset token for user
        
        Returns:
            Reset token
        """
        # Find user by email
        user = await self.auth_repository.find_user_by_email(email)
        if not user:
            # Don't reveal if email exists for security
            # Return a dummy token to prevent email enumeration
            pass
        
        # Create reset token (valid for 1 hour)
        from app.infrastructure.security.jwt_handler import create_reset_token
        reset_token = create_reset_token(user.id, user.email, timedelta(hours=1))
        
        # TODO: Send email with reset link
        # For now, just return the token
        # In production, this should send an email with the token
        
        return reset_token
    
    async def reset_password(self, token: str, new_password: str) -> None:
        """
        Reset password using reset token
        
        Args:
            token: Password reset token
            new_password: New password
        """
        # Verify reset token
        from app.infrastructure.security.jwt_handler import verify_and_decode_token
        try:
            payload = verify_and_decode_token(token, "reset")
        except Exception:
            raise ValueError("Invalid or expired reset token")
        
        user_id = int(payload["sub"])
        email = payload.get("email")
        
        # Find user
        user = await self.auth_repository.find_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify email matches
        if email and user.email != email:
            raise ValueError("Invalid token")
        
        # Update password
        new_hash = hash_password(new_password)
        user.password_hash = new_hash
        await self.auth_repository.update_user(user)

