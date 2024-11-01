from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import redis.asyncio as aioredis

# MongoDB client setup
mongo_client = AsyncIOMotorClient(settings.mongo_uri)
db = mongo_client.get_database()

# Redis client setup
redis_client = aioredis.from_url(settings.redis_uri)

async def create_indexes():
    await db["stores"].create_index([("addresses.location", "2dsphere")])
    await db["products"].create_index([("store_id", 1)])
    await db["orders"].create_index([("store_id", 1)])
    await db["orders"].create_index([("user_id", 1)])