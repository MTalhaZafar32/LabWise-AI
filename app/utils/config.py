"""
Configuration settings for LabWise AI
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from pathlib import Path
from typing import List, Union
import json

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "LabWise AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_PREFIX: str = "/api"
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173", 
        "http://localhost:3000",
        "http://localhost:5174",
        "http://localhost:5175"
    ]
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse ALLOWED_ORIGINS from various formats"""
        if isinstance(v, str):
            # Try to parse as JSON first
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Fall back to comma-separated values
                return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/labwise.db"
    KB_DATA_PATH: Path = Path("Knowladge-base")
    
    # OCR Settings
    OCR_CONFIDENCE_THRESHOLD: float = 0.7
    USE_GPU: bool = False
    
    # LLM Settings (Ollama - Legacy/Commented Out)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "phi3:mini"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 500
    
    # OpenAI API Settings (Active)
    OPENAI_API_KEY: str = ""  # From .env
    OPENAI_EXTRACTION_MODEL: str = "gpt-4o-mini"  # For extraction
    OPENAI_SUMMARY_MODEL: str = "gpt-4o-mini"  # For summary
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_MAX_TOKENS: int = 2000

    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".png", ".jpg", ".jpeg"]
    UPLOAD_DIR: Path = Path("uploads")
    
    # Medical Safety
    CONFIDENCE_LOW_THRESHOLD: float = 0.6
    CONFIDENCE_MEDIUM_THRESHOLD: float = 0.8
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

settings = Settings()

# Create necessary directories
settings.UPLOAD_DIR.mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)
