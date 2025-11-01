"""
Fixture Helpers
Additional fixtures for test data setup
"""

import pytest
from datetime import date, datetime
from typing import Optional
from app.domain.models.user import User
from app.domain.models.transaction import Transaction, TransactionType
from app.domain.models.category import Category
from app.domain.models.group import Group
from app.infrastructure.security.password_hasher import hash_password
from tests.helpers.test_data_factory import (
    create_test_user,
    create_test_transaction,
    create_test_category,
    create_test_group,
    create_test_users,
    create_test_transactions,
    create_test_categories
)


@pytest.fixture
def sample_user() -> User:
    """Fixture for a sample user"""
    return create_test_user(
        user_id=1,
        email="sample@example.com",
        nickname="SampleUser"
    )


@pytest.fixture
def sample_users() -> list[User]:
    """Fixture for multiple sample users"""
    return create_test_users(count=3)


@pytest.fixture
def sample_transaction() -> Transaction:
    """Fixture for a sample transaction"""
    return create_test_transaction(
        transaction_id=1,
        owner_user_id=1,
        amount=10000,
        memo="Sample transaction"
    )


@pytest.fixture
def sample_transactions() -> list[Transaction]:
    """Fixture for multiple sample transactions"""
    return create_test_transactions(count=5, owner_user_id=1)


@pytest.fixture
def sample_category() -> Category:
    """Fixture for a sample category"""
    return create_test_category(
        category_id=1,
        name="식비",
        category_type="EXPENSE"
    )


@pytest.fixture
def sample_categories() -> list[Category]:
    """Fixture for multiple sample categories"""
    return create_test_categories(count=5)


@pytest.fixture
def sample_group() -> Group:
    """Fixture for a sample group"""
    return create_test_group(
        group_id=1,
        name="Sample Group",
        owner_id=1
    )


@pytest.fixture
def authenticated_user_data() -> dict:
    """Fixture for authenticated user data"""
    return {
        "id": 1,
        "email": "test@example.com",
        "nickname": "TestUser",
        "group_id": None
    }


@pytest.fixture
def jwt_token_data() -> dict:
    """Fixture for JWT token data"""
    return {
        "sub": "1",
        "email": "test@example.com",
        "type": "access"
    }


@pytest.fixture
def transaction_request_data() -> dict:
    """Fixture for transaction request data"""
    return {
        "type": "EXPENSE",
        "date": str(date.today()),
        "amount": 10000,
        "category_id": 1,
        "memo": "Test transaction"
    }


@pytest.fixture
def category_request_data() -> dict:
    """Fixture for category request data"""
    return {
        "name": "식비",
        "type": "EXPENSE",
        "color": "#FF5733",
        "icon": "🍔"
    }


@pytest.fixture
def group_request_data() -> dict:
    """Fixture for group request data"""
    return {
        "name": "테스트 그룹",
        "description": "테스트용 그룹"
    }


@pytest.fixture
def budget_request_data() -> dict:
    """Fixture for budget request data"""
    return {
        "owner_type": "USER",
        "period": "2025-01",
        "total_amount": 1000000,
        "status": "ACTIVE"
    }


@pytest.fixture
def settings_request_data() -> dict:
    """Fixture for settings request data"""
    return {
        "currency": "KRW",
        "theme": "light",
        "language": "ko",
        "enable_notifications": True,
        "budget_alerts": True
    }


@pytest.fixture
def recurring_rule_request_data() -> dict:
    """Fixture for recurring rule request data"""
    return {
        "start_date": str(date.today()),
        "frequency": "MONTHLY",
        "day_rule": "1",
        "amount": 100000,
        "category_id": 1,
        "memo": "Monthly expense"
    }

