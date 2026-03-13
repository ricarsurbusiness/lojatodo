import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.models.user_model import User
from app.models.role_model import Role
from app.core.security import get_password_hash
from jose import jwt
from datetime import datetime, timedelta

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        cliente_role = Role(name="cliente", description="Customer role")
        admin_role = Role(name="admin", description="Admin role")
        superadmin_role = Role(name="superAdmin", description="Super Admin role")
        
        session.add_all([cliente_role, admin_role, superadmin_role])
        await session.commit()
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_client(test_db):
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_db):
    async with TestingSessionLocal() as session:
        user = User(
            email="test@example.com",
            name="Test User",
            password_hash=get_password_hash("password123")
        )
        cliente_role = Role(name="cliente")
        user.roles.append(cliente_role)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin_user(test_db):
    async with TestingSessionLocal() as session:
        user = User(
            email="admin@example.com",
            name="Admin User",
            password_hash=get_password_hash("admin123")
        )
        admin_role = Role(name="admin")
        user.roles.append(admin_role)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


@pytest_asyncio.fixture
def auth_headers(test_user):
    from app.core.config import settings
    payload = {
        "sub": str(test_user.id),
        "email": test_user.email,
        "roles": [role.name for role in test_user.roles],
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return {"Authorization": f"Bearer {token}"}
