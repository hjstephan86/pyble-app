# config.py - Configuration (application.properties equivalent)

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Bible App"
    app_version: str = "1.0.0"
    app_description: str = "A Bible application built with FastAPI"
    
    # Database settings
    database_url: str = "sqlite:///./bible.db"
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = True
    reload: bool = True
    
    # CORS settings
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    # Security settings (for future use)
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # Pagination settings
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Search settings
    search_limit: int = 50
    min_search_length: int = 3
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()

# Configuration for different environments
class DevelopmentSettings(Settings):
    debug: bool = True
    reload: bool = True
    database_url: str = "sqlite:///./bible_dev.db"

class ProductionSettings(Settings):
    debug: bool = False
    reload: bool = False
    database_url: str = "postgresql://user:password@localhost/bible_prod"
    
class TestSettings(Settings):
    database_url: str = "sqlite:///./bible_test.db"
    
# You can switch environments by setting ENVIRONMENT variable
def get_settings():
    import os
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "test":
        return TestSettings()
    else:
        return DevelopmentSettings()