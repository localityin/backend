from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class SKU(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    price: Decimal
    mrp: Decimal
    unit: str
    quantity: float
    in_stock: bool
    stock_count: int

    @field_validator("price")
    def validate_price(cls, value):
        if value.as_tuple().exponent < -2:
            raise ValueError("Price must have at most two decimal places")
        return value

class ProductCreate(BaseModel):
    name: str
    description: Optional[str]
    category: str
    sub_category: Optional[str]
    brand: Optional[str]
    skus: List[SKU]

class ProductResponse(BaseModel):
    id: str = Field(..., alias="_id")
    store_id: str
    name: str
    description: Optional[str]
    category: str
    sub_category: Optional[str]
    brand: Optional[str]
    skus: List[SKU]
    is_active: bool
    created_at: datetime
    updated_at: datetime
