from app.models.product import Product
from app.database import get_database
from uuid import UUID


async def create_product(product_data: dict):
    db = await get_database()
    product = Product(**product_data)
    await db["products"].insert_one(product.model_dump_json(by_alias=True))
    return product


async def get_product(product_id: str):
    db = await get_database()
    product = await db["products"].find_one({"id": product_id})
    return Product(**product) if product else None


async def update_product(product_id: str, product_data: dict):
    db = await get_database()
    await db["products"].update_one({"id": product_id}, {"$set": product_data})
    updated_product = await db["products"].find_one({"id": product_id})
    return Product(**updated_product) if updated_product else None


async def delete_product(product_id: str):
    db = await get_database()
    delete_result = await db["products"].delete_one({"id": product_id})
    return delete_result.deleted_count > 0


async def get_all_products():
    db = await get_database()
    products = []
    async for product in db["products"].find():
        products.append(Product(**product))
    return products
