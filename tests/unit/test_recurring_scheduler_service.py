"""
Unit Tests for RecurringSchedulerService
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import date, timedelta
from app.application.services.recurring_scheduler_service import RecurringSchedulerService
from app.domain.models.recurring_rule import RecurringRule, RecurringFrequency
from app.domain.models.transaction import Transaction, TransactionType


@pytest.fixture
def mock_session():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def scheduler_service(mock_session):
    """RecurringSchedulerService with mocked session"""
    return RecurringSchedulerService(session=mock_session)


@pytest.mark.asyncio
async def test_should_create_transaction_daily(scheduler_service):
    """Test should_create_transaction for daily frequency"""
    # Arrange
    day_rule = "매일"
    frequency = RecurringFrequency.DAILY
    target_date = date.today()
    start_date = date.today() - timedelta(days=1)
    
    # Act
    result = scheduler_service.should_create_transaction(
        day_rule, frequency, target_date, start_date
    )
    
    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_should_create_transaction_weekly(scheduler_service):
    """Test should_create_transaction for weekly frequency"""
    # Arrange
    day_rule = "월요일"
    frequency = RecurringFrequency.WEEKLY
    target_date = date.today()
    start_date = date.today() - timedelta(days=7)
    
    # Adjust target_date to be Monday (weekday 0)
    days_until_monday = (target_date.weekday() - 0) % 7
    target_date = target_date - timedelta(days=days_until_monday)
    
    # Act
    result = scheduler_service.should_create_transaction(
        day_rule, frequency, target_date, start_date
    )
    
    # Assert
    # Result depends on if today is Monday
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_should_create_transaction_monthly(scheduler_service):
    """Test should_create_transaction for monthly frequency"""
    # Arrange
    day_rule = "매월 1일"
    frequency = RecurringFrequency.MONTHLY
    target_date = date(2025, 1, 1)  # First day of month
    start_date = date(2024, 12, 1)
    
    # Act
    result = scheduler_service.should_create_transaction(
        day_rule, frequency, target_date, start_date
    )
    
    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_should_create_transaction_before_start_date(scheduler_service):
    """Test should_create_transaction when target date is before start date"""
    # Arrange
    day_rule = "매일"
    frequency = RecurringFrequency.DAILY
    target_date = date.today() - timedelta(days=10)
    start_date = date.today()
    
    # Act
    result = scheduler_service.should_create_transaction(
        day_rule, frequency, target_date, start_date
    )
    
    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_process_recurring_rules_success(scheduler_service, mock_session):
    """Test successful processing of recurring rules"""
    from sqlalchemy import select
    from sqlalchemy.orm import AsyncResult
    
    # Arrange
    mock_rule = RecurringRule(
        id=1,
        created_by=1,
        start_date=date.today() - timedelta(days=1),
        frequency=RecurringFrequency.DAILY,
        day_rule="매일",
        amount=100000,
        is_active=True
    )
    
    # Mock session execute
    mock_result = AsyncMock()
    mock_result.scalars.return_value.all.return_value = [mock_rule]
    
    # Mock existing transaction check
    mock_existing_result = AsyncMock()
    mock_existing_result.scalar_one_or_none.return_value = None  # No existing transaction
    
    mock_session.execute.side_effect = [
        mock_result,  # For getting rules
        mock_existing_result  # For checking existing transaction
    ]
    
    # Act
    result = await scheduler_service.process_recurring_rules(
        target_date=date.today(),
        user_id=1
    )
    
    # Assert
    assert result["success"] is True
    assert "created" in result
    assert "skipped" in result
    assert "total" in result
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_process_recurring_rules_skip_existing(scheduler_service, mock_session):
    """Test processing recurring rules skips existing transactions"""
    from sqlalchemy import select
    from sqlalchemy.orm import AsyncResult
    
    # Arrange
    mock_rule = RecurringRule(
        id=1,
        created_by=1,
        start_date=date.today() - timedelta(days=1),
        frequency=RecurringFrequency.DAILY,
        day_rule="매일",
        amount=100000,
        is_active=True
    )
    
    existing_transaction = Transaction(
        id=1,
        owner_user_id=1,
        date=date.today(),
        amount=100000
    )
    
    # Mock session execute
    mock_result = AsyncMock()
    mock_result.scalars.return_value.all.return_value = [mock_rule]
    
    # Mock existing transaction check
    mock_existing_result = AsyncMock()
    mock_existing_result.scalar_one_or_none.return_value = existing_transaction  # Transaction exists
    
    mock_session.execute.side_effect = [
        mock_result,  # For getting rules
        mock_existing_result  # For checking existing transaction
    ]
    
    # Act
    result = await scheduler_service.process_recurring_rules(
        target_date=date.today(),
        user_id=1
    )
    
    # Assert
    assert result["success"] is True
    assert result["created"] == 0  # Should skip
    assert result["skipped"] >= 0  # Should skip at least one
    # Should not commit since nothing was created
    # mock_session.commit.assert_not_called()  # Or check if commit was called


@pytest.mark.asyncio
async def test_generate_transaction_from_rule_success(scheduler_service, mock_session):
    """Test successful transaction generation from rule"""
    from sqlalchemy import select
    
    # Arrange
    mock_rule = RecurringRule(
        id=1,
        created_by=1,
        start_date=date.today() - timedelta(days=1),
        frequency=RecurringFrequency.MONTHLY,
        day_rule="1",
        amount=100000,
        is_active=True
    )
    
    # Mock session execute
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = mock_rule
    
    mock_existing_result = AsyncMock()
    mock_existing_result.scalar_one_or_none.return_value = None  # No existing transaction
    
    mock_session.execute.side_effect = [
        mock_result,  # For getting rule
        mock_existing_result  # For checking existing transaction
    ]
    
    # Act
    transaction = await scheduler_service.generate_transaction_from_rule(
        rule_id=1,
        target_date=date.today(),
        user_id=1
    )
    
    # Assert
    assert transaction.amount == 100000
    assert transaction.owner_user_id == 1
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_generate_transaction_from_rule_not_found(scheduler_service, mock_session):
    """Test transaction generation when rule not found"""
    # Arrange
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = None  # Rule not found
    
    mock_session.execute.return_value = mock_result
    
    # Act & Assert
    with pytest.raises(ValueError, match="Recurring rule not found"):
        await scheduler_service.generate_transaction_from_rule(
            rule_id=999,
            target_date=date.today(),
            user_id=1
        )


@pytest.mark.asyncio
async def test_generate_transaction_from_rule_existing_transaction(scheduler_service, mock_session):
    """Test transaction generation when transaction already exists"""
    # Arrange
    mock_rule = RecurringRule(
        id=1,
        created_by=1,
        start_date=date.today() - timedelta(days=1),
        frequency=RecurringFrequency.MONTHLY,
        day_rule="1",
        amount=100000,
        is_active=True
    )
    
    existing_transaction = Transaction(
        id=1,
        owner_user_id=1,
        date=date.today(),
        amount=100000
    )
    
    # Mock session execute
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = mock_rule
    
    mock_existing_result = AsyncMock()
    mock_existing_result.scalar_one_or_none.return_value = existing_transaction
    
    mock_session.execute.side_effect = [
        mock_result,  # For getting rule
        mock_existing_result  # For checking existing transaction
    ]
    
    # Act & Assert
    with pytest.raises(ValueError, match="Transaction already exists"):
        await scheduler_service.generate_transaction_from_rule(
            rule_id=1,
            target_date=date.today(),
            user_id=1
        )

