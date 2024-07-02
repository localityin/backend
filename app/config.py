from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    mongo_url: str = Field(..., env="MONGO_URL")
    db_name: str = Field(..., env="DB_NAME")

    # Application settings
    env: str = Field(..., env="ENV")
    version: str = Field(..., env="VERSION")

    class Config:
        env_file = ".env"


settings = Settings()
