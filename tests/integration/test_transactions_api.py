"""
Integration Tests for Transactions API
"""

import pytest
from httpx import AsyncClient
from datetime import date


@pytest.mark.asyncio
async def test_create_transaction(client: AsyncClient, test_user):
    """Test creating a transaction"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.post(
        "/api/v1/transactions",
        json={
            "type": "EXPENSE",
            "date": str(date.today()),
            "amount": 10000,
            "category_id": 1,
            "memo": "Test transaction"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 10000


@pytest.mark.asyncio
async def test_get_transactions(client: AsyncClient, test_user):
    """Test getting transactions list"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get("/api/v1/transactions")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_transactions_with_search(client: AsyncClient, test_user):
    """Test getting transactions with search"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get(
        "/api/v1/transactions",
        params={"search": "test"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_quick_add_transaction(client: AsyncClient, test_user):
    """Test quick add transaction"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.post(
        "/api/v1/transactions/quick-add",
        json={
            "type": "EXPENSE",
            "date": str(date.today()),
            "amount": 5000,
            "category_name": "식비",
            "memo": "Quick add test"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "transaction" in data


@pytest.mark.asyncio
async def test_get_transaction_by_id(client: AsyncClient, test_user):
    """Test getting transaction by ID"""
    # Note: test_user fixture already overrides get_current_user
    # First create a transaction
    create_response = await client.post(
        "/api/v1/transactions",
        json={
            "type": "EXPENSE",
            "date": str(date.today()),
            "amount": 10000,
            "category_id": 1
        }
    )
    
    assert create_response.status_code == 201
    transaction_id = create_response.json()["id"]
    
    # Then get it
    response = await client.get(f"/api/v1/transactions/{transaction_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == transaction_id


@pytest.mark.asyncio
async def test_update_transaction(client: AsyncClient, test_user):
    """Test updating a transaction"""
    # Note: test_user fixture already overrides get_current_user
    # First create a transaction
    create_response = await client.post(
        "/api/v1/transactions",
        json={
            "type": "EXPENSE",
            "date": str(date.today()),
            "amount": 10000,
            "category_id": 1
        }
    )
    
    assert create_response.status_code == 201
    transaction_id = create_response.json()["id"]
    
    # Then update it
    response = await client.put(
        f"/api/v1/transactions/{transaction_id}",
        json={"amount": 15000}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 15000


@pytest.mark.asyncio
async def test_delete_transaction(client: AsyncClient, test_user):
    """Test deleting a transaction"""
    # Note: test_user fixture already overrides get_current_user
    # First create a transaction
    create_response = await client.post(
        "/api/v1/transactions",
        json={
            "type": "EXPENSE",
            "date": str(date.today()),
            "amount": 10000,
            "category_id": 1
        }
    )
    
    assert create_response.status_code == 201
    transaction_id = create_response.json()["id"]
    
    # Then delete it
    response = await client.delete(f"/api/v1/transactions/{transaction_id}")
    
    assert response.status_code == 204

