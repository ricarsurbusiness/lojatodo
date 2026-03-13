import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.models.product_model import Product
from app.models.category_model import Category
from app.core.security import get_password_hash
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings

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
        category = Category(name="Electronics", description="Electronic devices")
        session.add(category)
        await session.commit()
        await session.refresh(category)
    
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
async def test_category(test_db):
    async with TestingSessionLocal() as session:
        category = Category(name="Test Category", description="Test category description")
        session.add(category)
        await session.commit()
        await session.refresh(category)
    return category


@pytest_asyncio.fixture
async def test_product(test_db, test_category):
    async with TestingSessionLocal() as session:
        product = Product(
            name="Test Product",
            description="Test product description",
            price=99.99,
            category_id=test_category.id,
            stock=10
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
    return product


@pytest_asyncio.fixture
def admin_auth_headers():
    payload = {
        "sub": "1",
        "email": "admin@example.com",
        "roles": ["admin"],
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
def user_auth_headers():
    payload = {
        "sub": "2",
        "email": "user@example.com",
        "roles": ["cliente"],
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return {"Authorization": f"Bearer {token}"}
