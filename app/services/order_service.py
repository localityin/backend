from app.models.order import Order
from app.database import get_database
from uuid import UUID
from typing import List


async def place_order(user_id: UUID, products: List[dict], store_id: UUID, user_location: dict):
    db = await get_database()
    order_data = {
        "user_id": user_id,
        "store_id": store_id,
        "items": products,
        "status": "Pending",
        "user_location": user_location
    }
    order = Order(**order_data)
    await db["orders"].insert_one(order.model_dump_json(by_alias=True))
    return order


async def update_order(store_id: UUID, order_id: UUID, status: str):
    db = await get_database()
    await db["orders"].update_one({"_id": order_id, "store_id": store_id}, {"$set": {"status": status}})
    updated_order = await db["orders"].find_one({"_id": order_id})
    return Order(**updated_order) if updated_order else None


async def modify_order(order_id: UUID, products: List[dict], location: dict):
    db = await get_database()
    await db["orders"].update_one({"_id": order_id, "status": "Pending"}, {"$set": {"items": products, "user_location": location}})
    updated_order = await db["orders"].find_one({"_id": order_id})
    return Order(**updated_order) if updated_order else None


async def fetch_order(order_id: UUID):
    db = await get_database()
    order = await db["orders"].find_one({"_id": order_id})
    return Order(**order) if order else None
