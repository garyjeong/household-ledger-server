"""
Unit Tests for RecurringRuleService
"""

import pytest
from unittest.mock import AsyncMock
from datetime import date
from app.application.services.recurring_rule_service import RecurringRuleService
from app.domain.models.recurring_rule import RecurringRule, RecurringFrequency


@pytest.fixture
def mock_recurring_rule_repo():
    """Mock recurring rule repository"""
    return AsyncMock()


@pytest.fixture
def recurring_rule_service(mock_recurring_rule_repo):
    """RecurringRuleService with mocked repository"""
    return RecurringRuleService(recurring_rule_repository=mock_recurring_rule_repo)


@pytest.mark.asyncio
async def test_get_recurring_rules_success(recurring_rule_service, mock_recurring_rule_repo):
    """Test successful recurring rules retrieval"""
    # Arrange
    mock_rules = [
        RecurringRule(
            id=1,
            created_by=1,
            start_date=date.today(),
            frequency=RecurringFrequency.MONTHLY,
            amount=100000,
            is_active=True
        )
    ]
    
    mock_recurring_rule_repo.find_all.return_value = mock_rules
    
    # Act
    result = await recurring_rule_service.get_recurring_rules(
        user_id=1,
        group_id=None,
        is_active=True
    )
    
    # Assert
    assert len(result) == 1
    assert result[0].id == 1
    mock_recurring_rule_repo.find_all.assert_called_once()


@pytest.mark.asyncio
async def test_get_recurring_rule_success(recurring_rule_service, mock_recurring_rule_repo):
    """Test successful recurring rule retrieval by ID"""
    # Arrange
    rule = RecurringRule(
        id=1,
        created_by=1,
        start_date=date.today(),
        frequency=RecurringFrequency.MONTHLY,
        amount=100000,
        is_active=True
    )
    
    mock_recurring_rule_repo.find_by_id.return_value = rule
    
    # Act
    result = await recurring_rule_service.get_recurring_rule(1, 1)
    
    # Assert
    assert result.id == 1
    assert result.created_by == 1
    mock_recurring_rule_repo.find_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_recurring_rule_not_found(recurring_rule_service, mock_recurring_rule_repo):
    """Test recurring rule retrieval when not found"""
    # Arrange
    mock_recurring_rule_repo.find_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="Recurring rule not found"):
        await recurring_rule_service.get_recurring_rule(999, 1)


@pytest.mark.asyncio
async def test_get_recurring_rule_unauthorized(recurring_rule_service, mock_recurring_rule_repo):
    """Test recurring rule retrieval when unauthorized"""
    # Arrange
    rule = RecurringRule(
        id=1,
        created_by=2,  # Different user
        start_date=date.today(),
        frequency=RecurringFrequency.MONTHLY,
        amount=100000,
        is_active=True
    )
    
    mock_recurring_rule_repo.find_by_id.return_value = rule
    
    # Act & Assert
    with pytest.raises(ValueError, match="Unauthorized"):
        await recurring_rule_service.get_recurring_rule(1, 1)  # user_id=1 trying to access user_id=2's rule


@pytest.mark.asyncio
async def test_create_recurring_rule_success(recurring_rule_service, mock_recurring_rule_repo):
    """Test successful recurring rule creation"""
    # Arrange
    rule = RecurringRule(
        created_by=1,
        start_date=date.today(),
        frequency=RecurringFrequency.MONTHLY,
        day_rule="1",
        amount=100000,
        is_active=True
    )
    
    mock_recurring_rule_repo.create.return_value = rule
    
    # Act
    result = await recurring_rule_service.create_recurring_rule(rule)
    
    # Assert
    assert result.amount == 100000
    mock_recurring_rule_repo.create.assert_called_once_with(rule)


@pytest.mark.asyncio
async def test_create_recurring_rule_invalid_amount(recurring_rule_service, mock_recurring_rule_repo):
    """Test recurring rule creation with invalid amount"""
    # Arrange
    rule = RecurringRule(
        created_by=1,
        start_date=date.today(),
        frequency=RecurringFrequency.MONTHLY,
        day_rule="1",
        amount=-1000,  # Invalid negative amount
        is_active=True
    )
    
    # Act & Assert
    with pytest.raises(ValueError, match="Amount must be positive"):
        await recurring_rule_service.create_recurring_rule(rule)


@pytest.mark.asyncio
async def test_update_recurring_rule_success(recurring_rule_service, mock_recurring_rule_repo):
    """Test successful recurring rule update"""
    # Arrange
    rule = RecurringRule(
        id=1,
        created_by=1,
        start_date=date.today(),
        frequency=RecurringFrequency.MONTHLY,
        amount=100000,
        is_active=True
    )
    
    updated_rule = RecurringRule(
        id=1,
        created_by=1,
        start_date=date.today(),
        frequency=RecurringFrequency.MONTHLY,
        amount=150000,  # Updated amount
        is_active=True
    )
    
    mock_recurring_rule_repo.find_by_id.return_value = rule
    mock_recurring_rule_repo.update.return_value = updated_rule
    
    # Act
    result = await recurring_rule_service.update_recurring_rule(
        1,
        1,
        {"amount": 150000}
    )
    
    # Assert
    assert result.amount == 150000
    mock_recurring_rule_repo.find_by_id.assert_called_once_with(1)
    mock_recurring_rule_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_delete_recurring_rule_success(recurring_rule_service, mock_recurring_rule_repo):
    """Test successful recurring rule deletion"""
    # Arrange
    rule = RecurringRule(
        id=1,
        created_by=1,
        start_date=date.today(),
        frequency=RecurringFrequency.MONTHLY,
        amount=100000,
        is_active=True
    )
    
    mock_recurring_rule_repo.find_by_id.return_value = rule
    
    # Act
    await recurring_rule_service.delete_recurring_rule(1, 1)
    
    # Assert
    mock_recurring_rule_repo.find_by_id.assert_called_once_with(1)
    mock_recurring_rule_repo.delete.assert_called_once_with(1)

