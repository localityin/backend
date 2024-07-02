from app.models.base import BaseUUIDModel, BaseModel
from pydantic import Field
from typing import Optional
from uuid import UUID


class Location(BaseModel):
    latitude: float
    longitude: float


class Store(BaseUUIDModel):
    name: str
    address: Optional[str]
    location: Location
    status: str = "active"

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Local Mart",
                "address": "123 Main Street",
                "status": "active",
                "location": {"latitude": 12.3456, "longitude": 78.9123}
            }
        }
