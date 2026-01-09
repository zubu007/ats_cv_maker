"""
API Configuration Module
Centralized configuration for the API server
"""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", 8000))
    api_reload: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    
    # CORS Configuration
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    
    # API Documentation
    api_title: str = "ATS CV Maker API"
    api_description: str = "REST API for analyzing and improving CVs for ATS compatibility"
    api_version: str = "1.0.0"
    
    # LLM Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
