from app.core.database import db
from nanoid import generate
from app.utils.datetime import get_ist_time
from typing import Any, Dict

async def get_store_by_phone(phone: int) -> str:
    """
    Helper function to fetch the store's name based on the phone number.
    """
    store = await db.stores.find_one({"phone": str(phone)})
    if store:
        return store
    else:
        return {}
        

async def create_store_document(phone: int) -> str:
    """
    Helper function to create a new store document in the database.
    """
    store = {
        "_id": 'str_' + generate('1234567890', 8),
        "phone": str(phone),
        "createdAt": get_ist_time(),
        "active": True
    }
    result = await db.stores.insert_one(store)
    return result.inserted_id