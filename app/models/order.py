from app.models.base import BaseUUIDModel, BaseModel
from pydantic import Field
from typing import List
from uuid import UUID


class OrderItem(BaseModel):
    product_id: str
    quantity: int


class Location(BaseModel):
    latitude: float
    longitude: float


class Order(BaseUUIDModel):
    user_id: UUID
    store_id: UUID
    items: List[OrderItem]
    status: str = "pending"
    rating: float = 5
    delivery_address: Location
    user_address: Location = None
    store_address: Location = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": "e7c9d3b5-7a46-4e64-bc90-29e3ecb8cf92",
                "store_id": "a8c7b4d5-6b36-4f7a-891c-1e6fd4bc032e",
                "items": [
                    {"product_id": "1", "quantity": 2},
                    {"product_id": "2", "quantity": 1}
                ],
                "rating": 3.4,
                "delivery_address": {"latitude": 12.9716, "longitude": 77.5946},
                "user_address": {"latitude": 12.3456, "longitude": 78.9123},
                "store_address": {"latitude": 12.6789, "longitude": 76.5432}
            }
        }
