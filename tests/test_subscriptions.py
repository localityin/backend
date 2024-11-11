import pytest
from httpx import AsyncClient
from main import app
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_create_subscription():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Create a test subscription plan
        plan = {
            "_id": "pln_testplan",
            "name": "Test Plan",
            "description": "A test subscription plan",
            "price": 100.00,
            "duration": 30,
            "features": ["Basic feature"],
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await app.db["subscriptionPlans"].insert_one(plan)

        # Login as store to create subscription
        login_response = await client.post("/api/v1/stores/login", data={
            "username": "store1@example.com",
            "password": "storepass123"
        })
        token = login_response.json()["access_token"]

        # Create subscription for the store
        response = await client.post("/api/v1/subscriptions/create", json={
            "plan_id": "pln_testplan"
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["plan_id"] == "pln_testplan"
        assert response.json()["status"] == "active"

@pytest.mark.asyncio
async def test_update_subscription():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Login as store
        login_response = await client.post("/api/v1/stores/login", data={
            "username": "store1@example.com",
            "password": "storepass123"
        })
        token = login_response.json()["access_token"]

        # Update subscription status
        response = await client.put("/api/v1/subscriptions/update", json={
            "status": "expired"
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["status"] == "expired"

@pytest.mark.asyncio
async def test_check_subscription_status():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as client:
        # Login as store
        login_response = await client.post("/api/v1/stores/login", data={
            "username": "store1@example.com",
            "password": "storepass123"
        })
        token = login_response.json()["access_token"]

        # Check subscription status
        response = await client.get("/api/v1/subscriptions/status", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert "status" in response.json()
