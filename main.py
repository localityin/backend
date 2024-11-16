from fastapi import FastAPI
from app.api.v1 import users, stores, products, orders, payments, search, whatsapp, inventory
from app.core.database import mongo_client, redis_client, create_indexes
from app.utils.datetime import get_ist_time

app = FastAPI()

# Include routers for all modules
app.include_router(users.router, prefix="/api/v1/users")
app.include_router(stores.router, prefix="/api/v1/stores")
app.include_router(products.router, prefix="/api/v1/products")
app.include_router(orders.router, prefix="/api/v1/orders")
app.include_router(payments.router, prefix="/api/v1/payments")
app.include_router(search.router, prefix="/api/v1/search")
app.include_router(whatsapp.router, prefix="/api/v1/whatsapp")
app.include_router(inventory.router, prefix="/api/v1/inventory")

@app.on_event("startup")
async def startup_db_client():
    print("Connecting to MongoDB and Redis...")

    # Create indexes for MongoDB collections
    await create_indexes()

@app.on_event("shutdown")
async def shutdown_db_client():
    print("Disconnecting MongoDB and Redis...")
    mongo_client.close()
    await redis_client.close()

@app.get("/health")
async def health_check():
    return {"status": "ok", "time": get_ist_time()}