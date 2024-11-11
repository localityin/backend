import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_register_store():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post("/api/v1/stores/register", json={
            "email": "store@example.com",
            "password": "storepass123",
            "name": "Test Store",
            "phone": "0987654321",
            "description": "A test store description"
        })
        assert response.status_code == 200
        assert response.json()["email"] == "store@example.com"

@pytest.mark.asyncio
async def test_login_store():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        response = await client.post("/api/v1/stores/login", data={
            "username": "store@example.com",
            "password": "storepass123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_get_store_profile():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Login to get the token
        login_response = await client.post("/api/v1/stores/login", data={
            "username": "store@example.com",
            "password": "storepass123"
        })
        token = login_response.json()["access_token"]

        # Access profile with the token
        response = await client.get("/api/v1/stores/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "store@example.com"
