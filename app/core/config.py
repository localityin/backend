from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str
    redis_uri: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    razorpay_api_key: str
    razorpay_api_secret: str
    whatsapp_secret: str
    
    class Config:
        env_file = ".env"

settings = Settings()
