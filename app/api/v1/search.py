from fastapi import APIRouter
from typing import Optional
from app.models.store import StoreResponse
from app.models.product import ProductResponse

from app.core.database import db
from typing import List

from datetime import datetime

router = APIRouter()

@router.get("/stores", response_model=List[StoreResponse])
async def search_stores(query: Optional[str] = None, limit: int = 10):
    query_filter = {"name": {"$regex": query, "$options": "i"}} if query else {}
    stores = await db["stores"].find(query_filter).limit(limit).to_list(limit)
    return [StoreResponse(**store) for store in stores]

@router.get("/products", response_model=List[ProductResponse])
async def search_products(query: Optional[str] = None, category: Optional[str] = None, limit: int = 10):
    query_filter = {}
    if query:
        query_filter["name"] = {"$regex": query, "$options": "i"}
    if category:
        query_filter["category"] = category
    products = await db["products"].find(query_filter).limit(limit).to_list(limit)
    return [ProductResponse(**product) for product in products]

@router.get("/stores/nearby", response_model=List[StoreResponse])
async def get_nearby_stores(latitude: float, longitude: float, max_distance: int = 5000, limit: int = 10):
    stores = await db["stores"].find({
        "addresses": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [longitude, latitude]},
                "$maxDistance": max_distance
            }
        }
    }).limit(limit).to_list(limit)
    return [StoreResponse(**store) for store in stores]
