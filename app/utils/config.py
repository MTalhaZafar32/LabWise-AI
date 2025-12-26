"""
Configuration settings for LabWise AI
"""
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "LabWise AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_PREFIX: str = "/api"
    ALLOWED_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/labwise.db"
    KB_DATA_PATH: Path = Path("Knowladge-base")
    
    # OCR Settings
    OCR_CONFIDENCE_THRESHOLD: float = 0.7
    USE_GPU: bool = False
    
    # LLM Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "phi3:mini"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 500
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".png", ".jpg", ".jpeg"}
    UPLOAD_DIR: Path = Path("uploads")
    
    # Medical Safety
    CONFIDENCE_LOW_THRESHOLD: float = 0.6
    CONFIDENCE_MEDIUM_THRESHOLD: float = 0.8
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create necessary directories
settings.UPLOAD_DIR.mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)
