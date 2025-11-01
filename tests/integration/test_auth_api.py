"""
Integration Tests for Auth API
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    """Test successful user signup"""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "nickname": "NewUser"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, test_user):
    """Test signup with duplicate email"""
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "test@example.com",
            "password": "password123",
            "nickname": "AnotherUser"
        }
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    """Test successful login"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials"""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user):
    """Test getting current user profile"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user):
    """Test token refresh"""
    response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": test_user["refresh_token"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, test_user):
    """Test logout"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.post("/api/v1/auth/logout")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient, test_user):
    """Test getting user profile"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.get("/api/v1/auth/profile")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "user" in data


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, test_user):
    """Test updating user profile"""
    # Note: test_user fixture already overrides get_current_user
    response = await client.put(
        "/api/v1/auth/profile",
        json={
            "nickname": "UpdatedUser",
            "email": "updated@example.com"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["name"] == "UpdatedUser"

