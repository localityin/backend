from app.models.base import BaseModel, BaseNanoIDModel
from typing import List


class Message(BaseModel):
    product_sku_id: str
    store_id: str
    quantity: int


class Conversation(BaseNanoIDModel):
    _id: str
    mobile_number: str
    items: List[Message]
