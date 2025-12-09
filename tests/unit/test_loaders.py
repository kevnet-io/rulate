"""
Tests for YAML/JSON loading utilities.

This module tests file loading, parsing, and validation for schemas, rulesets,
catalogs, and cluster rulesets.
"""

import json
from pathlib import Path

import pytest
import yaml

from rulate.models.catalog import Catalog
from rulate.models.cluster import ClusterRuleSet
from rulate.models.rule import RuleSet
from rulate.models.schema import Schema
from rulate.utils.loaders import (
    load_catalog,
    load_catalog_from_string,
    load_cluster_ruleset,
    load_cluster_ruleset_from_string,
    load_ruleset,
    load_ruleset_from_string,
    load_schema,
    load_schema_from_string,
    load_yaml_or_json,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for test files."""
    return tmp_path


@pytest.fixture
def valid_schema_dict():
    """Valid schema data as a dictionary."""
    return {
        "name": "test_schema",
        "version": "1.0.0",
        "description": "Test schema",
        "dimensions": [
            {"name": "category", "type": "enum", "values": ["shirt", "pants"], "required": True},
            {"name": "color", "type": "string", "required": True},
        ],
    }


@pytest.fixture
def valid_ruleset_dict():
    """Valid ruleset data as a dictionary."""
    return {
        "name": "test_rules",
        "version": "1.0.0",
        "schema_ref": "test_schema",
        "rules": [
            {
                "name": "different_categories",
                "type": "requirement",
                "enabled": True,
                "condition": {"has_different": {"field": "category"}},
            }
        ],
    }


@pytest.fixture
def valid_catalog_dict():
    """Valid catalog data as a dictionary."""
    return {
        "name": "test_catalog",
        "schema_ref": "test_schema",
        "items": [
            {"id": "item1", "name": "Item 1", "attributes": {"category": "shirt", "color": "blue"}},
            {"id": "item2", "name": "Item 2", "attributes": {"category": "pants", "color": "black"}},
        ],
    }


@pytest.fixture
def valid_cluster_ruleset_dict():
    """Valid cluster ruleset data as a dictionary."""
    return {
        "name": "test_cluster_rules",
        "version": "1.0.0",
        "schema_ref": "test_schema",
        "pairwise_ruleset_ref": "test_rules",
        "rules": [
            {
                "name": "min_size",
                "type": "requirement",
                "enabled": True,
                "condition": {"min_cluster_size": 2},
            }
        ],
    }


# ============================================================================
# load_yaml_or_json() Tests
# ============================================================================


class TestLoadYamlOrJson:
    """Tests for load_yaml_or_json() function."""

    def test_loads_yaml_file(self, temp_dir, valid_schema_dict):
        """Test loading a YAML file."""
        yaml_file = temp_dir / "test.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(valid_schema_dict, f)

        data = load_yaml_or_json(yaml_file)
        assert data == valid_schema_dict

    def test_loads_yml_file(self, temp_dir, valid_schema_dict):
        """Test loading a .yml file."""
        yml_file = temp_dir / "test.yml"
        with open(yml_file, "w") as f:
            yaml.dump(valid_schema_dict, f)

        data = load_yaml_or_json(yml_file)
        assert data == valid_schema_dict

    def test_loads_json_file(self, temp_dir, valid_schema_dict):
        """Test loading a JSON file."""
        json_file = temp_dir / "test.json"
        with open(json_file, "w") as f:
            json.dump(valid_schema_dict, f)

        data = load_yaml_or_json(json_file)
        assert data == valid_schema_dict

    def test_accepts_string_path(self, temp_dir, valid_schema_dict):
        """Test that string paths are accepted."""
        yaml_file = temp_dir / "test.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(valid_schema_dict, f)

        data = load_yaml_or_json(str(yaml_file))  # Pass as string
        assert data == valid_schema_dict

    def test_raises_error_for_nonexistent_file(self, temp_dir):
        """Test that FileNotFoundError is raised for missing files."""
        nonexistent = temp_dir / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError, match="File not found"):
            load_yaml_or_json(nonexistent)

    def test_raises_error_for_unsupported_format(self, temp_dir):
        """Test that ValueError is raised for unsupported file formats."""
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("some content")

        with pytest.raises(ValueError, match="Unsupported file format"):
            load_yaml_or_json(txt_file)

    def test_raises_error_for_invalid_yaml(self, temp_dir):
        """Test that ValueError is raised for invalid YAML syntax."""
        yaml_file = temp_dir / "invalid.yaml"
        yaml_file.write_text("invalid: yaml: syntax: [")

        with pytest.raises(ValueError, match="Invalid YAML"):
            load_yaml_or_json(yaml_file)

    def test_raises_error_for_invalid_json(self, temp_dir):
        """Test that ValueError is raised for invalid JSON syntax."""
        json_file = temp_dir / "invalid.json"
        json_file.write_text('{"invalid": "json",}')  # Trailing comma

        with pytest.raises(ValueError, match="Invalid JSON"):
            load_yaml_or_json(json_file)


# ============================================================================
# load_schema() Tests
# ============================================================================


class TestLoadSchema:
    """Tests for load_schema() function."""

    def test_loads_valid_schema_from_yaml(self, temp_dir, valid_schema_dict):
        """Test loading a valid schema from YAML file."""
        yaml_file = temp_dir / "schema.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(valid_schema_dict, f)

        schema = load_schema(yaml_file)

        assert isinstance(schema, Schema)
        assert schema.name == "test_schema"
        assert schema.version == "1.0.0"
        assert len(schema.dimensions) == 2

    def test_loads_valid_schema_from_json(self, temp_dir, valid_schema_dict):
        """Test loading a valid schema from JSON file."""
        json_file = temp_dir / "schema.json"
        with open(json_file, "w") as f:
            json.dump(valid_schema_dict, f)

        schema = load_schema(json_file)

        assert isinstance(schema, Schema)
        assert schema.name == "test_schema"

    def test_raises_error_for_invalid_schema(self, temp_dir):
        """Test that ValueError is raised for invalid schema data."""
        yaml_file = temp_dir / "invalid_schema.yaml"
        invalid_data = {"name": "test", "version": "1.0.0"}  # Missing dimensions

        with open(yaml_file, "w") as f:
            yaml.dump(invalid_data, f)

        with pytest.raises(ValueError, match="Failed to load schema"):
            load_schema(yaml_file)

    def test_raises_error_for_nonexistent_file(self, temp_dir):
        """Test that error is raised for missing file."""
        nonexistent = temp_dir / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            load_schema(nonexistent)


# ============================================================================
# load_schema_from_string() Tests
# ============================================================================


class TestLoadSchemaFromString:
    """Tests for load_schema_from_string() function."""

    def test_loads_schema_from_yaml_string(self, valid_schema_dict):
        """Test loading schema from YAML string."""
        yaml_content = yaml.dump(valid_schema_dict)

        schema = load_schema_from_string(yaml_content, format="yaml")

        assert isinstance(schema, Schema)
        assert schema.name == "test_schema"

    def test_loads_schema_from_json_string(self, valid_schema_dict):
        """Test loading schema from JSON string."""
        json_content = json.dumps(valid_schema_dict)

        schema = load_schema_from_string(json_content, format="json")

        assert isinstance(schema, Schema)
        assert schema.name == "test_schema"

    def test_raises_error_for_invalid_format(self):
        """Test that ValueError is raised for unsupported format."""
        with pytest.raises(ValueError, match="Unsupported format"):
            load_schema_from_string("some content", format="xml")

    def test_raises_error_for_invalid_content(self):
        """Test that ValueError is raised for invalid schema content."""
        invalid_yaml = "name: test\nversion: 1.0.0"  # Missing dimensions

        with pytest.raises(ValueError, match="Failed to load schema from string"):
            load_schema_from_string(invalid_yaml)


# ============================================================================
# load_ruleset() Tests
# ============================================================================


class TestLoadRuleset:
    """Tests for load_ruleset() function."""

    def test_loads_valid_ruleset_from_yaml(self, temp_dir, valid_ruleset_dict):
        """Test loading a valid ruleset from YAML file."""
        yaml_file = temp_dir / "rules.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(valid_ruleset_dict, f)

        ruleset = load_ruleset(yaml_file)

        assert isinstance(ruleset, RuleSet)
        assert ruleset.name == "test_rules"
        assert len(ruleset.rules) == 1

    def test_loads_valid_ruleset_from_json(self, temp_dir, valid_ruleset_dict):
        """Test loading a valid ruleset from JSON file."""
        json_file = temp_dir / "rules.json"
        with open(json_file, "w") as f:
            json.dump(valid_ruleset_dict, f)

        ruleset = load_ruleset(json_file)

        assert isinstance(ruleset, RuleSet)
        assert ruleset.name == "test_rules"

    def test_raises_error_for_invalid_ruleset(self, temp_dir):
        """Test that ValueError is raised for invalid ruleset data."""
        yaml_file = temp_dir / "invalid_rules.yaml"
        invalid_data = {"name": "test"}  # Missing required fields

        with open(yaml_file, "w") as f:
            yaml.dump(invalid_data, f)

        with pytest.raises(ValueError, match="Failed to load ruleset"):
            load_ruleset(yaml_file)


# ============================================================================
# load_ruleset_from_string() Tests
# ============================================================================


class TestLoadRulesetFromString:
    """Tests for load_ruleset_from_string() function."""

    def test_loads_ruleset_from_yaml_string(self, valid_ruleset_dict):
        """Test loading ruleset from YAML string."""
        yaml_content = yaml.dump(valid_ruleset_dict)

        ruleset = load_ruleset_from_string(yaml_content, format="yaml")

        assert isinstance(ruleset, RuleSet)
        assert ruleset.name == "test_rules"

    def test_loads_ruleset_from_json_string(self, valid_ruleset_dict):
        """Test loading ruleset from JSON string."""
        json_content = json.dumps(valid_ruleset_dict)

        ruleset = load_ruleset_from_string(json_content, format="json")

        assert isinstance(ruleset, RuleSet)
        assert ruleset.name == "test_rules"

    def test_raises_error_for_unsupported_format(self):
        """Test that ValueError is raised for unsupported format."""
        with pytest.raises(ValueError, match="Unsupported format"):
            load_ruleset_from_string("content", format="xml")


# ============================================================================
# load_catalog() Tests
# ============================================================================


class TestLoadCatalog:
    """Tests for load_catalog() function."""

    def test_loads_valid_catalog_from_yaml(self, temp_dir, valid_catalog_dict):
        """Test loading a valid catalog from YAML file."""
        yaml_file = temp_dir / "catalog.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(valid_catalog_dict, f)

        catalog = load_catalog(yaml_file)

        assert isinstance(catalog, Catalog)
        assert catalog.name == "test_catalog"
        assert len(catalog.items) == 2

    def test_loads_valid_catalog_from_json(self, temp_dir, valid_catalog_dict):
        """Test loading a valid catalog from JSON file."""
        json_file = temp_dir / "catalog.json"
        with open(json_file, "w") as f:
            json.dump(valid_catalog_dict, f)

        catalog = load_catalog(json_file)

        assert isinstance(catalog, Catalog)
        assert catalog.name == "test_catalog"

    def test_raises_error_for_invalid_catalog(self, temp_dir):
        """Test that ValueError is raised for invalid catalog data."""
        yaml_file = temp_dir / "invalid_catalog.yaml"
        invalid_data = {"name": "test"}  # Missing required fields

        with open(yaml_file, "w") as f:
            yaml.dump(invalid_data, f)

        with pytest.raises(ValueError, match="Failed to load catalog"):
            load_catalog(yaml_file)


# ============================================================================
# load_catalog_from_string() Tests
# ============================================================================


class TestLoadCatalogFromString:
    """Tests for load_catalog_from_string() function."""

    def test_loads_catalog_from_yaml_string(self, valid_catalog_dict):
        """Test loading catalog from YAML string."""
        yaml_content = yaml.dump(valid_catalog_dict)

        catalog = load_catalog_from_string(yaml_content, format="yaml")

        assert isinstance(catalog, Catalog)
        assert catalog.name == "test_catalog"
        assert len(catalog.items) == 2

    def test_loads_catalog_from_json_string(self, valid_catalog_dict):
        """Test loading catalog from JSON string."""
        json_content = json.dumps(valid_catalog_dict)

        catalog = load_catalog_from_string(json_content, format="json")

        assert isinstance(catalog, Catalog)
        assert catalog.name == "test_catalog"

    def test_raises_error_for_unsupported_format(self):
        """Test that ValueError is raised for unsupported format."""
        with pytest.raises(ValueError, match="Unsupported format"):
            load_catalog_from_string("content", format="xml")


# ============================================================================
# load_cluster_ruleset() Tests
# ============================================================================


class TestLoadClusterRuleset:
    """Tests for load_cluster_ruleset() function."""

    def test_loads_valid_cluster_ruleset_from_yaml(self, temp_dir, valid_cluster_ruleset_dict):
        """Test loading a valid cluster ruleset from YAML file."""
        yaml_file = temp_dir / "cluster_rules.yaml"
        with open(yaml_file, "w") as f:
            yaml.dump(valid_cluster_ruleset_dict, f)

        cluster_ruleset = load_cluster_ruleset(yaml_file)

        assert isinstance(cluster_ruleset, ClusterRuleSet)
        assert cluster_ruleset.name == "test_cluster_rules"
        assert len(cluster_ruleset.rules) == 1

    def test_loads_valid_cluster_ruleset_from_json(self, temp_dir, valid_cluster_ruleset_dict):
        """Test loading a valid cluster ruleset from JSON file."""
        json_file = temp_dir / "cluster_rules.json"
        with open(json_file, "w") as f:
            json.dump(valid_cluster_ruleset_dict, f)

        cluster_ruleset = load_cluster_ruleset(json_file)

        assert isinstance(cluster_ruleset, ClusterRuleSet)
        assert cluster_ruleset.name == "test_cluster_rules"

    def test_raises_error_for_invalid_cluster_ruleset(self, temp_dir):
        """Test that ValueError is raised for invalid cluster ruleset data."""
        yaml_file = temp_dir / "invalid_cluster_rules.yaml"
        invalid_data = {"name": "test"}  # Missing required fields

        with open(yaml_file, "w") as f:
            yaml.dump(invalid_data, f)

        with pytest.raises(ValueError, match="Failed to load cluster ruleset"):
            load_cluster_ruleset(yaml_file)


# ============================================================================
# load_cluster_ruleset_from_string() Tests
# ============================================================================


class TestLoadClusterRulesetFromString:
    """Tests for load_cluster_ruleset_from_string() function."""

    def test_loads_cluster_ruleset_from_yaml_string(self, valid_cluster_ruleset_dict):
        """Test loading cluster ruleset from YAML string."""
        yaml_content = yaml.dump(valid_cluster_ruleset_dict)

        cluster_ruleset = load_cluster_ruleset_from_string(yaml_content, format="yaml")

        assert isinstance(cluster_ruleset, ClusterRuleSet)
        assert cluster_ruleset.name == "test_cluster_rules"

    def test_loads_cluster_ruleset_from_json_string(self, valid_cluster_ruleset_dict):
        """Test loading cluster ruleset from JSON string."""
        json_content = json.dumps(valid_cluster_ruleset_dict)

        cluster_ruleset = load_cluster_ruleset_from_string(json_content, format="json")

        assert isinstance(cluster_ruleset, ClusterRuleSet)
        assert cluster_ruleset.name == "test_cluster_rules"

    def test_raises_error_for_unsupported_format(self):
        """Test that ValueError is raised for unsupported format."""
        with pytest.raises(ValueError, match="Unsupported format"):
            load_cluster_ruleset_from_string("content", format="xml")

    def test_raises_error_for_invalid_content(self):
        """Test that ValueError is raised for invalid cluster ruleset content."""
        invalid_yaml = "name: test\nversion: 1.0.0"  # Missing required fields

        with pytest.raises(ValueError, match="Failed to load cluster ruleset from string"):
            load_cluster_ruleset_from_string(invalid_yaml)


# ============================================================================
# Integration Tests
# ============================================================================


class TestLoadersIntegration:
    """Integration tests for loaders with real example files."""

    def test_round_trip_yaml(self, temp_dir, valid_schema_dict):
        """Test saving and loading back produces same data."""
        yaml_file = temp_dir / "roundtrip.yaml"

        # Save
        with open(yaml_file, "w") as f:
            yaml.dump(valid_schema_dict, f)

        # Load
        schema = load_schema(yaml_file)

        # Verify
        assert schema.name == valid_schema_dict["name"]
        assert schema.version == valid_schema_dict["version"]
        assert len(schema.dimensions) == len(valid_schema_dict["dimensions"])

    def test_round_trip_json(self, temp_dir, valid_catalog_dict):
        """Test JSON save and load produces same data."""
        json_file = temp_dir / "roundtrip.json"

        # Save
        with open(json_file, "w") as f:
            json.dump(valid_catalog_dict, f)

        # Load
        catalog = load_catalog(json_file)

        # Verify
        assert catalog.name == valid_catalog_dict["name"]
        assert len(catalog.items) == len(valid_catalog_dict["items"])

    def test_loads_from_example_files_if_they_exist(self):
        """Test loading from actual example files if they exist."""
        example_schema = Path("examples/wardrobe/schema.yaml")

        if example_schema.exists():
            schema = load_schema(example_schema)
            assert isinstance(schema, Schema)
            assert schema.name is not None
