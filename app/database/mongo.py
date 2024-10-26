from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.mongo_url)
database = client.get_database(settings.db_name)

user_collection = database.get_collection("users")
store_collection = database.get_collection("stores")
order_collection = database.get_collection("orders")
inventory_collection = database.get_collection("inventory")
product_collection = database.get_collection("products")
product_master_collection = database.get_collection("product_master")

conversation_collection = database.get_collection('conversations')

subscription_plans_collection = database.get_collection('subscription_plans')
payments_collection = database.get_collection('payments')
