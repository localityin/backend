import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_search_stores():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Create a test store
        await client.post("/api/v1/stores/register", json={
            "email": "store1@example.com",
            "password": "storepass123",
            "name": "Sample Store 1",
            "phone": "1234567890",
            "description": "Sample store for testing"
        })

        # Search for the store
        response = await client.get("/api/v1/search/stores", params={"query": "Sample"})
        assert response.status_code == 200
        assert len(response.json()) > 0
        assert response.json()[0]["name"] == "Sample Store 1"

@pytest.mark.asyncio
async def test_search_products():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Login as store
        login_response = await client.post("/api/v1/stores/login", data={
            "username": "store1@example.com",
            "password": "storepass123"
        })
        token = login_response.json()["access_token"]

        # Create a product for the store
        await client.post("/api/v1/products/", json={
            "name": "Sample Product",
            "description": "Sample description",
            "category": "Test Category",
            "skus": [
                {
                    "name": "Small",
                    "price": "10.00",
                    "mrp": "12.00",
                    "unit": "kg",
                    "quantity": 1,
                    "in_stock": True,
                    "stock_count": 100
                }
            ]
        }, headers={"Authorization": f"Bearer {token}"})

        # Search for the product
        response = await client.get("/api/v1/search/products", params={"query": "Sample"})
        assert response.status_code == 200
        assert len(response.json()) > 0
        assert response.json()[0]["name"] == "Sample Product"

@pytest.mark.asyncio
async def test_nearby_stores():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Search for nearby stores with a location (latitude and longitude)
        response = await client.get("/api/v1/stores/nearby", params={"latitude": 40.7128, "longitude": -74.0060})
        assert response.status_code == 200
        assert isinstance(response.json(), list)  # Should return a list of stores
