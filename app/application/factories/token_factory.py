"""
Token Factory
Factory pattern for creating authentication tokens
"""

from datetime import timedelta
from dataclasses import dataclass
from app.infrastructure.security.jwt_handler import create_access_token, create_refresh_token, verify_and_decode_token
from app.config import settings


@dataclass
class AuthTokens:
    """Authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenFactory:
    """Factory for creating authentication tokens"""
    
    @staticmethod
    def create_tokens(user_id: int, email: str) -> AuthTokens:
        """Create both access and refresh tokens"""
        payload = {
            "sub": str(user_id),
            "email": email
        }
        
        access_token = create_access_token(
            payload,
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
        )
        refresh_token = create_refresh_token(payload)
        
        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    @staticmethod
    def get_user_from_token(token: str, token_type: str = "access") -> dict:
        """Extract user info from token"""
        return verify_and_decode_token(token, token_type)

