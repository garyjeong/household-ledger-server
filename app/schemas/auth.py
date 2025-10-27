"""
Authentication Schemas (DTO)
Pydantic models for authentication API
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class SignupRequest(BaseModel):
    """Signup request schema"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nickname: str = Field(min_length=1, max_length=60)


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    """Access token only response"""
    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    """User profile response"""
    id: int
    email: str
    nickname: str
    avatar_url: Optional[str]
    group_id: Optional[int]
    
    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    old_password: str
    new_password: str = Field(min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

