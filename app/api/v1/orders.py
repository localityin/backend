from fastapi import APIRouter, HTTPException, Depends, status
from app.models.order import OrderCreate, OrderResponse, OrderItem
from app.utils.security import get_current_user, get_current_store
from app.core.database import db
from nanoid import generate
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/", response_model=OrderResponse)
async def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    order_id = f"ord_{generate(size=10)}"
    order_data = order.dict()
    order_data.update({
        "_id": order_id,
        "user_id": current_user["_id"],
        "status": "pending",
        "payment_status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    await db["orders"].insert_one(order_data)
    return OrderResponse(**order_data)

@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(current_user: dict = Depends(get_current_user)):
    orders = await db["orders"].find({"user_id": current_user["_id"]}).to_list(100)
    return [OrderResponse(**order) for order in orders]

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    order = await db["orders"].find_one({"_id": order_id, "user_id": current_user["_id"]})
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return OrderResponse(**order)

@router.get("/track/{order_id}", response_model=OrderResponse)
async def track_order(order_id: str, current_user: dict = Depends(get_current_user)):
    order = await db["orders"].find_one({"_id": order_id, "user_id": current_user["_id"]})
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return OrderResponse(**order)

@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(order_id: str, current_user: dict = Depends(get_current_user)):
    order = await db["orders"].find_one({"_id": order_id, "user_id": current_user["_id"]})
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order["status"] != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order cannot be canceled")
    
    await db["orders"].update_one(
        {"_id": order_id, "user_id": current_user["_id"]},
        {"$set": {"status": "cancelled", "updated_at": datetime.utcnow()}}
    )
    updated_order = await db["orders"].find_one({"_id": order_id, "user_id": current_user["_id"]})
    return OrderResponse(**updated_order)

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: str, status: str, current_store: dict = Depends(get_current_store)):
    valid_statuses = ["accepted", "rejected", "dispatched", "delivered"]
    if status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    
    result = await db["orders"].update_one(
        {"_id": order_id, "store_id": current_store["_id"]},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found or unauthorized")
    
    updated_order = await db["orders"].find_one({"_id": order_id, "store_id": current_store["_id"]})
    return OrderResponse(**updated_order)
