from app.models.inventory import Inventory, InventoryItem
from app.database.mongo import inventory_collection
from uuid import UUID


async def add_to_inventory(store_id: str, product_sku_id: str, quantity: int):
    inventory_item = InventoryItem(
        product_sku_id=product_sku_id, store_id=store_id, quantity=quantity)
    await inventory_collection.insert_one(inventory_item.model_dump_json(by_alias=True))


async def get_inventory(store_id: str):
    inventory = await inventory_collection.find_one({"store_id": store_id})
    return Inventory(**inventory) if inventory else None
