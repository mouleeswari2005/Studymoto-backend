"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App
    APP_NAME: str = "Student Productivity API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/student_productivity"
    
    @field_validator('DATABASE_URL', mode='before')
    @classmethod
    def convert_postgres_to_postgresql_asyncpg(cls, v: str) -> str:
        """Convert postgres:// URLs to postgresql+asyncpg:// and remove sslmode for asyncpg compatibility."""
        if not isinstance(v, str):
            return v
            
        # Replace postgres:// with postgresql+asyncpg://
        if v.startswith('postgres://'):
            v = v.replace('postgres://', 'postgresql+asyncpg://', 1)
        
        # Remove sslmode parameter - asyncpg doesn't support it in URL
        # SSL will be handled via connect_args in database.py
        import re
        # Remove sslmode=... from query string
        v = re.sub(r'[?&]sslmode=[^&]*', '', v)
        # Clean up any double ? or trailing &
        v = v.replace('??', '?').replace('?&', '?').rstrip('&')
        # Remove trailing ? if no query params remain
        if v.endswith('?'):
            v = v[:-1]
        
        return v
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS - accept comma-separated string and convert to list
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS_ORIGINS string to list."""
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Email (for notifications - placeholder)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    
    # Premium Feature Flag
    PREMIUM_FEATURES_ENABLED: bool = True

    # Timezone Configuration - IST (GMT+05:30)
    TIMEZONE: str = "Asia/Kolkata"

    # Push Notifications (VAPID keys)
    VAPID_PUBLIC_KEY: Optional[str] = None
    VAPID_PRIVATE_KEY: Optional[str] = None
    VAPID_EMAIL: Optional[str] = None

    # Notification Worker
    NOTIFICATION_CHECK_INTERVAL: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

