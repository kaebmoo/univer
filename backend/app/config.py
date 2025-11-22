"""
Application Configuration
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "Univer Report System"
    app_env: str = "development"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite:///./data/app.db"

    # Email Configuration (for OTP)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@company.com"
    smtp_from_name: str = "Univer Report System"

    # JWT Configuration
    jwt_secret: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 1440  # minutes (24 hours)

    # OTP Configuration
    otp_length: int = 6
    otp_expiration: int = 300  # seconds (5 minutes)
    otp_max_attempts: int = 3

    # Allowed Email Domains
    allowed_email_domains: str = "company.com,company.co.th"

    # CORS Configuration
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    cors_allow_credentials: bool = True

    # Data Files
    profit_loss_csv: str = "./data/profit_loss.csv"
    other_income_expense_csv: str = "./data/other_income_expense.csv"

    # Cache Configuration
    enable_cache: bool = True
    cache_ttl: int = 3600  # seconds (1 hour)

    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def allowed_domains_list(self) -> List[str]:
        """Get allowed email domains as list"""
        return [domain.strip() for domain in self.allowed_email_domains.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def profit_loss_path(self) -> Path:
        """Get profit loss CSV path"""
        return Path(self.profit_loss_csv)

    @property
    def other_income_expense_path(self) -> Path:
        """Get other income/expense CSV path"""
        return Path(self.other_income_expense_csv)

    def is_email_allowed(self, email: str) -> bool:
        """Check if email domain is allowed"""
        domain = email.split("@")[-1].lower()
        return domain in [d.lower() for d in self.allowed_domains_list]


# Create global settings instance
settings = Settings()
