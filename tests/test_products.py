import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_create_product():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Login as store
        login_response = await client.post("/api/v1/stores/login", data={
            "username": "store@example.com",
            "password": "storepass123"
        })
        token = login_response.json()["access_token"]

        # Create a product
        response = await client.post("/api/v1/products/", json={
            "name": "Test Product",
            "description": "A sample product",
            "category": "Category A",
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
        assert response.status_code == 200
        assert response.json()["name"] == "Test Product"
