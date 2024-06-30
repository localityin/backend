from uuid import UUID

from app.models.user import User
from app.database import get_database


async def create_user(user_data: dict):
    db = await get_database()
    user = User(**user_data)
    await db["users"].insert_one(user.model_dump_json(by_alias=True))
    return user


async def get_user(user_id: UUID):
    db = await get_database()
    user = await db["users"].find_one({"_id": user_id})
    return User(**user) if user else None


async def update_user(user_id: UUID, user_data: dict):
    db = await get_database()
    await db["users"].update_one({"_id": user_id}, {"$set": user_data})
    updated_user = await db["users"].find_one({"_id": user_id})
    return User(**updated_user) if updated_user else None


async def delete_user(user_id: UUID):
    db = await get_database()
    delete_result = await db["users"].delete_one({"_id": user_id})
    return delete_result.deleted_count > 0


async def get_all_users():
    db = await get_database()
    users = []
    async for user in db["users"].find():
        users.append(User(**user))
    return users
