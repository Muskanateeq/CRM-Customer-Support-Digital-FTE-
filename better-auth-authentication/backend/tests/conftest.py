"""
Pytest Configuration and Fixtures

Provides shared fixtures for testing:
- Database session
- Test client
- Authentication tokens
- Sample data
"""

import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.database import get_session
from src.models.user import User
from src.models.task import Task
from src.models.tag import Tag
from src.models.task_tag import TaskTag
from sqlmodel import SQLModel


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client"""

    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        id="test-user-id-123",
        email="test@example.com",
        name="Test User",
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_2(test_session: AsyncSession) -> User:
    """Create a second test user for isolation tests"""
    user = User(
        id="test-user-id-456",
        email="test2@example.com",
        name="Test User 2",
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers with mock JWT token"""
    # In real tests, you would generate a valid JWT token
    # For now, we'll mock the dependency
    return {
        "Authorization": "Bearer mock-jwt-token"
    }


@pytest_asyncio.fixture
async def test_task(test_session: AsyncSession, test_user: User) -> Task:
    """Create a test task"""
    from datetime import date, time

    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test Description",
        priority="medium",
        completed=False,
        due_date=date(2026, 12, 31),
        due_time=time(14, 0),
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def test_tag(test_session: AsyncSession, test_user: User) -> Tag:
    """Create a test tag"""
    tag = Tag(
        user_id=test_user.id,
        name="Work",
    )
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)
    return tag


@pytest_asyncio.fixture
async def completed_recurring_task(test_session: AsyncSession, test_user: User) -> Task:
    """Create a completed recurring task for testing recurrence logic"""
    from datetime import date, time

    task = Task(
        user_id=test_user.id,
        title="Recurring Task",
        description="Daily recurring task",
        priority="high",
        completed=True,
        due_date=date(2026, 2, 7),
        due_time=time(9, 0),
        recurrence_pattern={
            "type": "daily",
            "interval": 1,
        }
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)
    return task
