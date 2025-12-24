# Production Ready - Implementation Plan

**Epic**: Production Ready
**Version**: 0.1.0
**Last Updated**: December 24, 2025
**Status**: Planning → Implementation

## Overview

This plan transforms Rulate from "works on my machine" to a production-ready service with containerization, structured configuration, enhanced monitoring, and security hardening.

## Success Criteria

- [ ] Single `docker-compose up` command starts the full stack
- [ ] Health endpoint reports service status and dependencies
- [ ] Configuration managed via environment variables
- [ ] Structured logging with JSON output
- [ ] Security audit completed with no critical issues
- [ ] Comprehensive deployment documentation

---

## Current State Analysis

**Configuration**:
- Basic environment variables used: `DATABASE_URL`, `ENVIRONMENT`
- No structured configuration management
- CORS already conditional on ENVIRONMENT

**Health Endpoint**:
- Simple `/health` endpoint at line 72-75 in `/home/user/rulate/api/main.py`
- Returns only `{"status": "healthy"}`
- No database connectivity check, version info, or uptime

**Logging**:
- Minimal logging - only `print()` statements in CLI utilities
- Uses `click.echo()` in CLI commands
- No structured logging anywhere

**Dependencies**:
- Current: pydantic, pyyaml, click, fastapi, uvicorn, sqlalchemy
- Missing production deps: structlog, pydantic-settings

**Docker**:
- No Docker files exist yet
- No docker-compose configuration

**Security**:
- Uses `yaml.safe_load()` (good!)
- No file size limits
- No depth limits for YAML/JSON
- No rate limiting

---

## Phase 1: Environment Configuration Foundation

**Goal**: Replace hardcoded values with structured, validated configuration management.

### 1.1 Add Dependencies

**File**: `pyproject.toml`

Add to `dependencies` array (line 23-31):
```toml
"pydantic-settings>=2.0.0",
"python-dotenv>=1.0.0",
```

Add to `dev` dependency group (line 34-44):
```toml
"faker>=20.0.0",  # For generating test data
```

**Action**: Run `uv sync --dev` after changes

### 1.2 Create Configuration Module

**New File**: `api/config.py`

```python
"""
Application configuration using pydantic-settings.

Loads configuration from environment variables with validation and defaults.
"""

import os
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
        default="sqlite:///./rulate.db",
        description="Database connection URL"
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins (comma-separated in env)"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Security
    max_upload_size_mb: int = Field(
        default=10,
        description="Maximum file upload size in MB"
    )
    yaml_max_depth: int = Field(
        default=20,
        description="Maximum nesting depth for YAML/JSON parsing"
    )
    yaml_max_aliases: int = Field(
        default=100,
        description="Maximum number of YAML aliases to prevent bombs"
    )

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "text"] = "json"

    # Frontend
    frontend_build_dir: Path = Field(
        default=Path(__file__).parent.parent / "web" / "build",
        description="Path to frontend build directory"
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
```

### 1.3 Create Environment File Templates

**New File**: `.env.example`

```bash
# Application
ENVIRONMENT=development
DEBUG=false
VERSION=0.1.0

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./rulate.db

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Security
MAX_UPLOAD_SIZE_MB=10
YAML_MAX_DEPTH=20
YAML_MAX_ALIASES=100

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

**New File**: `.env.production.example`

```bash
# Application
ENVIRONMENT=production
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./data/rulate.db

# CORS (not needed in production - same origin)
CORS_ORIGINS=

# Security
MAX_UPLOAD_SIZE_MB=10
YAML_MAX_DEPTH=20
YAML_MAX_ALIASES=100

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 1.4 Update Database Connection

**File**: `api/database/connection.py`

Replace lines 13-16 with:
```python
from api.config import settings

# Database URL from settings
DATABASE_URL = settings.database_url
```

### 1.5 Update Main Application

**File**: `api/main.py`

Replace lines 40-50 (CORS configuration) with:
```python
from api.config import settings

# Configure CORS - only in development mode
if settings.is_development and settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

Replace line 53 (FRONTEND_BUILD_DIR) with:
```python
FRONTEND_BUILD_DIR = settings.frontend_build_dir
```

### 1.6 Testing

**New File**: `tests/unit/test_config.py`

```python
"""Tests for configuration management."""

import os
import pytest
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

    def test_environment_override(self, monkeypatch):
        """Test environment variable overrides."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("PORT", "9000")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        settings = Settings()
        assert settings.environment == "production"
        assert settings.port == 9000
        assert settings.log_level == "DEBUG"

    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from string."""
        settings = Settings(cors_origins="http://localhost:3000,http://app.example.com")
        assert len(settings.cors_origins) == 2
        assert "http://localhost:3000" in settings.cors_origins

    def test_is_development_property(self):
        """Test is_development property."""
        dev_settings = Settings(environment="development")
        assert dev_settings.is_development is True
        assert dev_settings.is_production is False

        prod_settings = Settings(environment="production")
        assert prod_settings.is_development is False
        assert prod_settings.is_production is True
```

**Commit Point**: "feat: add structured configuration with pydantic-settings"

---

## Phase 2: Structured Logging

**Goal**: Implement production-grade structured logging with JSON output.

### 2.1 Add Dependencies

**File**: `pyproject.toml`

Add to `dependencies` array:
```toml
"structlog>=23.2.0",
"python-json-logger>=2.0.0",
```

### 2.2 Create Logging Configuration

**New File**: `api/logging_config.py`

```python
"""
Structured logging configuration using structlog.

Provides JSON logging for production and human-readable logging for development.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from api.config import settings


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to log events."""
    event_dict["app"] = settings.app_name
    event_dict["version"] = settings.version
    event_dict["environment"] = settings.environment
    return event_dict


def configure_logging() -> None:
    """
    Configure structured logging for the application.

    - Development: Human-readable colored output
    - Production: JSON formatted logs for log aggregation
    """

    # Determine log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Shared processors for all environments
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
    ]

    if settings.log_format == "json":
        # Production: JSON logging
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Human-readable logging
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structured logger

    Example:
        logger = get_logger(__name__)
        logger.info("user_login", user_id=123, ip="192.168.1.1")
    """
    return structlog.get_logger(name)
```

### 2.3 Add Request/Response Logging Middleware

**New File**: `api/middleware/logging.py`

```python
"""Request/response logging middleware."""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from api.logging_config import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""

        # Start timer
        start_time = time.time()

        # Extract request details
        request_id = request.headers.get("X-Request-ID", "-")
        method = request.method
        path = request.url.path
        client_host = request.client.host if request.client else "-"

        # Log request
        logger.info(
            "http_request_started",
            request_id=request_id,
            method=method,
            path=path,
            client_host=client_host,
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            logger.info(
                "http_request_completed",
                request_id=request_id,
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            return response

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            logger.error(
                "http_request_failed",
                request_id=request_id,
                method=method,
                path=path,
                duration_ms=round(duration_ms, 2),
                error=str(exc),
                exc_info=True,
            )
            raise
```

### 2.4 Update Main Application

**File**: `api/main.py`

Add imports at top:
```python
from api.logging_config import configure_logging, get_logger
from api.middleware.logging import LoggingMiddleware
```

Update lifespan function (lines 22-28):
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    configure_logging()
    logger = get_logger(__name__)
    logger.info("application_startup", environment=settings.environment)

    init_db()
    logger.info("database_initialized")

    yield

    # Shutdown
    logger.info("application_shutdown")
```

Add middleware after CORS (around line 60):
```python
# Add request/response logging middleware
if not settings.is_development:  # Only in staging/production
    app.add_middleware(LoggingMiddleware)
```

**Commit Point**: "feat: add structured logging with structlog"

---

## Phase 3: Enhanced Health Check Endpoints

**Goal**: Kubernetes-friendly health checks with database connectivity and detailed status.

### 3.1 Create Health Check Module

**New File**: `api/routers/health.py`

```python
"""Health check endpoints for monitoring and orchestration."""

import time
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.config import settings
from api.database.connection import get_db
from api.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Track application start time
_start_time = time.time()


def check_database(db: Session) -> dict[str, Any]:
    """
    Check database connectivity.

    Returns:
        Status dict with connection details
    """
    try:
        # Execute simple query
        result = db.execute(text("SELECT 1"))
        result.fetchone()

        return {
            "status": "healthy",
            "message": "Database connection successful",
        }
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
        }


@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Comprehensive health check endpoint.

    Returns application status, version, uptime, and dependency health.
    Used for monitoring and alerting.

    Returns:
        200: Application is healthy
        503: Application is unhealthy (database down)
    """
    uptime_seconds = int(time.time() - _start_time)

    # Check database
    db_status = check_database(db)
    is_healthy = db_status["status"] == "healthy"

    response_data = {
        "status": "healthy" if is_healthy else "unhealthy",
        "version": settings.version,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime_seconds,
        "dependencies": {
            "database": db_status,
        },
    }

    logger.info(
        "health_check",
        status=response_data["status"],
        uptime=uptime_seconds,
    )

    return response_data


@router.get("/health/ready")
async def readiness_check(
    response: Response,
    db: Session = Depends(get_db)
) -> dict[str, str]:
    """
    Kubernetes readiness probe.

    Indicates whether the application is ready to receive traffic.
    Checks that all dependencies (database) are available.

    Returns:
        200: Application is ready to receive traffic
        503: Application is not ready (dependencies unavailable)
    """
    db_status = check_database(db)

    if db_status["status"] == "healthy":
        return {"status": "ready"}

    response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    logger.warning("readiness_check_failed", reason="database_unhealthy")
    return {"status": "not_ready", "reason": "database_unavailable"}


@router.get("/health/live")
async def liveness_check() -> dict[str, str]:
    """
    Kubernetes liveness probe.

    Indicates whether the application is alive and should not be restarted.
    This is a simple check that the application process is running.

    Always returns 200 unless the application is completely broken.

    Returns:
        200: Application is alive
    """
    return {"status": "alive"}
```

### 3.2 Update Main Application

**File**: `api/main.py`

Remove old health check (lines 72-75):
```python
# DELETE THIS:
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

Add health router import (line 18):
```python
from api.routers import catalogs, clusters, evaluation, health, import_export, rulesets, schemas
```

Add health router registration (after line 69):
```python
# Include health check router (no prefix - top-level routes)
app.include_router(health.router, tags=["health"])

# Include other routers with /api/v1 prefix
app.include_router(schemas.router, prefix="/api/v1", tags=["schemas"])
# ... rest of routers ...
```

**Commit Point**: "feat: add enhanced health check endpoints for Kubernetes"

---

## Phase 4: Security Hardening

**Goal**: Prevent YAML bombs, limit file uploads, add input validation.

### 4.1 Create Security Utilities

**New File**: `api/security.py`

See detailed implementation in full plan above.

**Commit Point**: "feat: add security hardening (YAML bombs, file size limits, input sanitization)"

---

## Phase 5: Docker Configuration

**Goal**: Single-container deployment with `docker-compose up`.

See detailed Docker files in full plan above.

**Commit Point**: "feat: add Docker support with production and development configurations"

---

## Phase 6: Deployment Documentation

**Goal**: Comprehensive deployment guides for common platforms.

See detailed documentation structure in full plan above.

**Commit Point**: "docs: add comprehensive deployment documentation"

---

## Phase 7: Final Integration & Testing

See detailed testing strategy in full plan above.

**Commit Point**: "test: add integration tests for production features"

---

## Implementation Order & Dependencies

### Sprint 1: Foundation (Days 1-2)
1. Phase 1: Environment Configuration ✓
2. Phase 2: Structured Logging ✓

**Dependencies**: None
**Testing**: Unit tests for config and logging
**Deliverable**: Settings and logging working in development

### Sprint 2: Health & Security (Days 3-4)
3. Phase 3: Enhanced Health Checks ✓
4. Phase 4: Security Hardening ✓

**Dependencies**: Requires Phase 1 (settings)
**Testing**: Integration tests for health endpoints, unit tests for security
**Deliverable**: Production-grade health monitoring and security

### Sprint 3: Containerization (Days 5-6)
5. Phase 5: Docker Configuration ✓

**Dependencies**: Requires Phases 1-4
**Testing**: Manual testing with Docker
**Deliverable**: Working Docker deployment

### Sprint 4: Documentation (Day 7)
6. Phase 6: Deployment Documentation ✓
7. Phase 7: Final Integration & Testing ✓

**Dependencies**: Requires all previous phases
**Testing**: Full integration test suite
**Deliverable**: Production-ready deployment

---

## Open Questions for User

1. **Database Backend**: Should we support PostgreSQL from the start, or document SQLite-to-PostgreSQL migration later?
   - **Recommendation**: Document SQLite for now (simpler), add PostgreSQL migration guide in docs

2. **Container Registry**: Where should we publish Docker images?
   - Options: Docker Hub, GitHub Container Registry, private registry
   - **Recommendation**: Document how to build locally, publish to GHCR as optional

3. **Authentication**: Should we add authentication/authorization in this epic?
   - **Recommendation**: No - this is infrastructure focused. Authentication is a separate epic

4. **Metrics Endpoint**: Should we add `/metrics` endpoint for Prometheus?
   - **Recommendation**: Add in Phase 2 (Scale & Performance) epic, not this one

5. **PostgreSQL Support**: Immediate or deferred?
   - **Recommendation**: Document PostgreSQL connection string, but don't require migration tooling yet

---

## Success Metrics

- [ ] All 1,833+ tests passing
- [ ] Docker image builds successfully (<500MB)
- [ ] Container starts in <10 seconds
- [ ] Health endpoint responds in <100ms
- [ ] Zero secrets in codebase (git-secrets check)
- [ ] Documentation complete for 3+ deployment platforms
- [ ] CI/CD pipeline green

---

## Critical Files for Implementation

Based on this plan, here are the most critical files:

1. **NEW**: `api/config.py` - Core configuration management
2. **MODIFY**: `api/main.py` - Integrate config, logging, health router
3. **NEW**: `api/routers/health.py` - Kubernetes-ready health checks
4. **NEW**: `api/logging_config.py` - Structured logging configuration
5. **NEW**: `Dockerfile` - Multi-stage production build
6. **NEW**: `api/security.py` - Security utilities
7. **NEW**: `.env.example` - Environment variable template
8. **NEW**: `docker-compose.yml` - Production deployment
