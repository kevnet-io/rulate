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
