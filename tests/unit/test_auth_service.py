"""
Unit Tests for AuthService
TDD approach: Test first, then implement
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, Mock, MagicMock, patch
from app.application.services.auth_service import AuthService
from app.domain.models.user import User


@patch('app.application.services.auth_service.hash_password')
async def fake_hash_password(password: str, mock_hash):
    """Mock password hasher"""
    return f"hashed_{password}"


@pytest.fixture
def mock_auth_repo():
    """Mock auth repository"""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_auth_repo):
    """AuthService with mocked repository"""
    return AuthService(auth_repository=mock_auth_repo)


@pytest.mark.asyncio
async def test_signup_success(auth_service, mock_auth_repo):
    """Test successful signup"""
    # Arrange
    email = "test@example.com"
    password = "password123"
    nickname = "TestUser"
    
    mock_auth_repo.find_user_by_email.return_value = None
    mock_auth_repo.create_user.return_value = User(
        id=1,
        email=email,
        password_hash=f"hashed_{password}",
        nickname=nickname
    )
    
    # Act
    user, tokens = await auth_service.signup(email, password, nickname)
    
    # Assert
    assert user.email == email
    assert user.nickname == nickname
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    mock_auth_repo.find_user_by_email.assert_called_once_with(email)
    mock_auth_repo.create_user.assert_called_once()


@pytest.mark.asyncio
async def test_signup_email_already_exists(auth_service, mock_auth_repo):
    """Test signup with existing email"""
    # Arrange
    email = "existing@example.com"
    mock_auth_repo.find_user_by_email.return_value = User(id=1, email=email)
    
    # Act & Assert
    with pytest.raises(ValueError, match="Email already registered"):
        await auth_service.signup(email, "password123", "User")


@pytest.mark.asyncio
@patch('app.application.services.auth_service.verify_password')
async def test_login_success(mock_verify, auth_service, mock_auth_repo):
    """Test successful login"""
    # Arrange
    email = "test@example.com"
    password = "password123"
    
    mock_verify.return_value = True
    
    user = User(
        id=1,
        email=email,
        password_hash=f"hashed_{password}",
        nickname="TestUser"
    )
    mock_auth_repo.find_user_by_email.return_value = user
    
    # Act
    result = await auth_service.login(email, password)
    
    # Assert
    assert "access_token" in result
    assert "refresh_token" in result
    assert result["user"]["email"] == email
    mock_auth_repo.find_user_by_email.assert_called_once_with(email)


@pytest.mark.asyncio
async def test_login_invalid_credentials(auth_service, mock_auth_repo):
    """Test login with invalid credentials"""
    # Arrange
    mock_auth_repo.find_user_by_email.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid credentials"):
        await auth_service.login("test@example.com", "wrong_password")


@pytest.mark.asyncio
async def test_refresh_token_success(auth_service, mock_auth_repo):
    """Test successful token refresh"""
    # Arrange
    user = User(id=1, email="test@example.com", nickname="TestUser")
    mock_auth_repo.find_user_by_id.return_value = user
    
    # Create a real refresh token for testing
    from app.application.factories.token_factory import TokenFactory
    token_factory = TokenFactory()
    real_token = token_factory.create_tokens(1, "test@example.com").refresh_token
    
    # Act
    result = await auth_service.refresh_token(real_token)
    
    # Assert
    assert "access_token" in result
    assert "token_type" in result
    mock_auth_repo.find_user_by_id.assert_called_once()


@pytest.mark.asyncio
@patch('app.application.services.auth_service.verify_password')
@patch('app.application.services.auth_service.hash_password')
async def test_change_password_success(mock_hash, mock_verify, auth_service, mock_auth_repo):
    """Test successful password change"""
    # Arrange
    mock_verify.return_value = True
    mock_hash.return_value = "hashed_new_password"
    
    user = User(
        id=1,
        email="test@example.com",
        password_hash="hashed_old_password",
        nickname="TestUser"
    )
    mock_auth_repo.find_user_by_id.return_value = user
    mock_auth_repo.update_user.return_value = user
    
    # Act
    await auth_service.change_password(1, "old_password", "new_password123")
    
    # Assert
    mock_auth_repo.find_user_by_id.assert_called_once_with(1)
    mock_auth_repo.update_user.assert_called_once()


@pytest.mark.asyncio
@patch('app.application.services.auth_service.verify_password')
async def test_change_password_invalid_old_password(mock_verify, auth_service, mock_auth_repo):
    """Test password change with invalid old password"""
    # Arrange
    mock_verify.return_value = False
    
    user = User(
        id=1,
        email="test@example.com",
        password_hash="hashed_correct_password",
        nickname="TestUser"
    )
    mock_auth_repo.find_user_by_id.return_value = user
    
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid password"):
        await auth_service.change_password(1, "wrong_password", "new_password123")

