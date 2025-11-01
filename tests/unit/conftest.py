"""
Pytest configuration for unit tests
"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from tests.helpers.test_data_factory import (
    create_test_user,
    create_test_transaction,
    create_test_category,
    create_test_group
)
from tests.helpers.mock_helpers import (
    create_mock_session,
    create_mock_repository,
    create_mock_statistics_repository,
    create_mock_balance_repository,
    create_mock_auth_repository,
    create_mock_transaction_repository,
    create_mock_category_repository,
    create_mock_group_repository,
    create_mock_budget_repository,
    create_mock_recurring_rule_repository
)

# Test database URL (in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine):
    """Create test database session"""
    from app.database import Base
    
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(test_engine)
    async with async_session_maker() as session:
        yield session
    
    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock repository fixtures
@pytest.fixture
def mock_auth_repo():
    """Mock auth repository"""
    return create_mock_auth_repository()


@pytest.fixture
def mock_transaction_repo():
    """Mock transaction repository"""
    return create_mock_transaction_repository()


@pytest.fixture
def mock_category_repo():
    """Mock category repository"""
    return create_mock_category_repository()


@pytest.fixture
def mock_group_repo():
    """Mock group repository"""
    return create_mock_group_repository()


@pytest.fixture
def mock_budget_repo():
    """Mock budget repository"""
    return create_mock_budget_repository()


@pytest.fixture
def mock_statistics_repo():
    """Mock statistics repository"""
    return create_mock_statistics_repository()


@pytest.fixture
def mock_balance_repo():
    """Mock balance repository"""
    return create_mock_balance_repository()


@pytest.fixture
def mock_recurring_rule_repo():
    """Mock recurring rule repository"""
    return create_mock_recurring_rule_repository()


# Test data fixtures
@pytest.fixture
def test_user_model():
    """Test user model instance"""
    return create_test_user(user_id=1)


@pytest.fixture
def test_transaction_model():
    """Test transaction model instance"""
    return create_test_transaction(transaction_id=1, owner_user_id=1)


@pytest.fixture
def test_category_model():
    """Test category model instance"""
    return create_test_category(category_id=1)


@pytest.fixture
def test_group_model():
    """Test group model instance"""
    return create_test_group(group_id=1)

