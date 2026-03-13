import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(test_client):
    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "name": "New User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "cliente" in data["roles"]
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(test_client, test_user):
    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        }
    )
    
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_email(test_client):
    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "password123",
            "name": "Test User"
        }
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_weak_password(test_client):
    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "short",
            "name": "Test User"
        }
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(test_client, test_user):
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(test_client, test_user):
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(test_client):
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_unauthenticated(test_client):
    response = await test_client.get("/api/v1/me")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_authenticated(test_client, test_user, auth_headers):
    response = await test_client.get(
        "/api/v1/me",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name
    assert "cliente" in data["roles"]


@pytest.mark.asyncio
async def test_refresh_token(test_client, test_user):
    login_response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    refresh_token = login_response.json()["refresh_token"]
    
    response = await test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_update_profile(test_client, test_user, auth_headers):
    response = await test_client.put(
        "/api/v1/profile",
        headers=auth_headers,
        json={"name": "Updated Name"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
