"""Request/response logging middleware."""

import time
from collections.abc import Callable

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
