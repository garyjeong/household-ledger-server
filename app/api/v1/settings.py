"""
Settings API Router
User settings management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user
from app.domain.models.user import User
from app.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.services.settings_service import SettingsService
from app.schemas.settings import UpdateSettingsRequest, DEFAULT_SETTINGS

router = APIRouter()


def get_settings_service(db: AsyncSession = Depends(get_session)) -> SettingsService:
    """Dependency injection for SettingsService"""
    return SettingsService(db)


@router.get("", response_model=dict)
async def get_settings(
    current_user: User = Depends(get_current_user),
    service: SettingsService = Depends(get_settings_service)
):
    """Get user settings"""
    try:
        settings = await service.get_settings(current_user.id)
        
        return {
            "success": True,
            "settings": settings
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"설정 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("", response_model=dict)
async def update_settings(
    request: UpdateSettingsRequest,
    current_user: User = Depends(get_current_user),
    service: SettingsService = Depends(get_settings_service)
):
    """Update user settings"""
    try:
        settings = await service.update_settings(current_user.id, request)
        
        return {
            "success": True,
            "settings": settings,
            "message": "설정이 성공적으로 저장되었습니다"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"설정 업데이트 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("", response_model=dict)
async def reset_settings(
    current_user: User = Depends(get_current_user),
    service: SettingsService = Depends(get_settings_service)
):
    """Reset settings to default"""
    try:
        settings = await service.reset_settings(current_user.id)
        
        return {
            "success": True,
            "settings": settings,
            "message": "설정이 초기화되었습니다"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"설정 초기화 중 오류가 발생했습니다: {str(e)}"
        )

