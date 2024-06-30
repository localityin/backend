from app.models.base import BaseUUIDModel


class User(BaseUUIDModel):
    name: str
    phone: str
    address: str
