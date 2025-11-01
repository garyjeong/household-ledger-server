"""
Settings Service
Business logic for user settings
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.models.user import User
from app.schemas.settings import AppSettings, UpdateSettingsRequest, DEFAULT_SETTINGS


class SettingsService:
    """Settings service with dependency injection"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_settings(self, user_id: int) -> dict:
        """Get user settings"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        # Return settings or default
        if user.settings:
            # Merge with defaults to ensure all keys exist
            merged_settings = {**DEFAULT_SETTINGS, **user.settings}
            return merged_settings
        
        return DEFAULT_SETTINGS

    async def update_settings(self, user_id: int, updates: UpdateSettingsRequest) -> dict:
        """Update user settings"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        # Get current settings
        current_settings = user.settings or DEFAULT_SETTINGS.copy()

        # Update settings
        update_dict = updates.model_dump(exclude_unset=True)
        
        # Handle nested category_display
        if 'category_display' in update_dict and update_dict['category_display'] is not None:
            if 'category_display' not in current_settings:
                current_settings['category_display'] = DEFAULT_SETTINGS['category_display'].copy()
            
            category_updates = update_dict.pop('category_display')
            current_settings['category_display'].update(category_updates.model_dump(exclude_unset=True))

        # Update other settings
        current_settings.update(update_dict)

        # Save to database
        user.settings = current_settings
        await self.session.commit()
        await self.session.refresh(user)

        return current_settings

    async def reset_settings(self, user_id: int) -> dict:
        """Reset settings to default"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        # Reset to default
        user.settings = None
        await self.session.commit()
        await self.session.refresh(user)

        return DEFAULT_SETTINGS

