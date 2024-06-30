from pydantic import BaseModel, Field, field_validator
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone

# Define IST timezone
IST = timezone(timedelta(hours=5, minutes=30))


class BaseUUIDModel(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, alias="updatedAt")

    class Config:
        # Allow population by field name for easier use with Pydantic
        allow_population_by_field_name = True
        orm_mode = True

    @field_validator("created_at", "updated_at", mode='before', check_fields=True)
    def default_timezone(cls, v):
        return v.astimezone(IST)

    def model_dump(self, *args, **kwargs):
        # Override model_dump method to ensure updatedAt is always set to current time
        kwargs['by_alias'] = True
        d = super().model_dump(*args, **kwargs)
        d['updatedAt'] = datetime.now(IST)
        return d