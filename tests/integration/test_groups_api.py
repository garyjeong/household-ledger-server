"""
Integration Tests for Groups API
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_groups(client: AsyncClient, test_user):
    """Test getting user groups"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get("/api/v1/groups")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_group(client: AsyncClient, test_user):
    """Test creating a group"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.post(
        "/api/v1/groups",
        json={"name": "테스트 그룹"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "테스트 그룹"


@pytest.mark.asyncio
async def test_get_group_by_id(client: AsyncClient, test_user):
    """Test getting group by ID"""
    # Note: test_user fixture already overrides get_current_user
    # First create a group
    create_response = await client.post(
        "/api/v1/groups",
        json={"name": "테스트 그룹"}
    )
    
    assert create_response.status_code == 201
    group_id = create_response.json()["id"]
    
    # Then get it
    response = await client.get(f"/api/v1/groups/{group_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == group_id


@pytest.mark.asyncio
async def test_update_group(client: AsyncClient, test_user):
    """Test updating a group"""
    # Note: test_user fixture already overrides get_current_user
    # First create a group
    create_response = await client.post(
        "/api/v1/groups",
        json={"name": "테스트 그룹"}
    )
    
    assert create_response.status_code == 201
    group_id = create_response.json()["id"]
    
    # Then update it
    response = await client.put(
        f"/api/v1/groups/{group_id}",
        json={"name": "수정된 그룹"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "수정된 그룹"


@pytest.mark.asyncio
async def test_delete_group(client: AsyncClient, test_user):
    """Test deleting a group"""
    # Note: test_user fixture already overrides get_current_user
    # First create a group
    create_response = await client.post(
        "/api/v1/groups",
        json={"name": "테스트 그룹"}
    )
    
    assert create_response.status_code == 201
    group_id = create_response.json()["id"]
    
    # Then delete it
    response = await client.delete(f"/api/v1/groups/{group_id}")
    
    assert response.status_code == 204

