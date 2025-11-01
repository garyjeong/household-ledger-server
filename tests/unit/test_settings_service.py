"""
Unit Tests for SettingsService
"""

import pytest
from unittest.mock import AsyncMock
from sqlalchemy import select
from app.application.services.settings_service import SettingsService
from app.domain.models.user import User
from app.schemas.settings import UpdateSettingsRequest, DEFAULT_SETTINGS


@pytest.fixture
def mock_session():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def settings_service(mock_session):
    """SettingsService with mocked session"""
    return SettingsService(session=mock_session)


@pytest.mark.asyncio
async def test_get_settings_default(settings_service, mock_session):
    """Test getting default settings when user has no settings"""
    # Arrange
    user = User(
        id=1,
        email="test@example.com",
        nickname="TestUser",
        settings=None  # No settings
    )
    
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = mock_result
    
    # Act
    result = await settings_service.get_settings(1)
    
    # Assert
    assert result == DEFAULT_SETTINGS
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_settings_existing(settings_service, mock_session):
    """Test getting existing user settings"""
    # Arrange
    existing_settings = {
        "currency": "USD",
        "theme": "dark",
        "language": "en"
    }
    
    user = User(
        id=1,
        email="test@example.com",
        nickname="TestUser",
        settings=existing_settings
    )
    
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = mock_result
    
    # Act
    result = await settings_service.get_settings(1)
    
    # Assert
    assert result['currency'] == 'USD'
    assert result['theme'] == 'dark'
    # Should merge with defaults
    assert 'show_won_suffix' in result
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_update_settings_success(settings_service, mock_session):
    """Test successful settings update"""
    # Arrange
    user = User(
        id=1,
        email="test@example.com",
        nickname="TestUser",
        settings={'currency': 'KRW'}
    )
    
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = mock_result
    
    update_request = UpdateSettingsRequest(
        currency="USD",
        theme="dark"
    )
    
    # Act
    result = await settings_service.update_settings(1, update_request)
    
    # Assert
    assert result['currency'] == 'USD'
    assert result['theme'] == 'dark'
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_reset_settings_success(settings_service, mock_session):
    """Test successful settings reset"""
    # Arrange
    user = User(
        id=1,
        email="test@example.com",
        nickname="TestUser",
        settings={'currency': 'USD'}
    )
    
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = mock_result
    
    # Act
    result = await settings_service.reset_settings(1)
    
    # Assert
    assert result == DEFAULT_SETTINGS
    assert user.settings is None
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_settings_user_not_found(settings_service, mock_session):
    """Test getting settings when user not found"""
    # Arrange
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    # Act & Assert
    with pytest.raises(ValueError, match="User not found"):
        await settings_service.get_settings(999)

