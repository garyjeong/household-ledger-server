"""
Integration Tests for Balance API
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_balance(client: AsyncClient, test_user):
    """Test getting balance"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get("/api/v1/balance")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "balance" in data["data"]


@pytest.mark.asyncio
async def test_get_balance_with_projection(client: AsyncClient, test_user):
    """Test getting balance with projection"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get(
        "/api/v1/balance",
        params={
            "include_projection": True,
            "projection_months": 3
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "monthly_trend" in data["data"]


@pytest.mark.asyncio
async def test_get_balance_with_period(client: AsyncClient, test_user):
    """Test getting balance with specific period"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get(
        "/api/v1/balance",
        params={"period": "2025-01"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "period_data" in data["data"]

