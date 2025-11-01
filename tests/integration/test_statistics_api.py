"""
Integration Tests for Statistics API
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_statistics_current_month(client: AsyncClient, test_user):
    """Test getting statistics for current month"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get(
        "/api/v1/statistics",
        params={"period": "current-month"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "summary" in data["data"]
    assert "category_statistics" in data["data"]


@pytest.mark.asyncio
async def test_get_statistics_last_month(client: AsyncClient, test_user):
    """Test getting statistics for last month"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get(
        "/api/v1/statistics",
        params={"period": "last-month"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_get_statistics_custom_dates(client: AsyncClient, test_user):
    """Test getting statistics with custom date range"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get(
        "/api/v1/statistics",
        params={
            "start_date": "2025-01-01",
            "end_date": "2025-01-31"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_get_statistics_with_group(client: AsyncClient, test_user):
    """Test getting statistics with group filter"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get(
        "/api/v1/statistics",
        params={
            "period": "current-month",
            "group_id": 1
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

