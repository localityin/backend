from app.models.product import Product
from app.database import product_collection
from uuid import UUID


async def create_product(product_data: dict):
    product = Product(**product_data)
    await product_collection.insert_one(product.model_dump_json(by_alias=True))
    return product


async def get_product(product_id: str):
    product = await product_collection.find_one({"id": product_id})
    return Product(**product) if product else None


async def update_product(product_id: str, product_data: dict):
    await product_collection.update_one({"id": product_id}, {"$set": product_data})
    updated_product = await db["products"].find_one({"id": product_id})
    return Product(**updated_product) if updated_product else None


async def delete_product(product_id: str):
    delete_result = await product_collection.delete_one({"id": product_id})
    return delete_result.deleted_count > 0


async def get_all_products():
    products = []
    async for product in product_collection.find():
        products.append(Product(**product))
    return products
