from app.models.base import BaseModel, BaseUUIDModel
from typing import List, Optional


class Message(BaseModel):
    product_sku_id: str
    store_id: str
    quantity: int


class Conversation(BaseUUIDModel):
    mobile_number: str
    items: List[Message]
