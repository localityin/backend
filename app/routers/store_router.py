from fastapi import APIRouter, HTTPException
from uuid import UUID

from app.services.store_service import create_store, get_store, update_store, delete_store, get_all_stores
from app.models.store import Store

router = APIRouter()


@router.post("/stores", response_model=Store)
async def add_store(store: Store):
    new_store = await create_store(store.model_dump_json(by_alias=True))
    return new_store


@router.get("/stores/{store_id}", response_model=Store)
async def fetch_store(store_id: UUID):
    store = await get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.put("/stores/{store_id}", response_model=Store)
async def modify_store(store_id: UUID, store_data: dict):
    updated_store = await update_store(store_id, store_data)
    if not updated_store:
        raise HTTPException(status_code=404, detail="Store not found")
    return updated_store


@router.delete("/stores/{store_id}", response_model=dict)
async def remove_store(store_id: UUID):
    deleted = await delete_store(store_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Store not found")
    return {"message": "Store deleted successfully"}


@router.get("/stores", response_model=list[Store])
async def list_stores():
    stores = await get_all_stores()
    return stores
