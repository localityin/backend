import pytest
from fastapi.testclient import TestClient
from main import app

from app.core.database import db, mongo_client

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="module", autouse=True)
async def setup_and_teardown():
    # Clean up the database before and after tests
    await db["users"].delete_many({})
    await db["stores"].delete_many({})
    await db["products"].delete_many({})
    await db["orders"].delete_many({})
    await db["payments"].delete_many({})
    await db["analytics"].delete_many({})
    await db["subscription"].delete_many({})
    yield
    await mongo_client.close()
