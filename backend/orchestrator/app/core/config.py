from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AI Security Testing Agent"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Database (SQLite)
    DATABASE_URL: str = "sqlite:///./data/bug_detector.db"
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"
    
    # Vector Database
    VECTOR_DB_PATH: str = "./data/vector_db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Scanner Configuration
    SEMGREP_TIMEOUT: int = 300
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-use-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
