# Configuration settings
"""Configuration settings for the application."""

import os
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    app_name: str = "Documentation Update Assistant"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Logging Settings
    log_level: str = "INFO"
    environment: str = "development"
    
    # OpenAI Settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    
    # Storage Settings
    storage_path: str = "data"
    documents_path: str = "documents"
    
    # CORS Settings
    allowed_origins: List[str] = [
        "http://localhost:3000", 
        "http://localhost:8000"
    ]
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Database Settings (for future use)
    database_url: Optional[str] = None
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


# Global settings instance
settings = Settings()