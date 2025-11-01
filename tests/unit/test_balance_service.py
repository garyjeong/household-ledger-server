"""
Unit Tests for BalanceService
"""

import pytest
from unittest.mock import AsyncMock
from datetime import date
from app.application.services.balance_service import BalanceService
from app.domain.models.transaction import TransactionType


@pytest.fixture
def mock_balance_repo():
    """Mock balance repository"""
    return AsyncMock()


@pytest.fixture
def mock_session():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def balance_service(mock_balance_repo, mock_session):
    """BalanceService with mocked dependencies"""
    return BalanceService(
        balance_repository=mock_balance_repo,
        session=mock_session
    )


@pytest.mark.asyncio
async def test_calculate_balance_success(balance_service, mock_balance_repo):
    """Test successful balance calculation"""
    # Arrange
    mock_balance_repo.calculate_balance.return_value = 500000
    
    # Act
    result = await balance_service.calculate_balance(
        user_id=1,
        group_id=None
    )
    
    # Assert
    assert result == 500000
    mock_balance_repo.calculate_balance.assert_called_once()


@pytest.mark.asyncio
async def test_get_amount_by_type_income(balance_service, mock_balance_repo):
    """Test getting income amount"""
    # Arrange
    mock_balance_repo.get_amount_by_type.return_value = 1000000
    
    # Act
    result = await balance_service.get_amount_by_type(
        user_id=1,
        transaction_type=TransactionType.INCOME
    )
    
    # Assert
    assert result == 1000000
    mock_balance_repo.get_amount_by_type.assert_called_once()


@pytest.mark.asyncio
async def test_get_amount_by_type_expense(balance_service, mock_balance_repo):
    """Test getting expense amount"""
    # Arrange
    mock_balance_repo.get_amount_by_type.return_value = 500000
    
    # Act
    result = await balance_service.get_amount_by_type(
        user_id=1,
        transaction_type=TransactionType.EXPENSE
    )
    
    # Assert
    assert result == 500000
    mock_balance_repo.get_amount_by_type.assert_called_once()


@pytest.mark.asyncio
async def test_get_monthly_trend_success(balance_service, mock_balance_repo):
    """Test successful monthly trend retrieval"""
    # Arrange
    mock_trend = [
        {'month': '2025-01', 'balance': 500000, 'income': 1000000, 'expense': 500000},
        {'month': '2025-02', 'balance': 600000, 'income': 1200000, 'expense': 600000}
    ]
    
    mock_balance_repo.get_monthly_trend.return_value = mock_trend
    
    # Act
    result = await balance_service.get_monthly_trend(
        user_id=1,
        months=2
    )
    
    # Assert
    assert len(result) == 2
    assert result[0]['month'] == '2025-01'
    mock_balance_repo.get_monthly_trend.assert_called_once()


@pytest.mark.asyncio
async def test_calculate_projected_balance_success(balance_service, mock_balance_repo, mock_session):
    """Test successful projected balance calculation"""
    from app.domain.models.recurring_rule import RecurringRule, RecurringFrequency
    from sqlalchemy import select
    from sqlalchemy.orm import AsyncResult
    
    # Arrange
    mock_balance_repo.calculate_balance.return_value = 500000
    
    # Mock recurring rules
    mock_rule = RecurringRule(
        id=1,
        created_by=1,
        amount=100000,
        frequency=RecurringFrequency.MONTHLY,
        is_active=True
    )
    
    # Mock session execute
    mock_result = AsyncMock()
    mock_result.scalars.return_value.all.return_value = [mock_rule]
    mock_session.execute.return_value = mock_result
    
    # Act
    result = await balance_service.calculate_projected_balance(
        user_id=1,
        months=3
    )
    
    # Assert
    assert result == 500000 + (100000 * 3)  # Current balance + projected from recurring rules

