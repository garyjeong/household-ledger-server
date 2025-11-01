"""
JWT Token Handler
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_refresh_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_reset_token(user_id: int, email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create password reset token"""
    to_encode = {
        "sub": str(user_id),
        "email": email
    }
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)  # Reset token expires in 1 hour
    
    to_encode.update({"exp": expire, "type": "reset"})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_and_decode_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode JWT token"""
    secret = settings.jwt_secret if token_type in ("access", "reset") else settings.jwt_refresh_secret
    
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.jwt_algorithm]
        )
        
        if token_type == "reset" and payload.get("type") != "reset":
            raise JWTError("Invalid token type")
        elif token_type != "reset" and payload.get("type") != token_type:
            raise JWTError("Invalid token type")
        
        return payload
    except JWTError:
        raise JWTError("Invalid token")

