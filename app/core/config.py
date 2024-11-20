from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8000
    
    mongo_uri: str
    mongo_db: str
    redis_uri: str
    
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    
    razorpay_api_key: str
    razorpay_api_secret: str

    whatsapp_secret: str
    whatsapp_store_number: str
    whatsapp_user_number: str

    base_url: str
    inference_url: str
    
    class Config:
        env_file = ".env"
        ignore_extra = True

settings = Settings()
