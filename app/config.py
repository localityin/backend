from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    mongo_url: str = Field(..., env="MONGO_URL")
    db_name: str = Field(..., env="DB_NAME")

    # Redis settings
    redis_host: str = Field(..., env="REDIS_HOST")
    redis_port: str = Field(..., env="REDIS_POST")
    redis_db: str = Field(..., env="REDIS_DB")
    redis_password: str = Field(..., env="REDIS_PASSWORD")

    # Application settings
    env: str = Field(..., env="ENV")
    version: str = Field(..., env="VERSION")
    secret: str = Field(..., env="SECRET")

    class Config:
        env_file = ".env"


settings = Settings()
