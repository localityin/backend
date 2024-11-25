from app.core.database import db
from nanoid import generate
from app.utils.datetime import get_ist_time
from typing import Any, Dict

async def get_user_by_phone(phone: int) -> str:
    """
    Helper function to fetch the user's name based on the phone number.
    """
    user = await db.users.find_one({"phone": str(phone)})
    if user:
        return user
    else:
        return {}
    
async def create_user_document(phone: int) -> str:
    """
    Helper function to create a new user document in the database.
    """
    user = {
        "_id": 'usr_' + generate('1234567890', 8),
        "phone": str(phone),
        "createdAt": get_ist_time(),
        "active": True
    }
    result = await db.users.insert_one(user)
    return result.inserted_id

async def update_user_name(phone: int, name: str) -> str:
    """
    Helper function to update the user's name based on the phone number.
    """
    result = await db.users.update_one({"phone": str(phone)}, {"$set": {"name": name}})
    return result.modified_count

async def update_user_address(phone: int, address: Dict[str, Any]) -> str:
    """
    Helper function to update the user's address based on the phone number.
    """
    result = await db.users.update_one({"phone": str(phone)}, {"$set": {"address": address}})
    return result.modified_count

async def get_user_address(phone: int) -> str:
    """
    Helper function to fetch the user's address based on the phone number.
    """
    user = await db.users.find_one({"phone": str(phone)})
    if user:
        return user.get("address")
    else:
        return {}