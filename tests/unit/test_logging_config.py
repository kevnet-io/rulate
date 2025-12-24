"""Tests for logging configuration."""

from unittest.mock import patch

from api.logging_config import add_app_context, configure_logging, get_logger


class TestAddAppContext:
    """Tests for add_app_context processor."""

    def test_adds_app_name(self):
        """Test that app name is added to log event."""
        event_dict = {}
        result = add_app_context(None, "info", event_dict)

        assert "app" in result
        assert result["app"] == "Rulate API"

    def test_adds_version(self):
        """Test that version is added to log event."""
        event_dict = {}
        result = add_app_context(None, "info", event_dict)

        assert "version" in result
        assert result["version"] == "0.1.0"

    def test_adds_environment(self):
        """Test that environment is added to log event."""
        event_dict = {}
        result = add_app_context(None, "info", event_dict)

        assert "environment" in result
        assert result["environment"] in ["development", "staging", "production"]

    def test_preserves_existing_fields(self):
        """Test that existing fields are preserved."""
        event_dict = {"existing": "value", "count": 42}
        result = add_app_context(None, "info", event_dict)

        assert result["existing"] == "value"
        assert result["count"] == 42


class TestConfigureLogging:
    """Tests for configure_logging function."""

    def test_configure_logging_json_format(self):
        """Test logging configuration with JSON format."""
        with patch("api.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "json"
            mock_settings.app_name = "Test App"
            mock_settings.version = "1.0.0"
            mock_settings.environment = "test"

            # Should not raise any errors
            configure_logging()

    def test_configure_logging_text_format(self):
        """Test logging configuration with text format."""
        with patch("api.logging_config.settings") as mock_settings:
            mock_settings.log_level = "INFO"
            mock_settings.log_format = "text"
            mock_settings.app_name = "Test App"
            mock_settings.version = "1.0.0"
            mock_settings.environment = "development"

            # Should not raise any errors - exercises the else branch
            configure_logging()

    def test_configure_logging_with_debug_level(self):
        """Test logging configuration with DEBUG level."""
        with patch("api.logging_config.settings") as mock_settings:
            mock_settings.log_level = "DEBUG"
            mock_settings.log_format = "json"
            mock_settings.app_name = "Test App"
            mock_settings.version = "1.0.0"
            mock_settings.environment = "test"

            # Should not raise any errors
            configure_logging()


class TestGetLogger:
    """Tests for get_logger function."""

    def test_returns_bound_logger(self):
        """Test that get_logger returns a structlog logger."""
        logger = get_logger(__name__)

        # Should return a logger instance
        assert logger is not None

    def test_logger_has_standard_methods(self):
        """Test that logger has standard logging methods."""
        logger = get_logger(__name__)

        # Verify standard logging methods exist
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
