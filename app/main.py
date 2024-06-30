from fastapi import FastAPI
from app.routers import user_router, store_router, order_router, webhook_router
from app.config import settings

app = FastAPI()

app.include_router(user_router.router, prefix="/api/v1")
app.include_router(store_router.router, prefix="/api/v1")
app.include_router(order_router.router, prefix="/api/v1")
app.include_router(webhook_router.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Locality API",
        "debug": settings.debug,
        "version": settings.version
    }
