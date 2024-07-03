import redis
from redis import Redis
from app.config import settings

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
)


def get_redis() -> Redis:
    return redis_client
