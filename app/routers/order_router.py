from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import List
from app.services.order_service import place_order, update_order, modify_order, fetch_order
from app.models.order import Order

router = APIRouter()


@router.post("/orders/place", response_model=Order)
async def place_order_route(user_id: UUID, products: List[dict], store_id: UUID, user_location: dict):
    new_order = await place_order(user_id, products, store_id, user_location)
    return new_order


@router.put("/orders/update/{store_id}/{order_id}")
async def update_order_route(store_id: UUID, order_id: UUID, status: str):
    updated_order = await update_order(store_id, order_id, status)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order updated successfully"}


@router.put("/orders/modify/{order_id}")
async def modify_order_route(order_id: UUID, products: List[dict], location: dict):
    modified_order = await modify_order(order_id, products, location)
    if not modified_order:
        raise HTTPException(
            status_code=404, detail="Order not found or status is not pending")
    return {"message": "Order modified successfully"}


@router.get("/orders/{order_id}", response_model=Order)
async def fetch_order_route(order_id: UUID):
    order = await fetch_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
