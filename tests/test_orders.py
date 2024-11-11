import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_create_order():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Login as user
        login_response = await client.post("/api/v1/users/login", data={
            "username": "user@example.com",
            "password": "password123"
        })
        token = login_response.json()["access_token"]

        # Place an order
        response = await client.post("/api/v1/orders/", json={
            "store_id": "str_example_id",
            "items": [{"sku_id": "sku_example_id", "product_id": "prd_example_id", "quantity": 1, "price": "10.00"}],
            "subtotal": "10.00",
            "platform_fee": "1.00",
            "delivery_fee": "5.00",
            "total": "16.00",
            "delivery_address": {"address": "123 Street", "latitude": 0.0, "longitude": 0.0}
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["total"] == "16.00"
