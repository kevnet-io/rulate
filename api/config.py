"""
Application configuration using pydantic-settings.

Loads configuration from environment variables with validation and defaults.
"""

import json
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Rulate API"
    version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = Field(
        default="sqlite:///./rulate.db", description="Database connection URL"
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins (comma-separated in env)",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from JSON array or comma-separated string."""
        if isinstance(v, str):
            # Try JSON first (handles '["url1","url2"]' format)
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(o).strip() for o in parsed if str(o).strip()]
            except (json.JSONDecodeError, ValueError):
                pass
            # Fall back to comma-separated (handles 'url1,url2' format)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Security
    max_upload_size_mb: int = Field(default=10, description="Maximum file upload size in MB")
    yaml_max_depth: int = Field(
        default=20, description="Maximum nesting depth for YAML/JSON parsing"
    )
    yaml_max_aliases: int = Field(
        default=100, description="Maximum number of YAML aliases to prevent bombs"
    )

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"

    # Frontend
    frontend_build_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent / "web" / "build",
        description="Path to frontend build directory",
    )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


# Global settings instance
settings = Settings()
