from uuid import UUID

from app.models.user import User
from app.database.mongo import user_collection


async def create_user(user_data: dict):
    user = User(**user_data)
    await user_collection.insert_one(user.model_dump_json(by_alias=True))
    return user


async def get_user(user_id: UUID):
    user = await user_collection.find_one({"_id": user_id})
    return User(**user) if user else None


async def update_user(user_id: UUID, user_data: dict):
    await user_collection.update_one({"_id": user_id}, {"$set": user_data})
    updated_user = await user_collection.find_one({"_id": user_id})
    return User(**updated_user) if updated_user else None


async def delete_user(user_id: UUID):
    delete_result = await user_collection.delete_one({"_id": user_id})
    return delete_result.deleted_count > 0


async def get_all_users():
    users = []
    async for user in user_collection.find():
        users.append(User(**user))
    return users
