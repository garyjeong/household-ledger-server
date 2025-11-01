"""
Integration Tests for Dashboard API
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_monthly_stats(client: AsyncClient, test_user):
    """Test getting monthly dashboard stats"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get(
        "/api/v1/dashboard/monthly-stats",
        params={
            "year": 2025,
            "month": 1
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


@pytest.mark.asyncio
async def test_get_monthly_stats_default(client: AsyncClient, test_user):
    """Test getting monthly stats with default values"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get("/api/v1/dashboard/monthly-stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_get_monthly_stats_with_group(client: AsyncClient, test_user):
    """Test getting monthly stats with group filter"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get(
        "/api/v1/dashboard/monthly-stats",
        params={
            "year": 2025,
            "month": 1,
            "group_id": 1
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

