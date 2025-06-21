from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Project info
    project_name: str = "Chat App"
    version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    debug: bool = True
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings():
    return Settings()
