"""
Group Schemas (DTO)
Pydantic models for group API
"""

from pydantic import BaseModel, Field
from typing import Optional


class GroupCreateRequest(BaseModel):
    """Create group request"""
    name: str = Field(min_length=1, max_length=120)


class GroupResponse(BaseModel):
    """Group response"""
    id: int
    name: str
    owner_id: int
    
    class Config:
        from_attributes = True


class JoinGroupRequest(BaseModel):
    """Join group request"""
    code: str = Field(min_length=10, max_length=10)


class InviteCodeResponse(BaseModel):
    """Invite code response"""
    code: str
    expires_at: str
    
    class Config:
        from_attributes = True

