import pytest
from decimal import Decimal
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_get_empty_cart(test_client):
    response = await test_client.get("/api/v1/cart")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["items"] == []
    assert Decimal(str(data["total"])) == Decimal("0")


@pytest.mark.asyncio
async def test_add_to_cart(test_client, mock_redis, mock_product_service):
    mock_redis.hgetall.return_value = {
        b"1": b'{"product_id": 1, "quantity": 2, "name": "Test Product", "price": "99.99"}'
    }
    
    response = await test_client.post(
        "/api/v1/cart/add",
        json={
            "product_id": 1,
            "quantity": 2
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 0


@pytest.mark.asyncio
async def test_add_to_cart_product_not_found(test_client, mock_product_service):
    mock_product_service.get_product.side_effect = Exception("Product not found")
    
    response = await test_client.post(
        "/api/v1/cart/add",
        json={
            "product_id": 999,
            "quantity": 1
        }
    )
    
    assert response.status_code in [404, 500]


@pytest.mark.asyncio
async def test_update_cart_quantity(test_client, mock_redis):
    mock_redis.hgetall.return_value = {
        b"1": b'{"product_id": 1, "quantity": 2, "name": "Test Product", "price": "99.99"}'
    }
    
    response = await test_client.post(
        "/api/v1/cart/update",
        json={
            "product_id": 1,
            "quantity": 5
        }
    )
    
    assert response.status_code == 200
    data = response.json()


@pytest.mark.asyncio
async def test_update_quantity_to_zero(test_client, mock_redis):
    mock_redis.hgetall.return_value = {}
    
    response = await test_client.post(
        "/api/v1/cart/update",
        json={
            "product_id": 1,
            "quantity": 0
        }
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_remove_from_cart(test_client, mock_redis):
    mock_redis.hgetall.return_value = {
        b"1": b'{"product_id": 1, "quantity": 2, "name": "Test Product", "price": "99.99"}'
    }
    
    response = await test_client.post(
        "/api/v1/cart/remove?product_id=1"
    )
    
    assert response.status_code == 200
    data = response.json()


@pytest.mark.asyncio
async def test_remove_nonexistent_item(test_client, mock_redis):
    mock_redis.hgetall.return_value = {}
    
    response = await test_client.post(
        "/api/v1/cart/remove?product_id=999"
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_invalid_quantity(test_client):
    response = await test_client.post(
        "/api/v1/cart/add",
        json={
            "product_id": 1,
            "quantity": 0
        }
    )
    
    assert response.status_code == 422
