import pytest
from decimal import Decimal


@pytest.mark.asyncio
async def test_list_products_empty(test_client):
    response = await test_client.get("/api/v1/products")
    
    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_list_products_with_pagination(test_client, test_product):
    response = await test_client.get("/api/v1/products?page=1&limit=10")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == test_product.name
    assert data[0]["price"] == float(test_product.price)


@pytest.mark.asyncio
async def test_list_products_with_search(test_client, test_product):
    response = await test_client.get("/api/v1/products?search=Test")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "Test" in data[0]["name"]


@pytest.mark.asyncio
async def test_get_product_success(test_client, test_product):
    response = await test_client.get(f"/api/v1/products/{test_product.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_product.name
    assert data["description"] == test_product.description
    assert Decimal(str(data["price"])) == test_product.price


@pytest.mark.asyncio
async def test_get_product_not_found(test_client):
    response = await test_client.get("/api/v1/products/99999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_product_admin_success(test_client, test_category, admin_auth_headers):
    response = await test_client.post(
        "/api/v1/products",
        headers=admin_auth_headers,
        json={
            "name": "New Product",
            "description": "New product description",
            "price": 199.99,
            "category_id": test_category.id,
            "stock": 50
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Product"
    assert Decimal(str(data["price"])) == Decimal("199.99")


@pytest.mark.asyncio
async def test_create_product_without_auth(test_client, test_category):
    response = await test_client.post(
        "/api/v1/products",
        json={
            "name": "New Product",
            "description": "New product description",
            "price": 199.99,
            "category_id": test_category.id,
            "stock": 50
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_product_user_forbidden(test_client, test_category, user_auth_headers):
    response = await test_client.post(
        "/api/v1/products",
        headers=user_auth_headers,
        json={
            "name": "New Product",
            "description": "New product description",
            "price": 199.99,
            "category_id": test_category.id,
            "stock": 50
        }
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_product_missing_fields(test_client, admin_auth_headers):
    response = await test_client.post(
        "/api/v1/products",
        headers=admin_auth_headers,
        json={
            "name": "New Product"
        }
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_product_admin_success(test_client, test_product, admin_auth_headers):
    response = await test_client.put(
        f"/api/v1/products/{test_product.id}",
        headers=admin_auth_headers,
        json={
            "name": "Updated Product",
            "price": 149.99
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product"
    assert Decimal(str(data["price"])) == Decimal("149.99")


@pytest.mark.asyncio
async def test_update_product_not_found(test_client, admin_auth_headers):
    response = await test_client.put(
        "/api/v1/products/99999",
        headers=admin_auth_headers,
        json={"name": "Updated"}
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_admin_success(test_client, test_product, admin_auth_headers):
    response = await test_client.delete(
        f"/api/v1/products/{test_product.id}",
        headers=admin_auth_headers
    )
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_product_not_found(test_client, admin_auth_headers):
    response = await test_client.delete(
        "/api/v1/products/99999",
        headers=admin_auth_headers
    )
    
    assert response.status_code == 404
