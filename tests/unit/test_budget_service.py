"""
Unit Tests for BudgetService
"""

import pytest
from unittest.mock import AsyncMock
from datetime import date
from app.application.services.budget_service import BudgetService
from app.domain.models.budget import Budget, OwnerType, BudgetStatus


@pytest.fixture
def mock_budget_repo():
    """Mock budget repository"""
    return AsyncMock()


@pytest.fixture
def mock_statistics_repo():
    """Mock statistics repository"""
    return AsyncMock()


@pytest.fixture
def mock_session():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def budget_service(mock_budget_repo, mock_statistics_repo, mock_session):
    """BudgetService with mocked dependencies"""
    return BudgetService(
        budget_repository=mock_budget_repo,
        statistics_repository=mock_statistics_repo,
        session=mock_session
    )


@pytest.mark.asyncio
async def test_get_budgets_success(budget_service, mock_budget_repo):
    """Test successful budget retrieval"""
    # Arrange
    mock_budgets = [
        Budget(
            id=1,
            owner_type=OwnerType.USER,
            owner_id=1,
            period="2025-01",
            total_amount=1000000,
            status=BudgetStatus.ACTIVE
        )
    ]
    
    mock_budget_repo.find_all.return_value = mock_budgets
    
    # Act
    result = await budget_service.get_budgets(
        owner_type=OwnerType.USER,
        owner_id=1
    )
    
    # Assert
    assert len(result) == 1
    assert result[0].period == "2025-01"
    mock_budget_repo.find_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_budget_success(budget_service, mock_budget_repo):
    """Test successful budget retrieval by ID"""
    # Arrange
    budget = Budget(
        id=1,
        owner_type=OwnerType.USER,
        owner_id=1,
        period="2025-01",
        total_amount=1000000,
        status=BudgetStatus.ACTIVE
    )
    
    mock_budget_repo.find_by_id.return_value = budget
    
    # Act
    result = await budget_service.get_budget(1, OwnerType.USER, 1)
    
    # Assert
    assert result.id == 1
    assert result.period == "2025-01"
    mock_budget_repo.find_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_budget_not_found(budget_service, mock_budget_repo):
    """Test budget retrieval when not found"""
    # Arrange
    mock_budget_repo.find_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="Budget not found"):
        await budget_service.get_budget(999, OwnerType.USER, 1)


@pytest.mark.asyncio
async def test_create_or_update_budget_new(budget_service, mock_budget_repo):
    """Test successful budget creation"""
    # Arrange
    budget = Budget(
        id=1,
        owner_type=OwnerType.USER,
        owner_id=1,
        period="2025-01",
        total_amount=1000000,
        status=BudgetStatus.ACTIVE
    )
    
    mock_budget_repo.find_by_period.return_value = None
    mock_budget_repo.create.return_value = budget
    
    # Act
    result = await budget_service.create_or_update_budget(
        owner_type=OwnerType.USER,
        owner_id=1,
        period="2025-01",
        total_amount=1000000
    )
    
    # Assert
    assert result.period == "2025-01"
    mock_budget_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_or_update_budget_existing(budget_service, mock_budget_repo):
    """Test successful budget update when exists"""
    # Arrange
    existing_budget = Budget(
        id=1,
        owner_type=OwnerType.USER,
        owner_id=1,
        period="2025-01",
        total_amount=1000000,
        status=BudgetStatus.ACTIVE
    )
    
    updated_budget = Budget(
        id=1,
        owner_type=OwnerType.USER,
        owner_id=1,
        period="2025-01",
        total_amount=1500000,  # Updated amount
        status=BudgetStatus.ACTIVE
    )
    
    mock_budget_repo.find_by_period.return_value = existing_budget
    mock_budget_repo.update.return_value = updated_budget
    
    # Act
    result = await budget_service.create_or_update_budget(
        owner_type=OwnerType.USER,
        owner_id=1,
        period="2025-01",
        total_amount=1500000
    )
    
    # Assert
    assert result.total_amount == 1500000
    mock_budget_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_get_budget_status_success(budget_service, mock_budget_repo, mock_statistics_repo):
    """Test successful budget status retrieval"""
    # Arrange
    budget = Budget(
        id=1,
        owner_type=OwnerType.USER,
        owner_id=1,
        period="2025-01",
        total_amount=1000000,
        status=BudgetStatus.ACTIVE
    )
    
    mock_budget_repo.find_by_period.return_value = budget
    mock_statistics_repo.get_summary_statistics.return_value = {
        'total_expense': 600000,
        'total_income': 0
    }
    
    # Act
    result = await budget_service.get_budget_status(
        owner_type=OwnerType.USER,
        owner_id=1,
        period="2025-01"
    )
    
    # Assert
    assert 'total_budget' in result
    assert 'total_spent' in result
    assert 'remaining_budget' in result
    assert result['total_budget'] == 1000000
    assert result['total_spent'] == 600000

