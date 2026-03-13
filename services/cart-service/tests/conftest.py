import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.dependencies import get_redis, get_current_user


@pytest_asyncio.fixture
def mock_redis():
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=True)
    redis_mock.hgetall = AsyncMock(return_value={})
    redis_mock.hset = AsyncMock(return_value=True)
    redis_mock.hdel = AsyncMock(return_value=True)
    return redis_mock


@pytest_asyncio.fixture
def mock_product_service():
    with patch('app.services.product_client.ProductServiceClient') as mock:
        mock_client = AsyncMock()
        mock_client.get_product = AsyncMock(return_value={
            "id": 1,
            "name": "Test Product",
            "price": 99.99
        })
        mock.return_value = mock_client
        yield mock_client


@pytest_asyncio.fixture
async def test_client(mock_redis, mock_product_service):
    async def override_get_redis():
        yield mock_redis
    
    async def override_get_current_user():
        return MagicMock(user_id=1, email="test@example.com", roles=["cliente"])
    
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
def user_payload():
    return {"user_id": 1, "email": "test@example.com", "roles": ["cliente"]}
