"""
Unit Tests for TransactionService
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import date, datetime
from app.application.services.transaction_service import TransactionService
from app.domain.models.transaction import Transaction, TransactionType


@pytest.fixture
def mock_transaction_repo():
    """Mock transaction repository"""
    return AsyncMock()


@pytest.fixture
def transaction_service(mock_transaction_repo):
    """TransactionService with mocked repository"""
    return TransactionService(transaction_repository=mock_transaction_repo)


@pytest.mark.asyncio
async def test_get_transactions_success(transaction_service, mock_transaction_repo):
    """Test successful transaction retrieval"""
    # Arrange
    mock_transactions = [
        Transaction(
            id=1,
            owner_user_id=1,
            type=TransactionType.EXPENSE.value,
            date=date.today(),
            amount=10000,
            category_id=1
        ),
        Transaction(
            id=2,
            owner_user_id=1,
            type=TransactionType.INCOME.value,
            date=date.today(),
            amount=50000,
            category_id=2
        )
    ]
    
    mock_transaction_repo.find_all.return_value = mock_transactions
    mock_transaction_repo.count_total.return_value = 2
    
    # Act
    transactions, total = await transaction_service.get_transactions(
        group_id=None,
        user_id=1,
        limit=50,
        offset=0
    )
    
    # Assert
    assert len(transactions) == 2
    assert total == 2
    assert transactions[0].id == 1
    mock_transaction_repo.find_all.assert_called_once()
    mock_transaction_repo.count_total.assert_called_once()


@pytest.mark.asyncio
async def test_create_transaction_success(transaction_service, mock_transaction_repo):
    """Test successful transaction creation"""
    # Arrange
    transaction = Transaction(
        owner_user_id=1,
        type=TransactionType.EXPENSE.value,
        date=date.today(),
        amount=10000,
        category_id=1
    )
    
    mock_transaction_repo.create.return_value = transaction
    
    # Act
    result = await transaction_service.create_transaction(transaction)
    
    # Assert
    assert result.amount == 10000
    mock_transaction_repo.create.assert_called_once_with(transaction)


@pytest.mark.asyncio
async def test_create_transaction_invalid_amount(transaction_service, mock_transaction_repo):
    """Test transaction creation with invalid amount"""
    # Arrange
    transaction = Transaction(
        owner_user_id=1,
        type=TransactionType.EXPENSE.value,
        date=date.today(),
        amount=-1000,  # Invalid negative amount
        category_id=1
    )
    
    # Act & Assert
    with pytest.raises(ValueError, match="Amount must be positive"):
        await transaction_service.create_transaction(transaction)


@pytest.mark.asyncio
async def test_get_transaction_success(transaction_service, mock_transaction_repo):
    """Test successful transaction retrieval by ID"""
    # Arrange
    transaction = Transaction(
        id=1,
        owner_user_id=1,
        type=TransactionType.EXPENSE.value,
        date=date.today(),
        amount=10000,
        category_id=1
    )
    
    mock_transaction_repo.find_by_id.return_value = transaction
    
    # Act
    result = await transaction_service.get_transaction(1, 1)
    
    # Assert
    assert result.id == 1
    assert result.owner_user_id == 1
    mock_transaction_repo.find_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_transaction_not_found(transaction_service, mock_transaction_repo):
    """Test transaction retrieval when not found"""
    # Arrange
    mock_transaction_repo.find_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="Transaction not found"):
        await transaction_service.get_transaction(999, 1)


@pytest.mark.asyncio
async def test_get_transaction_unauthorized(transaction_service, mock_transaction_repo):
    """Test transaction retrieval when unauthorized"""
    # Arrange
    transaction = Transaction(
        id=1,
        owner_user_id=2,  # Different user
        type=TransactionType.EXPENSE.value,
        date=date.today(),
        amount=10000,
        category_id=1
    )
    
    mock_transaction_repo.find_by_id.return_value = transaction
    
    # Act & Assert
    with pytest.raises(ValueError, match="Unauthorized"):
        await transaction_service.get_transaction(1, 1)  # user_id=1 trying to access user_id=2's transaction


@pytest.mark.asyncio
async def test_update_transaction_success(transaction_service, mock_transaction_repo):
    """Test successful transaction update"""
    # Arrange
    transaction = Transaction(
        id=1,
        owner_user_id=1,
        type=TransactionType.EXPENSE.value,
        date=date.today(),
        amount=10000,
        category_id=1
    )
    
    updated_transaction = Transaction(
        id=1,
        owner_user_id=1,
        type=TransactionType.EXPENSE.value,
        date=date.today(),
        amount=15000,  # Updated amount
        category_id=1
    )
    
    mock_transaction_repo.find_by_id.return_value = transaction
    mock_transaction_repo.update.return_value = updated_transaction
    
    # Act
    result = await transaction_service.update_transaction(
        1,
        1,
        {"amount": 15000}
    )
    
    # Assert
    assert result.amount == 15000
    mock_transaction_repo.find_by_id.assert_called_once_with(1)
    mock_transaction_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_delete_transaction_success(transaction_service, mock_transaction_repo):
    """Test successful transaction deletion"""
    # Arrange
    transaction = Transaction(
        id=1,
        owner_user_id=1,
        type=TransactionType.EXPENSE.value,
        date=date.today(),
        amount=10000,
        category_id=1
    )
    
    mock_transaction_repo.find_by_id.return_value = transaction
    
    # Act
    await transaction_service.delete_transaction(1, 1)
    
    # Assert
    mock_transaction_repo.find_by_id.assert_called_once_with(1)
    mock_transaction_repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_transaction_not_found(transaction_service, mock_transaction_repo):
    """Test transaction deletion when not found"""
    # Arrange
    mock_transaction_repo.find_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(ValueError, match="Transaction not found"):
        await transaction_service.delete_transaction(999, 1)

