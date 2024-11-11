from pydantic import BaseModel, Field, field_validator
from typing import List
from datetime import datetime
from decimal import Decimal

class OrderItem(BaseModel):
    sku_id: str
    product_id: str
    quantity: int
    price: Decimal

    @field_validator("price")
    def validate_price(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Price must have at most two decimal places")
        return value


class OrderCreate(BaseModel):
    store_id: str
    items: List[OrderItem]
    subtotal: Decimal
    platform_fee: Decimal
    delivery_fee: Decimal
    total: Decimal
    delivery_address: dict

    @field_validator("subtotal", "platform_fee", "delivery_fee", "total")
    def validate_price(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Price must have at most two decimal places")
        return value

class OrderResponse(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    store_id: str
    items: List[OrderItem]
    status: str
    subtotal: Decimal
    platform_fee: Decimal
    delivery_fee: Decimal
    total: Decimal
    payment_status: str
    created_at: datetime
    updated_at: datetime

    @field_validator("subtotal", "platform_fee", "delivery_fee", "total")
    def validate_price(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Price must have at most two decimal places")
        return value

class RateOrder(BaseModel):
    rating: int
    review: str