"""Security utilities for input validation and attack prevention."""

import json
from typing import Any

import yaml
from fastapi import HTTPException, UploadFile, status

from api.config import settings
from api.logging_config import get_logger

logger = get_logger(__name__)


class SafeYAMLLoader(yaml.SafeLoader):
    """YAML loader with depth and alias limits to prevent bombs."""

    def __init__(self, stream: Any):
        self._depth = 0
        self._max_depth = settings.yaml_max_depth
        self._alias_count = 0
        self._max_aliases = settings.yaml_max_aliases
        super().__init__(stream)

    def compose_node(self, parent: Any, index: Any) -> Any:
        """Override to track nesting depth and alias count during composition."""
        # Check for alias usage BEFORE calling super()
        # This must be done before super() because compose_node() internally consumes the AliasEvent
        if self.check_event(yaml.events.AliasEvent):
            self._alias_count += 1
            if self._alias_count > self._max_aliases:
                raise yaml.YAMLError(
                    f"YAML contains too many alias references (max: {self._max_aliases})"
                )

        # Track nesting depth
        self._depth += 1
        if self._depth > self._max_depth:
            raise yaml.YAMLError(f"YAML depth exceeds maximum of {self._max_depth} levels")
        try:
            return super().compose_node(parent, index)
        finally:
            self._depth -= 1


def safe_yaml_load(content: str) -> Any:
    """
    Safely load YAML with depth and alias limits.

    Args:
        content: YAML content string

    Returns:
        Parsed YAML data

    Raises:
        HTTPException: If YAML is invalid or exceeds limits
    """
    try:
        return yaml.load(content, Loader=SafeYAMLLoader)
    except yaml.YAMLError as e:
        logger.warning("yaml_parsing_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid YAML: {str(e)}"
        )


def safe_json_load(content: str) -> Any:
    """
    Safely load JSON with basic validation.

    Args:
        content: JSON content string

    Returns:
        Parsed JSON data

    Raises:
        HTTPException: If JSON is invalid
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.warning("json_parsing_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON: {str(e)}"
        )


async def validate_file_upload(file: UploadFile) -> bytes:
    """
    Validate and read uploaded file with size limits.

    Args:
        file: Uploaded file

    Returns:
        File content as bytes

    Raises:
        HTTPException: If file exceeds size limit
    """
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    # Read file in chunks to avoid loading huge files into memory
    content = bytearray()
    chunk_size = 1024 * 1024  # 1MB chunks

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break

        content.extend(chunk)

        if len(content) > max_size_bytes:
            logger.warning(
                "file_upload_size_exceeded",
                filename=file.filename,
                size_mb=len(content) / (1024 * 1024),
                limit_mb=settings.max_upload_size_mb,
            )
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"File size exceeds maximum of {settings.max_upload_size_mb}MB",
            )

    logger.info(
        "file_upload_validated",
        filename=file.filename,
        size_bytes=len(content),
    )

    return bytes(content)


def sanitize_catalog_name(name: str) -> str:
    """
    Sanitize catalog name to prevent path traversal attacks.

    Args:
        name: Catalog name

    Returns:
        Sanitized name

    Raises:
        HTTPException: If name contains invalid characters
    """
    # Allow alphanumeric, underscore, hyphen
    if not name.replace("_", "").replace("-", "").isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catalog name can only contain letters, numbers, underscores, and hyphens",
        )

    # Prevent path traversal
    if ".." in name or "/" in name or "\\" in name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Catalog name cannot contain path separators",
        )

    return name
