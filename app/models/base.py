from pydantic import BaseModel, Field, field_validator
from uuid import uuid4, UUID
from datetime import datetime

from app.utils.datetime import get_local_datetime, IST


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
