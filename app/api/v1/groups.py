"""
Group API Router
Group management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.group import (
    GroupCreateRequest,
    GroupResponse,
    JoinGroupRequest,
    InviteCodeResponse
)
from app.dependencies import get_group_service, get_current_user
from app.application.services.group_service import GroupService
from app.domain.models.user import User
from datetime import datetime

router = APIRouter()


@router.get("", response_model=list[GroupResponse])
async def get_user_groups(
    current_user: User = Depends(get_current_user),
    service: GroupService = Depends(get_group_service)
):
    """Get all groups for current user"""
    groups = await service.get_user_groups(current_user.id)
    return groups


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    request: GroupCreateRequest,
    current_user: User = Depends(get_current_user),
    service: GroupService = Depends(get_group_service)
):
    """Create new group"""
    group = await service.create_group(
        user_id=current_user.id,
        name=request.name
    )
    return group


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    service: GroupService = Depends(get_group_service)
):
    """Get group by ID"""
    try:
        group = await service.get_group(group_id)
        return group
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    name: str,
    current_user: User = Depends(get_current_user),
    service: GroupService = Depends(get_group_service)
):
    """Update group (only owner)"""
    try:
        group = await service.update_group(group_id, current_user.id, name)
        return group
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    service: GroupService = Depends(get_group_service)
):
    """Delete group (only owner)"""
    try:
        await service.delete_group(group_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{group_id}/invite", response_model=InviteCodeResponse)
async def generate_invite_code(
    group_id: int,
    current_user: User = Depends(get_current_user),
    service: GroupService = Depends(get_group_service)
):
    """Generate invite code for group"""
    try:
        code = await service.generate_invite_code(group_id, current_user.id)
        return InviteCodeResponse(code=code, expires_at=str(datetime.now()))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/join", response_model=GroupResponse)
async def join_group(
    request: JoinGroupRequest,
    current_user: User = Depends(get_current_user),
    service: GroupService = Depends(get_group_service)
):
    """Join group using invite code"""
    try:
        group = await service.join_group(current_user.id, request.code)
        return group
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_group(
    current_user: User = Depends(get_current_user),
    service: GroupService = Depends(get_group_service)
):
    """Leave current group"""
    await service.leave_group(current_user.id)

