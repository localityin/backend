from fastapi import APIRouter, HTTPException, Depends, status
from app.models.product import ProductCreate, ProductResponse, SKU
from app.utils.security import get_current_store
from app.core.database import db
from nanoid import generate
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate, current_store: dict = Depends(get_current_store)):
    product_id = f"prd_{generate(size=10)}"
    skus = [
        {**sku.dict(), "_id": f"sku_{generate(size=10)}"}
        for sku in product.skus
    ]
    product_data = product.dict()
    product_data.update({
        "_id": product_id,
        "store_id": current_store["_id"],
        "skus": skus,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    await db["products"].insert_one(product_data)
    return ProductResponse(**product_data)

@router.get("/", response_model=List[ProductResponse])
async def get_products(current_store: dict = Depends(get_current_store)):
    products = await db["products"].find({"store_id": current_store["_id"]}).to_list(100)
    return [ProductResponse(**product) for product in products]

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, current_store: dict = Depends(get_current_store)):
    product = await db["products"].find_one({"_id": product_id, "store_id": current_store["_id"]})
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return ProductResponse(**product)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product: ProductCreate, current_store: dict = Depends(get_current_store)):
    skus = [
        {**sku.dict(), "_id": f"sku_{generate(size=10)}"} if not sku._id else sku.dict()
        for sku in product.skus
    ]
    product_data = product.dict()
    product_data.update({
        "skus": skus,
        "updated_at": datetime.utcnow()
    })
    
    result = await db["products"].update_one(
        {"_id": product_id, "store_id": current_store["_id"]},
        {"$set": product_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    updated_product = await db["products"].find_one({"_id": product_id, "store_id": current_store["_id"]})
    return ProductResponse(**updated_product)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, current_store: dict = Depends(get_current_store)):
    result = await db["products"].delete_one({"_id": product_id, "store_id": current_store["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return None

@router.post("/{product_id}/skus", response_model=SKU)
async def add_sku(product_id: str, sku: SKU, current_store: dict = Depends(get_current_store)):
    sku_data = {**sku.dict(), "_id": f"sku_{generate(size=10)}"}
    result = await db["products"].update_one(
        {"_id": product_id, "store_id": current_store["_id"]},
        {"$push": {"skus": sku_data}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return SKU(**sku_data)

@router.put("/{product_id}/skus/{sku_id}", response_model=SKU)
async def update_sku(product_id: str, sku_id: str, sku: SKU, current_store: dict = Depends(get_current_store)):
    sku_data = sku.dict()
    result = await db["products"].update_one(
        {"_id": product_id, "store_id": current_store["_id"], "skus._id": sku_id},
        {"$set": {"skus.$": sku_data}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SKU not found")
    return sku

@router.delete("/{product_id}/skus/{sku_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sku(product_id: str, sku_id: str, current_store: dict = Depends(get_current_store)):
    result = await db["products"].update_one(
        {"_id": product_id, "store_id": current_store["_id"]},
        {"$pull": {"skus": {"_id": sku_id}}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SKU not found")
    return None

@router.put("/bulk-update")
async def bulk_update_products(updates: List[ProductCreate], current_store: dict = Depends(get_current_store)):
    for product in updates:
        await db["products"].update_one(
            {"_id": product._id, "store_id": current_store["_id"]},
            {"$set": product.dict()}
        )
    return {"status": "Bulk update completed"}
