from app.models.base import BaseUUIDModel


class User(BaseUUIDModel):
    name: str
    mobile_number: str
    address: str
