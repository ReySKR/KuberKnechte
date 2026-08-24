import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    quote_path: str

@lru_cache
def get_settings() -> BaseSettings:
    if os.getenv("IS_PROD"):
        settings: BaseSettings = Settings()
        if not os.getenv("QUOTE_PATH"):
            raise ValueError("Quote path not set to environment variable 'QUOTE_PATH'.")
        settings.quote_path = os.getenv("QUOTE_PATH")
    else:
        settings = Settings(_env_file=".env")
    return settings