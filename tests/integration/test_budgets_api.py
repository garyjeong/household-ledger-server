"""
Integration Tests for Budgets API
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_budgets(client: AsyncClient, test_user):
    """Test getting budgets"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get(
        "/api/v1/budgets",
        params={"owner_type": "USER"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


@pytest.mark.asyncio
async def test_create_budget(client: AsyncClient, test_user):
    """Test creating a budget"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.post(
        "/api/v1/budgets",
        json={
            "owner_type": "USER",
            "period": "2025-01",
            "total_amount": 1000000,
            "status": "ACTIVE"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["period"] == "2025-01"


@pytest.mark.asyncio
async def test_get_budget_status(client: AsyncClient, test_user):
    """Test getting budget status"""
    # Note: test_user fixture already overrides get_current_user
    # First create a budget
    create_response = await client.post(
        "/api/v1/budgets",
        json={
            "owner_type": "USER",
            "period": "2025-01",
            "total_amount": 1000000,
            "status": "ACTIVE"
        }
    )
    
    assert create_response.status_code == 201
    
    # Then get status
    response = await client.get(
        "/api/v1/budgets/status",
        params={
            "owner_type": "USER",
            "period": "2025-01"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "budget_status" in data["data"]


@pytest.mark.asyncio
async def test_update_budget(client: AsyncClient, test_user):
    """Test updating a budget"""
    # Note: test_user fixture already overrides get_current_user
    # First create a budget
    create_response = await client.post(
        "/api/v1/budgets",
        json={
            "owner_type": "USER",
            "period": "2025-01",
            "total_amount": 1000000,
            "status": "ACTIVE"
        }
    )
    
    assert create_response.status_code == 201
    budget_id = create_response.json()["data"]["id"]
    
    # Then update it
    response = await client.put(
        f"/api/v1/budgets/{budget_id}",
        params={"owner_type": "USER"},
        json={"total_amount": 1500000}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["total_amount"] == 1500000


@pytest.mark.asyncio
async def test_delete_budget(client: AsyncClient, test_user):
    """Test deleting a budget"""
    # Note: test_user fixture already overrides get_current_user
    # First create a budget
    create_response = await client.post(
        "/api/v1/budgets",
        json={
            "owner_type": "USER",
            "period": "2025-01",
            "total_amount": 1000000,
            "status": "ACTIVE"
        }
    )
    
    assert create_response.status_code == 201
    budget_id = create_response.json()["data"]["id"]
    
    # Then delete it
    response = await client.delete(
        f"/api/v1/budgets/{budget_id}",
        params={"owner_type": "USER"}
    )
    
    assert response.status_code == 204

