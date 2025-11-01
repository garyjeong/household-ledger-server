"""
Global pytest configuration
Common fixtures available to all tests
"""

import pytest
from tests.helpers.test_data_factory import (
    create_test_user,
    create_test_transaction,
    create_test_category,
    create_test_group
)
from tests.helpers.mock_helpers import (
    create_mock_session,
    create_mock_repository
)


@pytest.fixture
def mock_db_session():
    """Global mock database session fixture"""
    return create_mock_session()


@pytest.fixture
def sample_user_data():
    """Sample user data for tests"""
    return {
        "id": 1,
        "email": "test@example.com",
        "nickname": "TestUser",
        "password": "password123"
    }


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for tests"""
    from datetime import date
    return {
        "id": 1,
        "owner_user_id": 1,
        "type": "EXPENSE",
        "date": date.today(),
        "amount": 10000,
        "category_id": 1,
        "memo": "Test transaction"
    }


@pytest.fixture
def sample_category_data():
    """Sample category data for tests"""
    return {
        "id": 1,
        "name": "식비",
        "type": "EXPENSE",
        "color": "#FF5733",
        "created_by": 1
    }


@pytest.fixture
def sample_group_data():
    """Sample group data for tests"""
    return {
        "id": 1,
        "name": "테스트 그룹",
        "owner_id": 1
    }

