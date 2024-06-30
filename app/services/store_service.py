from uuid import UUID

from app.models.store import Store
from app.database import get_database


async def create_store(store_data: dict):
    db = await get_database()
    store = Store(**store_data)
    await db["stores"].insert_one(store.model_dump_json(by_alias=True))
    return store


async def get_store(store_id: UUID):
    db = await get_database()
    store = await db["stores"].find_one({"_id": store_id})
    return Store(**store) if store else None


async def update_store(store_id: UUID, store_data: dict):
    db = await get_database()
    await db["stores"].update_one({"_id": store_id}, {"$set": store_data})
    updated_store = await db["stores"].find_one({"_id": store_id})
    return Store(**updated_store) if updated_store else None


async def delete_store(store_id: UUID):
    db = await get_database()
    delete_result = await db["stores"].delete_one({"_id": store_id})
    return delete_result.deleted_count > 0


async def get_all_stores():
    db = await get_database()
    stores = []
    async for store in db["stores"].find():
        stores.append(Store(**store))
    return stores
