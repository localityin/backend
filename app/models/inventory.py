from app.models.base import BaseNanoIDModel, BaseModel
from typing import List


class InventoryItem(BaseModel):
    product_sku_id: str
    store_id: str
    quantity: int


class Inventory(BaseNanoIDModel):
    store_id: str
    items: List[InventoryItem]
