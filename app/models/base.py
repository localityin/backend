from pydantic import BaseModel, Field, field_validator
from uuid import uuid4, UUID
from datetime import datetime
from nanoid import generate

from app.utils.datetime import get_local_datetime, IST

PREFIXES = {
    "users": "usr_",
    "stores": "str_",
    'address': 'adr_',
    "products": "prd_",
    "orders": "ord_",
    "subscriptions": "sub_",
    "payments": "pay_",
    "analytics": "anl_"
}

class BaseUUIDModel(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    created_at: datetime = Field(
        default_factory=get_local_datetime, alias="createdAt")
    updated_at: datetime = Field(
        default_factory=get_local_datetime, alias="updatedAt")

    class Config:
        # Allow population by field name for easier use with Pydantic
        populate_by_name = True
        from_attributes = True

    @field_validator("created_at", "updated_at", mode='before', check_fields=True)
    def default_timezone(cls, v):
        return v.astimezone(IST)

    def model_dump(self, *args, **kwargs):
        # Override model_dump method to ensure updatedAt is always set to current time
        kwargs['by_alias'] = True
        d = super().model_dump(*args, **kwargs)
        return d


class BaseNanoIDModel(BaseModel):
    _id: str = Field(default=None, alias="_id")
    created_at: datetime = Field(default_factory=get_local_datetime, alias="createdAt")
    updated_at: datetime = Field(default_factory=get_local_datetime, alias="updatedAt")

    class Config:
        populate_by_name = True
        from_attributes = True

    @field_validator("_id", mode="before")
    def generate_nanoid_id(cls, v, values):
        """Generates _id with prefix and nanoid if not already set"""
        if v is not None:
            return v  # Return existing ID if provided

        # Extract class name and map to prefix
        class_name = cls.__name__
        prefix = PREFIXES.get(class_name, "gen_")  # Default prefix if not found
        nano_id = generate(size=8)  # Generate a nanoid of length 8

        return f"{prefix}{nano_id}"

    @field_validator("created_at", "updated_at", mode="before", check_fields=True)
    def default_timezone(cls, v):
        return v.astimezone(IST)

    def model_dump(self, *args, **kwargs):
        kwargs['by_alias'] = True
        d = super().model_dump(*args, **kwargs)
        return d