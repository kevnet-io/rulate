"""Tests for configuration management."""

from api.config import Settings


class TestSettings:
    """Tests for Settings configuration."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        assert settings.environment == "development"
        assert settings.port == 8000
        assert settings.log_level == "INFO"
        assert settings.max_upload_size_mb == 10
        assert settings.yaml_max_depth == 20
        assert settings.yaml_max_aliases == 100

    def test_environment_override(self, monkeypatch):
        """Test environment variable overrides."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("PORT", "9000")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        settings = Settings()
        assert settings.environment == "production"
        assert settings.port == 9000
        assert settings.log_level == "DEBUG"

    def test_cors_origins_parsing_from_string(self, monkeypatch):
        """Test CORS origins parsing from JSON list string."""
        # pydantic-settings expects JSON format for lists
        monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:3000","http://app.example.com"]')

        settings = Settings()
        assert len(settings.cors_origins) == 2
        assert "http://localhost:3000" in settings.cors_origins
        assert "http://app.example.com" in settings.cors_origins

    def test_cors_origins_parsing_with_spaces(self, monkeypatch):
        """Test CORS origins parsing handles JSON list format."""
        monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:3000", "http://app.example.com"]')

        settings = Settings()
        assert len(settings.cors_origins) == 2
        assert "http://localhost:3000" in settings.cors_origins

    def test_is_development_property(self):
        """Test is_development property."""
        dev_settings = Settings(environment="development")
        assert dev_settings.is_development is True
        assert dev_settings.is_production is False

    def test_is_production_property(self):
        """Test is_production property."""
        prod_settings = Settings(environment="production")
        assert prod_settings.is_development is False
        assert prod_settings.is_production is True

    def test_staging_environment(self):
        """Test staging environment."""
        staging_settings = Settings(environment="staging")
        assert staging_settings.is_development is False
        assert staging_settings.is_production is False
        assert staging_settings.environment == "staging"

    def test_database_url_override(self, monkeypatch):
        """Test database URL can be overridden."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost/db")

        settings = Settings()
        assert settings.database_url == "postgresql://user:pass@localhost/db"

    def test_security_settings_override(self, monkeypatch):
        """Test security settings can be overridden."""
        monkeypatch.setenv("MAX_UPLOAD_SIZE_MB", "50")
        monkeypatch.setenv("YAML_MAX_DEPTH", "10")
        monkeypatch.setenv("YAML_MAX_ALIASES", "50")

        settings = Settings()
        assert settings.max_upload_size_mb == 50
        assert settings.yaml_max_depth == 10
        assert settings.yaml_max_aliases == 50
