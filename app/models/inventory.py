from pydantic import BaseModel, Field, field_validator
from typing import List
from datetime import datetime
from decimal import Decimal

class InventoryItem(BaseModel):
    sku_id: str
    product_id: str
    quantity: int
    price: Decimal

    @field_validator("price")
    def validate_price(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Price must have at most two decimal places")
        return value
    
class InventoryCreate(BaseModel):
    store_id: str
    items: List[InventoryItem]
    total: Decimal

    @field_validator("total")
    def validate_price(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Price must have at most two decimal places")
        return value
    
class InventoryResponse(BaseModel):
    id: str = Field(..., alias="_id")
    store_id: str
    items: List[InventoryItem]
    total: Decimal
    created_at: datetime
    updated_at: datetime

    @field_validator("total")
    def validate_price(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Price must have at most two decimal places")
        return value
    
class UpdateInventoryItem(BaseModel):
    quantity: int
    price: Decimal

    @field_validator("price")
    def validate_price(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Price must have at most two decimal places")
        return value
    
class UpdateInventory(BaseModel):
    items: List[UpdateInventoryItem]
    total: Decimal

    @field_validator("total")
    def validate_price(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Price must have at most two decimal places")
        return value
    
class InventoryUpdateResponse(BaseModel):
    id: str = Field(..., alias="_id")
    store_id: str
    items: List[InventoryItem]
    total: Decimal
    created_at: datetime
    updated_at: datetime

    @field_validator("total")
    def validate_price(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Price must have at most two decimal places")
        return value
    