"""
Unit Tests for GroupService
"""

import pytest
from unittest.mock import AsyncMock
from app.application.services.group_service import GroupService
from app.domain.models.group import Group


@pytest.fixture
def mock_group_repo():
    """Mock group repository"""
    return AsyncMock()


@pytest.fixture
def group_service(mock_group_repo):
    """GroupService with mocked repository"""
    return GroupService(group_repository=mock_group_repo)


@pytest.mark.asyncio
async def test_get_user_groups_success(group_service, mock_group_repo):
    """Test successful user groups retrieval"""
    # Arrange
    mock_groups = [
        Group(id=1, name="My Group", owner_id=1),
        Group(id=2, name="Another Group", owner_id=1)
    ]
    
    mock_group_repo.find_user_groups.return_value = mock_groups
    
    # Act
    result = await group_service.get_user_groups(1)
    
    # Assert
    assert len(result) == 2
    assert result[0].name == "My Group"
    mock_group_repo.find_user_groups.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_create_group_success(group_service, mock_group_repo):
    """Test successful group creation"""
    # Arrange
    group = Group(
        name="New Group",
        owner_id=1
    )
    
    mock_group_repo.create.return_value = group
    
    # Act
    result = await group_service.create_group(group)
    
    # Assert
    assert result.name == "New Group"
    mock_group_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_group_success(group_service, mock_group_repo):
    """Test successful group retrieval by ID"""
    # Arrange
    group = Group(id=1, name="My Group", owner_id=1)
    mock_group_repo.find_by_id.return_value = group
    
    # Act
    result = await group_service.get_group(1, 1)
    
    # Assert
    assert result.id == 1
    assert result.name == "My Group"
    mock_group_repo.find_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_group_not_found(group_service, mock_group_repo):
    """Test group retrieval when not found"""
    # Arrange
    mock_group_repo.find_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="Group not found"):
        await group_service.get_group(999, 1)


@pytest.mark.asyncio
async def test_update_group_success(group_service, mock_group_repo):
    """Test successful group update"""
    # Arrange
    group = Group(id=1, name="My Group", owner_id=1)
    updated_group = Group(id=1, name="Updated Group", owner_id=1)
    
    mock_group_repo.find_by_id.return_value = group
    mock_group_repo.update.return_value = updated_group
    
    # Act
    result = await group_service.update_group(1, 1, {"name": "Updated Group"})
    
    # Assert
    assert result.name == "Updated Group"
    mock_group_repo.find_by_id.assert_called_once_with(1)
    mock_group_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_delete_group_success(group_service, mock_group_repo):
    """Test successful group deletion"""
    # Arrange
    group = Group(id=1, name="My Group", owner_id=1)
    mock_group_repo.find_by_id.return_value = group
    
    # Act
    await group_service.delete_group(1, 1)
    
    # Assert
    mock_group_repo.find_by_id.assert_called_once_with(1)
    mock_group_repo.delete.assert_called_once_with(1)

