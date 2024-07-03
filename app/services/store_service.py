from uuid import UUID

from app.models.store import Store
from app.database.mongo import store_collection


async def create_store(store_data: dict):
    store = Store(**store_data)
    await store_collection.insert_one(store.model_dump_json(by_alias=True))
    return store


async def get_store(store_id: UUID):
    store = await store_collection.find_one({"_id": store_id})
    return Store(**store) if store else None


async def update_store(store_id: UUID, store_data: dict):
    await store_collection.update_one({"_id": store_id}, {"$set": store_data})
    updated_store = await store_collection.find_one({"_id": store_id})
    return Store(**updated_store) if updated_store else None


async def delete_store(store_id: UUID):
    delete_result = await store_collection.delete_one({"_id": store_id})
    return delete_result.deleted_count > 0


async def get_all_stores():
    stores = []
    async for store in store_collection.find():
        stores.append(Store(**store))
    return stores
