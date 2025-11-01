"""
Authentication API Router
TDD: Tests written first, now implementing to make tests pass
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
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


@router.post("/logout")
async def logout():
    """Logout user (token invalidation)"""
    # Note: In JWT-based auth, logout is handled client-side by removing tokens
    # For server-side token blacklisting, would need token storage/blacklist table
    return {
        "success": True,
        "message": "로그아웃되었습니다."
    }


@router.get("/profile", response_model=dict)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get user profile"""
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "name": current_user.nickname,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat() if hasattr(current_user.created_at, 'isoformat') else str(current_user.created_at),
        }
    }


@router.put("/profile", response_model=dict)
async def update_profile(
    nickname: Optional[str] = None,
    email: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
    db: AsyncSession = Depends(get_session)
):
    """Update user profile"""
    try:
        from app.infrastructure.repositories.auth_repository_impl import AuthRepositoryImpl
        from sqlalchemy import select, and_
        
        auth_repo = AuthRepositoryImpl(db)
        
        # Email duplicate check (exclude current user)
        if email and email != current_user.email:
            existing_user = await auth_repo.find_user_by_email(email)
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="이미 사용 중인 이메일입니다"
                )
        
        # Update fields
        if nickname:
            current_user.nickname = nickname
        if email:
            current_user.email = email
        
        updated_user = await auth_repo.update_user(current_user)
        
        return {
            "success": True,
            "message": "프로필이 성공적으로 업데이트되었습니다",
            "user": {
                "id": updated_user.id,
                "name": updated_user.nickname,
                "email": updated_user.email,
                "created_at": updated_user.created_at.isoformat() if hasattr(updated_user.created_at, 'isoformat') else str(updated_user.created_at),
            }
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 업데이트 중 오류가 발생했습니다: {str(e)}"
        )


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

