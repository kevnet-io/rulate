"""Tests for security utilities."""

import pytest
import yaml
from fastapi import HTTPException

from api.security import safe_yaml_load, sanitize_catalog_name


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
