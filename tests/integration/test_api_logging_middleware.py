"""Integration tests for logging middleware."""

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.middleware.logging import LoggingMiddleware


class TestLoggingMiddleware:
    """Tests for LoggingMiddleware."""

    @pytest.fixture
    def app_with_middleware(self):
        """Create a test app with logging middleware."""
        app = FastAPI()
        app.add_middleware(LoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")

        return app

    @pytest.fixture
    def test_client(self, app_with_middleware):
        """Create test client for app with middleware."""
        return TestClient(app_with_middleware, raise_server_exceptions=False)

    def test_successful_request_logs_started_and_completed(self, test_client):
        """Test successful request logs both started and completed events."""
        with patch("api.middleware.logging.logger") as mock_logger:
            response = test_client.get("/test")

            assert response.status_code == 200

            # Verify both log calls
            call_args_list = mock_logger.info.call_args_list
            assert len(call_args_list) >= 2

            # First call should be http_request_started
            first_call = call_args_list[0]
            assert first_call[0][0] == "http_request_started"

            # Second call should be http_request_completed
            second_call = call_args_list[1]
            assert second_call[0][0] == "http_request_completed"
            assert "duration_ms" in second_call[1]
            assert "status_code" in second_call[1]
            assert second_call[1]["status_code"] == 200

    def test_request_logs_method_and_path(self, test_client):
        """Test request logs include method and path."""
        with patch("api.middleware.logging.logger") as mock_logger:
            test_client.get("/test")

            call_kwargs = mock_logger.info.call_args_list[0][1]
            assert call_kwargs["method"] == "GET"
            assert call_kwargs["path"] == "/test"

    def test_request_id_header_extraction(self, test_client):
        """Test X-Request-ID header is logged when present."""
        with patch("api.middleware.logging.logger") as mock_logger:
            test_client.get("/test", headers={"X-Request-ID": "test-request-123"})

            call_kwargs = mock_logger.info.call_args_list[0][1]
            assert call_kwargs["request_id"] == "test-request-123"

    def test_missing_request_id_uses_default(self, test_client):
        """Test missing X-Request-ID uses dash as default."""
        with patch("api.middleware.logging.logger") as mock_logger:
            test_client.get("/test")

            call_kwargs = mock_logger.info.call_args_list[0][1]
            assert call_kwargs["request_id"] == "-"

    def test_exception_logs_error(self, test_client):
        """Test exceptions are logged with error level."""
        with patch("api.middleware.logging.logger") as mock_logger:
            test_client.get("/error")

            # Should have info calls for started, then error for failed
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert call_args[0][0] == "http_request_failed"
            assert "duration_ms" in call_args[1]
            assert "error" in call_args[1]

    def test_duration_calculation(self, test_client):
        """Test duration is calculated correctly."""
        with patch("api.middleware.logging.logger") as mock_logger:
            test_client.get("/test")

            # Get the completed log call
            completed_call = mock_logger.info.call_args_list[1]
            duration_ms = completed_call[1]["duration_ms"]

            # Duration should be a positive number (rounded to 2 decimal places)
            assert isinstance(duration_ms, float)
            assert duration_ms >= 0
            # Check it's rounded (has at most 2 decimal places)
            assert duration_ms == round(duration_ms, 2)

    def test_client_host_extraction(self, test_client):
        """Test client host is logged."""
        with patch("api.middleware.logging.logger") as mock_logger:
            test_client.get("/test")

            call_kwargs = mock_logger.info.call_args_list[0][1]
            # TestClient uses testclient as the host
            assert "client_host" in call_kwargs
