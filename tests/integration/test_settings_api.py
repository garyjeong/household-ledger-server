"""
Integration Tests for Settings API
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_settings(client: AsyncClient, test_user):
    """Test getting user settings"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get("/api/v1/settings")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "settings" in data


@pytest.mark.asyncio
async def test_update_settings(client: AsyncClient, test_user):
    """Test updating user settings"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.put(
        "/api/v1/settings",
        json={
            "currency": "USD",
            "theme": "dark",
            "language": "en"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["settings"]["currency"] == "USD"
    assert data["settings"]["theme"] == "dark"


@pytest.mark.asyncio
async def test_reset_settings(client: AsyncClient, test_user):
    """Test resetting user settings"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.delete("/api/v1/settings")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "설정이 초기화되었습니다"

