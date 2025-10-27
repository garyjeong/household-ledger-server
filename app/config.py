"""
Application Configuration
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "mysql+pymysql://gary:wjdwhdans@localhost:3306/household_ledger"
    
    # JWT
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_refresh_secret: str = "your-refresh-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3001", "http://localhost:3000"]
    
    # OCR
    ocr_provider: str = "easyocr"
    ocr_languages: str = "ko,en"
    
    # File Upload
    upload_dir: str = "./uploads"
    max_upload_size: int = 10485760  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

