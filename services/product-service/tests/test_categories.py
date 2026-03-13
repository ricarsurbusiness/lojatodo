import pytest


@pytest.mark.asyncio
async def test_list_categories(test_client):
    response = await test_client.get("/api/v1/categories")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_category_admin(test_client, admin_auth_headers):
    response = await test_client.post(
        "/api/v1/categories",
        headers=admin_auth_headers,
        json={
            "name": "New Category",
            "description": "Category description"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Category"


@pytest.mark.asyncio
async def test_create_category_user_forbidden(test_client, user_auth_headers):
    response = await test_client.post(
        "/api/v1/categories",
        headers=user_auth_headers,
        json={
            "name": "New Category",
            "description": "Category description"
        }
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_category_not_found(test_client):
    response = await test_client.get("/api/v1/categories/99999")
    
    assert response.status_code == 404
