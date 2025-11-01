"""
Settings Schemas (DTO)
Pydantic models for settings API
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal


class CategoryDisplaySettings(BaseModel):
    """Category display settings"""
    show_icons: Optional[bool] = True
    icon_style: Optional[Literal['default', 'modern', 'minimal']] = 'default'
    color_style: Optional[Literal['vibrant', 'pastel', 'monochrome']] = 'vibrant'
    group_by_type: Optional[bool] = True
    sort_by: Optional[Literal['name', 'usage', 'amount', 'recent']] = 'name'

    class Config:
        json_schema_extra = {
            "example": {
                "show_icons": True,
                "icon_style": "default",
                "color_style": "vibrant",
                "group_by_type": True,
                "sort_by": "name"
            }
        }


class AppSettings(BaseModel):
    """Application settings"""
    currency: Literal['KRW', 'USD', 'EUR', 'JPY'] = 'KRW'
    show_won_suffix: bool = True
    default_landing: Literal['dashboard', 'transactions', 'statistics'] = 'dashboard'
    theme: Literal['light', 'dark', 'system'] = 'system'
    language: Literal['ko', 'en'] = 'ko'
    category_display: Optional[CategoryDisplaySettings] = CategoryDisplaySettings()
    enable_notifications: bool = True
    notification_sound: bool = True
    budget_alerts: bool = True
    compact_mode: bool = False
    show_tutorials: bool = True
    quick_input_shortcuts: bool = True
    partner_name: Optional[str] = None
    split_default: int = Field(default=50, ge=0, le=100)


class UpdateSettingsRequest(BaseModel):
    """Update settings request"""
    currency: Optional[Literal['KRW', 'USD', 'EUR', 'JPY']] = None
    show_won_suffix: Optional[bool] = None
    default_landing: Optional[Literal['dashboard', 'transactions', 'statistics']] = None
    theme: Optional[Literal['light', 'dark', 'system']] = None
    language: Optional[Literal['ko', 'en']] = None
    category_display: Optional[CategoryDisplaySettings] = None
    enable_notifications: Optional[bool] = None
    notification_sound: Optional[bool] = None
    budget_alerts: Optional[bool] = None
    compact_mode: Optional[bool] = None
    show_tutorials: Optional[bool] = None
    quick_input_shortcuts: Optional[bool] = None
    partner_name: Optional[str] = None
    split_default: Optional[int] = Field(None, ge=0, le=100)


# Default settings
DEFAULT_SETTINGS = AppSettings().model_dump()

