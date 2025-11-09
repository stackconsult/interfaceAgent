"""
Test configuration and fixtures.
"""
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import Base
from app.models import User, Role, Agent
from app.core.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_superuser(db_session: AsyncSession) -> User:
    """Create a test superuser."""
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_role(db_session: AsyncSession) -> Role:
    """Create a test role."""
    role = Role(
        name="test_role",
        description="Test role for testing",
    )
    db_session.add(role)
    await db_session.commit()
    await db_session.refresh(role)
    return role


@pytest.fixture
async def test_agent(db_session: AsyncSession) -> Agent:
    """Create a test agent."""
    from app.models.agent import AgentType, AgentStatus
    
    agent = Agent(
        name="test_agent",
        description="Test agent for testing",
        agent_type=AgentType.VALIDATOR,
        status=AgentStatus.ACTIVE,
        config={},
        version="1.0.0",
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    return agent
