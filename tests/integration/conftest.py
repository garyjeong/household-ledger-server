"""
Pytest configuration for integration tests
"""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.main import app
from app.database import Base, get_session

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
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)
    
    async with async_session_maker() as session:
        yield session
    
    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def override_get_session(test_session):
    """Override get_session dependency"""
    async def _get_session():
        yield test_session
    
    app.dependency_overrides[get_session] = _get_session
    yield
    app.dependency_overrides.pop(get_session, None)


@pytest.fixture(scope="function")
async def client(override_get_session):
    """Create test HTTP client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def test_user(client, test_session, override_get_session):
    """Create a test user and return auth tokens"""
    from app.domain.models.user import User
    from app.infrastructure.security.password_hasher import hash_password
    from app.dependencies import get_current_user
    
    # Create test user
    user = User(
        email="test@example.com",
        password_hash=hash_password("password123"),
        nickname="TestUser"
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    
    # Override get_current_user to return test user
    async def _get_current_user():
        return user
    
    app.dependency_overrides[get_current_user] = _get_current_user
    
    # Login to get tokens
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    tokens = response.json()
    
    yield {
        "user": user,
        "access_token": tokens.get("access_token"),
        "refresh_token": tokens.get("refresh_token")
    }
    
    # Cleanup
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

