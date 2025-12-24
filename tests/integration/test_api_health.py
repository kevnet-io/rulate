"""Integration tests for health check endpoints."""

from unittest.mock import patch


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""

    def test_health_check_success(self, client):
        """Test health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], int)
        assert data["dependencies"]["database"]["status"] == "healthy"

    def test_health_check_includes_metadata(self, client):
        """Test health check includes all required metadata."""
        response = client.get("/health")
        data = response.json()

        # Required fields
        assert "version" in data
        assert "environment" in data
        assert "timestamp" in data
        assert "uptime_seconds" in data
        assert "dependencies" in data

        # Timestamp should be ISO format
        assert "T" in data["timestamp"]
        assert "Z" in data["timestamp"] or "+" in data["timestamp"]

    def test_health_check_environment(self, client):
        """Test health check shows correct environment."""
        response = client.get("/health")
        data = response.json()

        # Test environment should be development by default
        assert data["environment"] in ["development", "staging", "production"]

    def test_health_check_returns_503_when_db_unhealthy(self, client):
        """Test health check returns 503 when database is down."""
        with patch("api.routers.health.check_database") as mock_check:
            mock_check.return_value = {
                "status": "unhealthy",
                "message": "Database connection failed: Connection refused",
            }

            response = client.get("/health")

            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["dependencies"]["database"]["status"] == "unhealthy"


class TestReadinessProbe:
    """Tests for GET /health/ready endpoint."""

    def test_readiness_when_healthy(self, client):
        """Test readiness probe returns ready when healthy."""
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}

    def test_readiness_response_format(self, client):
        """Test readiness response has correct format."""
        response = client.get("/health/ready")
        data = response.json()

        assert "status" in data
        assert data["status"] in ["ready", "not_ready"]

    def test_readiness_returns_503_when_db_unhealthy(self, client):
        """Test readiness returns 503 when database is down."""
        with patch("api.routers.health.check_database") as mock_check:
            mock_check.return_value = {
                "status": "unhealthy",
                "message": "Database connection failed: Connection refused",
            }

            response = client.get("/health/ready")

            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "not_ready"
            assert data["reason"] == "database_unavailable"


class TestLivenessProbe:
    """Tests for GET /health/live endpoint."""

    def test_liveness_always_returns_alive(self, client):
        """Test liveness probe always returns alive."""
        response = client.get("/health/live")
        assert response.status_code == 200
        assert response.json() == {"status": "alive"}

    def test_liveness_no_dependencies(self, client):
        """Test liveness probe doesn't check dependencies."""
        # Liveness should return quickly without database checks
        response = client.get("/health/live")
        assert response.status_code == 200

        # Should only have status field
        data = response.json()
        assert list(data.keys()) == ["status"]
