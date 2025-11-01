"""
Integration Tests for Categories API
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_categories(client: AsyncClient, test_user):
    """Test getting categories"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get(
        "/api/v1/categories",
        params={"type": "EXPENSE"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_category(client: AsyncClient, test_user):
    """Test creating a category"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.post(
        "/api/v1/categories",
        params={
            "name": "테스트 카테고리",
            "type": "EXPENSE",
            "color": "#FF5733"
        }
    )
    
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_update_category(client: AsyncClient, test_user):
    """Test updating a category"""
    # Note: test_user fixture already overrides get_current_user
    # First create a category
    create_response = await client.post(
        "/api/v1/categories",
        params={
            "name": "테스트 카테고리",
            "type": "EXPENSE",
            "color": "#FF5733"
        }
    )
    
    assert create_response.status_code == 201
    category_id = create_response.json()["id"]
    
    # Then update it
    response = await client.put(
        f"/api/v1/categories/{category_id}",
        params={
            "name": "수정된 카테고리",
            "color": "#33FF57"
        }
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_category(client: AsyncClient, test_user):
    """Test deleting a category"""
    # Note: test_user fixture already overrides get_current_user
    # First create a category
    create_response = await client.post(
        "/api/v1/categories",
        params={
            "name": "테스트 카테고리",
            "type": "EXPENSE",
            "color": "#FF5733"
        }
    )
    
    assert create_response.status_code == 201
    category_id = create_response.json()["id"]
    
    # Then delete it
    response = await client.delete(f"/api/v1/categories/{category_id}")
    
    assert response.status_code == 204

