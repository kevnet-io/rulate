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
async def readiness_check(response: Response, db: Session = Depends(get_db)) -> dict[str, str]:
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
