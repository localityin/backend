from app.models.base import BaseUUIDModel
from pydantic import Field
from typing import Optional
from uuid import UUID


class Location():
    latitude: float
    longitude: float


class Store(BaseUUIDModel):
    name: str
    address: Optional[str]
    location: Location
    status: str = "active"

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "Local Mart",
                "address": "123 Main Street",
                "status": "active",
                "location": {"latitude": 12.3456, "longitude": 78.9123}
            }
        }
