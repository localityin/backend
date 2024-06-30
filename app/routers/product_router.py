from fastapi import APIRouter, HTTPException
from app.services.product_service import create_product, get_product, update_product, delete_product, get_all_products
from app.models.product import Product

router = APIRouter()


@router.post("/products", response_model=Product)
async def add_product(product: Product):
    new_product = await create_product(product)
    return new_product


@router.get("/products/{product_id}", response_model=Product)
async def fetch_product(product_id: str):
    product = await get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/products/{product_id}", response_model=Product)
async def modify_product(product_id: str, product_data: dict):
    updated_product = await update_product(product_id, product_data)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product


@router.delete("/products/{product_id}", response_model=dict)
async def remove_product(product_id: str):
    deleted = await delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


@router.get("/products", response_model=list[Product])
async def list_products():
    products = await get_all_products()
    return products
