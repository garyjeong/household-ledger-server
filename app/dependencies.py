"""
Dependency Injection
FastAPI dependency functions for dependency injection
"""

from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.domain.models.user import User
from app.application.factories.token_factory import TokenFactory
from app.application.services.auth_service import AuthService
from app.application.services.group_service import GroupService
from app.application.services.transaction_service import TransactionService
from app.infrastructure.repositories.auth_repository_impl import AuthRepositoryImpl
from app.infrastructure.repositories.group_repository_impl import GroupRepositoryImpl


# Token Factory
token_factory = TokenFactory()


async def get_db() -> AsyncSession:
    """Get database session"""
    async for session in get_session():
        yield session


async def get_current_user(
    authorization: str = Header(..., description="Bearer token"),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Dependency: Requires valid access token
    """
    # Extract token from Authorization header
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    try:
        # Verify token
        payload = token_factory.get_user_from_token(token, "access")
        user_id = int(payload["sub"])
        
        # Get user from database
        from app.domain.models.user import User
        from sqlalchemy import select
        
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Get authentication service"""
    auth_repo = AuthRepositoryImpl(db)
    return AuthService(auth_repository=auth_repo)


async def get_group_service(db: AsyncSession = Depends(get_db)) -> GroupService:
    """Get group service"""
    group_repo = GroupRepositoryImpl(db)
    return GroupService(group_repository=group_repo)


async def get_transaction_service(db: AsyncSession = Depends(get_db)) -> TransactionService:
    """Get transaction service"""
    from app.infrastructure.repositories.transaction_repository_impl import TransactionRepositoryImpl
    transaction_repo = TransactionRepositoryImpl(db)
    return TransactionService(transaction_repository=transaction_repo)

