"""
Configuration settings for the CashFlow application.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = "CashFlow Monitor"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    database_url: str = "sqlite:///./cashflow.db"
    database_echo: bool = False
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list[str] = [".csv", ".ofx", ".qif"]
    
    # Open Finance Brasil settings
    default_currency: str = "BRL"
    default_country: str = "BR"
    
    # Data processing settings
    batch_size: int = 1000
    max_transactions_per_import: int = 50000
    
    # Backup settings
    backup_directory: Path = Path("./backups")
    auto_backup_enabled: bool = True
    backup_retention_days: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure backup directory exists
settings.backup_directory.mkdir(exist_ok=True)
