"""
Application Configuration
"""

from pydantic_settings import BaseSettings
from typing import List
from pydantic import field_validator, ConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8"
    )
    
    # Database
    database_url: str = "mysql+pymysql://gary:wjdwhdans@localhost:3306/household_ledger"
    
    # JWT
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_refresh_secret: str = "your-refresh-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS - accept comma-separated string from env, default to list
    cors_origins_str: str | None = None
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from environment variable or return default"""
        if self.cors_origins_str:
            # Parse comma-separated string
            return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]
        return ["http://localhost:3001", "http://localhost:3000"]
    
    # OCR
    ocr_provider: str = "easyocr"
    ocr_languages: str = "ko,en"
    
    # File Upload
    upload_dir: str = "./uploads"
    max_upload_size: int = 10485760  # 10MB


settings = Settings()

