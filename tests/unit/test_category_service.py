"""
Unit Tests for CategoryService
"""

import pytest
from unittest.mock import AsyncMock
from app.application.services.category_service import CategoryService
from app.domain.models.category import Category


@pytest.fixture
def mock_category_repo():
    """Mock category repository"""
    return AsyncMock()


@pytest.fixture
def category_service(mock_category_repo):
    """CategoryService with mocked repository"""
    return CategoryService(category_repository=mock_category_repo)


@pytest.mark.asyncio
async def test_get_categories_success(category_service, mock_category_repo):
    """Test successful category retrieval"""
    # Arrange
    mock_categories = [
        Category(id=1, name="식비", type="EXPENSE", created_by=1),
        Category(id=2, name="교통비", type="EXPENSE", created_by=1)
    ]
    
    mock_category_repo.find_all.return_value = mock_categories
    
    # Act
    result = await category_service.get_categories(group_id=1, type="EXPENSE")
    
    # Assert
    assert len(result) == 2
    assert result[0].name == "식비"
    mock_category_repo.find_all.assert_called_once()


@pytest.mark.asyncio
async def test_create_category_success(category_service, mock_category_repo):
    """Test successful category creation"""
    # Arrange
    category = Category(
        name="새 카테고리",
        type="EXPENSE",
        group_id=1,
        created_by=1
    )
    
    mock_category_repo.create.return_value = category
    
    # Act
    result = await category_service.create_category(category)
    
    # Assert
    assert result.name == "새 카테고리"
    mock_category_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_get_category_success(category_service, mock_category_repo):
    """Test successful category retrieval by ID"""
    # Arrange
    category = Category(id=1, name="식비", type="EXPENSE", created_by=1)
    mock_category_repo.find_by_id.return_value = category
    
    # Act
    result = await category_service.get_category(1, 1)
    
    # Assert
    assert result.id == 1
    assert result.name == "식비"
    mock_category_repo.find_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_category_not_found(category_service, mock_category_repo):
    """Test category retrieval when not found"""
    # Arrange
    mock_category_repo.find_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="Category not found"):
        await category_service.get_category(999, 1)


@pytest.mark.asyncio
async def test_update_category_success(category_service, mock_category_repo):
    """Test successful category update"""
    # Arrange
    category = Category(id=1, name="식비", type="EXPENSE", created_by=1)
    updated_category = Category(id=1, name="식비 (수정)", type="EXPENSE", created_by=1)
    
    mock_category_repo.find_by_id.return_value = category
    mock_category_repo.update.return_value = updated_category
    
    # Act
    result = await category_service.update_category(1, 1, {"name": "식비 (수정)"})
    
    # Assert
    assert result.name == "식비 (수정)"
    mock_category_repo.find_by_id.assert_called_once_with(1)
    mock_category_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_delete_category_success(category_service, mock_category_repo):
    """Test successful category deletion"""
    # Arrange
    category = Category(id=1, name="식비", type="EXPENSE", created_by=1)
    mock_category_repo.find_by_id.return_value = category
    
    # Act
    await category_service.delete_category(1, 1)
    
    # Assert
    mock_category_repo.find_by_id.assert_called_once_with(1)
    mock_category_repo.delete.assert_called_once_with(1)

