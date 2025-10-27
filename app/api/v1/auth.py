"""
Authentication API Router
TDD: Tests written first, now implementing to make tests pass
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    AccessTokenResponse,
    UserProfileResponse,
    ChangePasswordRequest,
    RefreshTokenRequest
)
from app.dependencies import get_auth_service, get_current_user
from app.application.services.auth_service import AuthService
from app.domain.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    service: AuthService = Depends(get_auth_service)
):
    """
    Sign up new user
    
    - **email**: User email (must be unique)
    - **password**: Password (min 8 characters)
    - **nickname**: Display name
    """
    try:
        user, tokens = await service.signup(
            email=request.email,
            password=request.password,
            nickname=request.nickname
        )
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    """
    Login existing user
    
    - **email**: User email
    - **password**: User password
    """
    try:
        result = await service.login(
            email=request.email,
            password=request.password
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Refresh token from login
    """
    try:
        result = await service.refresh_token(request.refresh_token)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return current_user


@router.put("/me")
async def update_profile(
    nickname: str,
    current_user: User = Depends(get_current_user)
):
    """Update user profile"""
    # TODO: Implement profile update logic
    current_user.nickname = nickname
    return {"message": "Profile updated"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service)
):
    """Change user password"""
    try:
        await service.change_password(
            user_id=current_user.id,
            old_password=request.old_password,
            new_password=request.new_password
        )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/check-email")
async def check_email(email: str):
    """Check if email is available"""
    # TODO: Implement email check logic
    return {"available": True, "email": email}

