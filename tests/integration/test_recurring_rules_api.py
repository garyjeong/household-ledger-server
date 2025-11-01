"""
Integration Tests for RecurringRules API
"""

import pytest
from httpx import AsyncClient
from datetime import date


@pytest.mark.asyncio
async def test_create_recurring_rule(client: AsyncClient, test_user):
    """Test creating a recurring rule"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.post(
        "/api/v1/recurring-rules",
        json={
            "start_date": str(date.today()),
            "frequency": "MONTHLY",
            "day_rule": "1",
            "amount": 100000,
            "category_id": 1,
            "memo": "Monthly expense"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "data" in data


@pytest.mark.asyncio
async def test_get_recurring_rules(client: AsyncClient, test_user):
    """Test getting recurring rules list"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get("/api/v1/recurring-rules")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


@pytest.mark.asyncio
async def test_process_recurring_rules(client: AsyncClient, test_user):
    """Test processing recurring rules"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.post(
        "/api/v1/recurring-rules/process",
        json={"target_date": str(date.today())}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "created" in data

