import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post("/api/v1/users/register", json={
            "email": "user@example.com",
            "password": "password123",
            "name": "Test User",
            "phone": "1234567890"
        })
        assert response.status_code == 200
        assert response.json()["email"] == "user@example.com"

@pytest.mark.asyncio
async def test_login_user():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post("/api/v1/users/login", data={
            "username": "user@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_get_user_profile():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Login to get the token
        login_response = await client.post("/api/v1/users/login", data={
            "username": "user@example.com",
            "password": "password123"
        })
        token = login_response.json()["access_token"]
        
        # Access profile with the token
        response = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "user@example.com"
