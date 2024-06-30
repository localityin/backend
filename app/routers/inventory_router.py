from fastapi import APIRouter, HTTPException
from app.services.inventory_service import add_to_inventory, get_inventory
from app.models.inventory import Inventory

router = APIRouter()


@router.post("/inventory/add", response_model=dict)
async def add_inventory_item(store_id: str, product_sku_id: str, quantity: int):
    await add_to_inventory(store_id, product_sku_id, quantity)
    return {"message": f"Added {quantity} units of product {product_sku_id} to inventory of store {store_id}"}


@router.get("/inventory/{store_id}", response_model=Inventory)
async def fetch_inventory(store_id: str):
    inventory = await get_inventory(store_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory
