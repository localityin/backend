from app.models.inventory import Inventory, InventoryItem
from app.database import get_database
from uuid import UUID


async def add_to_inventory(store_id: str, product_sku_id: str, quantity: int):
    db = await get_database()
    inventory_item = InventoryItem(
        product_sku_id=product_sku_id, store_id=store_id, quantity=quantity)
    await db["inventory"].insert_one(inventory_item.model_dump_json(by_alias=True))


async def get_inventory(store_id: str):
    db = await get_database()
    inventory = await db["inventory"].find_one({"store_id": store_id})
    return Inventory(**inventory) if inventory else None
