from app.models.inventory import InventoryCreate, InventoryResponse, UpdateInventory, InventoryUpdateResponse
from app.utils.security import get_current_store
from fastapi import APIRouter, HTTPException, Depends, status
from app.utils.security import get_current_store
from app.core.database import db
from nanoid import generate
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/", response_model=InventoryResponse)
async def create_inventory(inventory: InventoryCreate, current_store: dict = Depends(get_current_store)):
    inventory_id = f"inv_{generate(size=10)}"
    items = [
        {**item.dict(), "_id": f"item_{generate(size=10)}"}
        for item in inventory.items
    ]
    inventory_data = inventory.dict()
    inventory_data.update({
        "_id": inventory_id,
        "store_id": current_store["_id"],
        "items": items,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    await db["inventory"].insert_one(inventory_data)
    return InventoryResponse(**inventory_data)

@router.get("/", response_model=List[InventoryResponse])
async def get_inventory(current_store: dict = Depends(get_current_store)):
    inventory = await db["inventory"].find({"store_id": current_store["_id"]}).to_list(100)
    return [InventoryResponse(**item) for item in inventory]

@router.get("/{inventory_id}", response_model=InventoryResponse)
async def get_inventory_item(inventory_id: str, current_store: dict = Depends(get_current_store)):
    inventory = await db["inventory"].find_one({"_id": inventory_id, "store_id": current_store["_id"]})
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    return InventoryResponse(**inventory)

@router.put("/{inventory_id}", response_model=InventoryUpdateResponse)
async def update_inventory(inventory_id: str, inventory: UpdateInventory, current_store: dict = Depends(get_current_store)):
    items = [
        {**item.dict(), "_id": f"item_{generate(size=10)}"} if not item._id else item.dict()
        for item in inventory.items
    ]
    inventory_data = inventory.dict()
    inventory_data.update({
        "items": items,
        "updated_at": datetime.utcnow()
    })
    
    result = await db["inventory"].update_one(
        {"_id": inventory_id, "store_id": current_store["_id"]},
        {"$set": inventory_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    
    updated_inventory = await db["inventory"].find_one({"_id": inventory_id, "store_id": current_store["_id"]})
    return InventoryUpdateResponse(**updated_inventory)
