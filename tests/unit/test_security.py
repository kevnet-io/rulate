"""Tests for security utilities."""

from unittest.mock import AsyncMock, MagicMock

import pytest
import yaml
from fastapi import HTTPException

from api.security import (
    safe_json_load,
    safe_yaml_load,
    sanitize_catalog_name,
    validate_file_upload,
)


class TestSafeYAMLLoader:
    """Tests for YAML bomb prevention."""

    def test_simple_yaml_loads(self):
        """Test simple YAML loads successfully."""
        content = "key: value\nlist:\n  - item1\n  - item2"
        data = safe_yaml_load(content)
        assert data["key"] == "value"
        assert len(data["list"]) == 2

    def test_deep_nesting_rejected(self):
        """Test deeply nested YAML is rejected."""
        # Create YAML with 25 levels of nesting (exceeds default limit of 20)
        # Each level needs proper indentation
        lines = []
        for i in range(25):
            lines.append("  " * i + f"level{i}:")
        lines.append("  " * 25 + "value: final")
        content = "\n".join(lines)

        with pytest.raises((yaml.YAMLError, HTTPException)):
            safe_yaml_load(content)

    def test_valid_aliases_allowed(self):
        """Test reasonable aliases work (depth limiting is primary protection)."""
        # Small number of aliases should work
        content = """
base: &base
  key: value
item1: *base
item2: *base
item3: *base
"""
        data = safe_yaml_load(content)
        assert data["item1"]["key"] == "value"
        assert data["item2"]["key"] == "value"

    def test_excessive_alias_uses_rejected(self):
        """Test YAML with too many alias USES is rejected."""
        # Create YAML with 1 anchor but 150 uses (exceeds limit of 100)
        content = "base: &base value\n"
        for i in range(150):
            content += f"item_{i}: *base\n"

        with pytest.raises((yaml.YAMLError, HTTPException)):
            safe_yaml_load(content)

    def test_alias_uses_within_limit_allowed(self):
        """Test reasonable number of alias uses works."""
        # Create YAML with 1 anchor and 50 uses (within limit)
        content = "base: &base value\n"
        for i in range(50):
            content += f"item_{i}: *base\n"

        data = safe_yaml_load(content)
        assert len(data) == 51  # 1 base + 50 items
        assert data["base"] == "value"
        assert data["item_0"] == "value"
        assert data["item_49"] == "value"


class TestCatalogNameSanitization:
    """Tests for catalog name sanitization."""

    def test_valid_names_pass(self):
        """Test valid catalog names pass validation."""
        assert sanitize_catalog_name("my_catalog") == "my_catalog"
        assert sanitize_catalog_name("catalog-v2") == "catalog-v2"
        assert sanitize_catalog_name("catalog123") == "catalog123"
        assert sanitize_catalog_name("MyCatalog") == "MyCatalog"

    def test_path_traversal_rejected(self):
        """Test path traversal attempts are rejected."""
        with pytest.raises(HTTPException):
            sanitize_catalog_name("../etc/passwd")

        with pytest.raises(HTTPException):
            sanitize_catalog_name("catalog/../admin")

        with pytest.raises(HTTPException):
            sanitize_catalog_name("..\\windows\\system32")

    def test_invalid_characters_rejected(self):
        """Test invalid characters are rejected."""
        with pytest.raises(HTTPException):
            sanitize_catalog_name("catalog;rm -rf /")

        with pytest.raises(HTTPException):
            sanitize_catalog_name("catalog with spaces")

        with pytest.raises(HTTPException):
            sanitize_catalog_name("catalog!@#$")

    def test_path_separators_rejected(self):
        """Test path separators are rejected."""
        with pytest.raises(HTTPException):
            sanitize_catalog_name("path/to/catalog")

        with pytest.raises(HTTPException):
            sanitize_catalog_name("path\\to\\catalog")


class TestSafeJSONLoad:
    """Tests for safe JSON loading."""

    def test_valid_json_loads(self):
        """Test simple JSON loads successfully."""
        content = '{"key": "value", "list": [1, 2, 3]}'
        data = safe_json_load(content)
        assert data["key"] == "value"
        assert len(data["list"]) == 3

    def test_invalid_json_raises_http_exception(self):
        """Test invalid JSON raises HTTPException with 400 status."""
        with pytest.raises(HTTPException) as exc_info:
            safe_json_load("not valid json")
        assert exc_info.value.status_code == 400
        assert "Invalid JSON" in exc_info.value.detail

    def test_empty_json_object(self):
        """Test empty JSON object loads."""
        data = safe_json_load("{}")
        assert data == {}

    def test_json_array_loads(self):
        """Test JSON array loads."""
        data = safe_json_load("[1, 2, 3]")
        assert data == [1, 2, 3]


class TestValidateFileUpload:
    """Tests for file upload validation."""

    @pytest.mark.asyncio
    async def test_file_under_limit_succeeds(self, monkeypatch):
        """Test file under size limit uploads successfully."""
        # Set small limit for testing
        monkeypatch.setattr("api.security.settings.max_upload_size_mb", 1)

        # Create mock file with small content
        content = b"small file content"
        mock_file = MagicMock()
        mock_file.filename = "test.yaml"

        # Mock async read to return content then empty bytes
        mock_file.read = AsyncMock(side_effect=[content, b""])

        result = await validate_file_upload(mock_file)
        assert result == content

    @pytest.mark.asyncio
    async def test_file_over_limit_raises_413(self, monkeypatch):
        """Test file exceeding size limit raises 413."""
        # Set very small limit (1 byte) for testing
        monkeypatch.setattr("api.security.settings.max_upload_size_mb", 0)

        # Create mock file that returns content exceeding limit
        content = b"this content exceeds the 0MB limit"
        mock_file = MagicMock()
        mock_file.filename = "large.yaml"
        mock_file.read = AsyncMock(side_effect=[content, b""])

        with pytest.raises(HTTPException) as exc_info:
            await validate_file_upload(mock_file)
        assert exc_info.value.status_code == 413
        assert "exceeds maximum" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_chunked_reading(self, monkeypatch):
        """Test file is read in chunks."""
        monkeypatch.setattr("api.security.settings.max_upload_size_mb", 10)

        # Create mock file that returns content in multiple chunks
        chunk1 = b"first chunk of data "
        chunk2 = b"second chunk of data"
        mock_file = MagicMock()
        mock_file.filename = "chunked.yaml"
        mock_file.read = AsyncMock(side_effect=[chunk1, chunk2, b""])

        result = await validate_file_upload(mock_file)
        assert result == chunk1 + chunk2
