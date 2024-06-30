from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # Database settings
    mongo_url: str = Field(..., env="MONGODB_URI")
    db_name: str = Field(..., env="MONGODB_NAME")

    # Application settings
    env: bool = Field(False, env="ENVIRONMENT")
    version: bool = Field(False, env="VERSION")

    class Config:
        env_file = ".env"


settings = Settings()
