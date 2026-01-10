"""
Comprehensive tests for the CLI.

Tests cover all CLI commands:
- validate: schema, rules, catalog
- evaluate: pair, matrix, item, cluster
- show: schema, catalog
"""

import json

import pytest
import yaml
from click.testing import CliRunner

from rulate.cli import evaluate, main, show, validate


@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_schema_file(tmp_path):
    """Create a sample schema file for testing."""
    # Create YAML dict directly to avoid enum serialization issues
    schema_dict = {
        "name": "test_schema",
        "version": "1.0.0",
        "description": "Test schema",
        "dimensions": [
            {"name": "category", "type": "enum", "values": ["shirt", "pants"], "required": True},
            {"name": "color", "type": "string", "required": True},
            {"name": "formality", "type": "integer", "min": 1, "max": 5, "required": False},
        ],
    }
    schema_file = tmp_path / "schema.yaml"
    with open(schema_file, "w") as f:
        yaml.dump(schema_dict, f)
    return str(schema_file)


@pytest.fixture
def sample_ruleset_file(tmp_path):
    """Create a sample ruleset file for testing."""
    ruleset_dict = {
        "name": "test_rules",
        "version": "1.0.0",
        "schema_ref": "test_schema",
        "rules": [
            {
                "name": "different_categories",
                "type": "requirement",
                "condition": {"has_different": {"field": "category"}},
                "enabled": True,
            },
        ],
    }
    rules_file = tmp_path / "rules.yaml"
    with open(rules_file, "w") as f:
        yaml.dump(ruleset_dict, f)
    return str(rules_file)


@pytest.fixture
def sample_catalog_file(tmp_path):
    """Create a sample catalog file for testing."""
    catalog_dict = {
        "name": "test_catalog",
        "schema_ref": "test_schema",
        "items": [
            {
                "id": "shirt_001",
                "name": "Blue Shirt",
                "attributes": {"category": "shirt", "color": "blue", "formality": 3},
            },
            {
                "id": "pants_001",
                "name": "Black Pants",
                "attributes": {"category": "pants", "color": "black", "formality": 4},
            },
            {
                "id": "shirt_002",
                "name": "Red Shirt",
                "attributes": {"category": "shirt", "color": "red", "formality": 2},
            },
        ],
    }
    catalog_file = tmp_path / "catalog.yaml"
    with open(catalog_file, "w") as f:
        yaml.dump(catalog_dict, f)
    return str(catalog_file)


@pytest.fixture
def sample_cluster_ruleset_file(tmp_path, sample_ruleset_file):
    """Create a sample cluster ruleset file for testing."""
    cluster_ruleset_dict = {
        "name": "test_cluster_rules",
        "version": "1.0.0",
        "schema_ref": "test_schema",
        "pairwise_ruleset_ref": "test_rules",
        "rules": [
            {
                "name": "min_size",
                "type": "requirement",
                "condition": {"has_item_with": {"field": "category", "value": "shirt"}},
                "enabled": True,
            },
        ],
    }
    cluster_rules_file = tmp_path / "cluster_rules.yaml"
    with open(cluster_rules_file, "w") as f:
        yaml.dump(cluster_ruleset_dict, f)
    return str(cluster_rules_file)


@pytest.fixture
def invalid_schema_file(tmp_path):
    """Create an invalid schema file for testing error handling."""
    invalid_file = tmp_path / "invalid_schema.yaml"
    with open(invalid_file, "w") as f:
        f.write("invalid: yaml: content:\n  - broken")
    return str(invalid_file)


# ============================================================================
# VALIDATE COMMANDS TESTS
# ============================================================================


class TestValidateSchema:
    """Tests for 'validate schema' command."""

    def test_validates_valid_schema(self, cli_runner, sample_schema_file):
        """validate schema command succeeds with valid schema."""
        result = cli_runner.invoke(validate, ["schema", sample_schema_file])
        assert result.exit_code == 0
        assert "✓ Schema valid: test_schema v1.0.0" in result.output
        assert "Dimensions: 3" in result.output
        assert "category: enum (required)" in result.output
        assert "color: string (required)" in result.output
        assert "formality: integer" in result.output

    def test_fails_with_invalid_schema(self, cli_runner, invalid_schema_file):
        """validate schema command fails with invalid schema."""
        result = cli_runner.invoke(validate, ["schema", invalid_schema_file])
        assert result.exit_code == 1
        assert "✗ Schema validation failed" in result.output

    def test_fails_with_nonexistent_file(self, cli_runner):
        """validate schema command fails with nonexistent file."""
        result = cli_runner.invoke(validate, ["schema", "nonexistent.yaml"])
        assert result.exit_code != 0


class TestValidateRules:
    """Tests for 'validate rules' command."""

    def test_validates_valid_ruleset(self, cli_runner, sample_ruleset_file):
        """validate rules command succeeds with valid ruleset."""
        result = cli_runner.invoke(validate, ["rules", sample_ruleset_file])
        assert result.exit_code == 0
        assert "✓ RuleSet valid: test_rules v1.0.0" in result.output
        assert "Schema: test_schema" in result.output
        assert "Rules: 1" in result.output
        assert "different_categories (requirement, enabled)" in result.output

    def test_validates_ruleset_with_schema(
        self, cli_runner, sample_ruleset_file, sample_schema_file
    ):
        """validate rules command with --schema option."""
        result = cli_runner.invoke(
            validate, ["rules", sample_ruleset_file, "--schema", sample_schema_file]
        )
        assert result.exit_code == 0
        assert "✓ RuleSet valid" in result.output

    def test_warns_on_schema_mismatch(self, cli_runner, sample_ruleset_file, tmp_path):
        """validate rules command warns when schema doesn't match."""
        # Create schema with different name
        different_schema_dict = {
            "name": "different_schema",
            "version": "1.0.0",
            "dimensions": [{"name": "test", "type": "string", "required": True}],
        }
        different_schema_file = tmp_path / "different.yaml"
        with open(different_schema_file, "w") as f:
            yaml.dump(different_schema_dict, f)

        result = cli_runner.invoke(
            validate, ["rules", sample_ruleset_file, "--schema", str(different_schema_file)]
        )
        assert result.exit_code == 0
        assert "⚠ Warning" in result.output
        assert "different_schema" in result.output

    def test_fails_with_invalid_ruleset(self, cli_runner, invalid_schema_file):
        """validate rules command fails with invalid ruleset."""
        result = cli_runner.invoke(validate, ["rules", invalid_schema_file])
        assert result.exit_code == 1
        assert "✗ RuleSet validation failed" in result.output


class TestValidateCatalog:
    """Tests for 'validate catalog' command."""

    def test_validates_valid_catalog(self, cli_runner, sample_catalog_file):
        """validate catalog command succeeds with valid catalog."""
        result = cli_runner.invoke(validate, ["catalog", sample_catalog_file])
        assert result.exit_code == 0
        assert "✓ Catalog valid: test_catalog" in result.output
        assert "Schema: test_schema" in result.output
        assert "Items: 3" in result.output

    def test_validates_catalog_with_schema(
        self, cli_runner, sample_catalog_file, sample_schema_file
    ):
        """validate catalog command with --schema validates items."""
        result = cli_runner.invoke(
            validate, ["catalog", sample_catalog_file, "--schema", sample_schema_file]
        )
        assert result.exit_code == 0
        assert "✓ Catalog valid" in result.output
        assert "Validating items against schema" in result.output
        assert "✓ All 3 items valid" in result.output

    def test_warns_on_schema_mismatch(self, cli_runner, sample_catalog_file, tmp_path):
        """validate catalog command warns when schema doesn't match."""
        different_schema_dict = {
            "name": "different_schema",
            "version": "1.0.0",
            "dimensions": [{"name": "test", "type": "string", "required": True}],
        }
        different_schema_file = tmp_path / "different.yaml"
        with open(different_schema_file, "w") as f:
            yaml.dump(different_schema_dict, f)

        result = cli_runner.invoke(
            validate, ["catalog", sample_catalog_file, "--schema", str(different_schema_file)]
        )
        assert "⚠ Warning" in result.output
        assert "different_schema" in result.output

    def test_fails_with_invalid_items(self, cli_runner, tmp_path, sample_schema_file):
        """validate catalog command fails when items don't match schema."""
        # Create catalog with invalid items
        invalid_catalog_dict = {
            "name": "invalid_catalog",
            "schema_ref": "test_schema",
            "items": [
                {"id": "invalid_001", "name": "Invalid Item", "attributes": {"wrong": "field"}},
            ],
        }
        invalid_catalog_file = tmp_path / "invalid_catalog.yaml"
        with open(invalid_catalog_file, "w") as f:
            yaml.dump(invalid_catalog_dict, f)

        result = cli_runner.invoke(
            validate, ["catalog", str(invalid_catalog_file), "--schema", sample_schema_file]
        )
        assert result.exit_code == 1
        assert "✗ invalid_001" in result.output
        assert "items failed validation" in result.output

    def test_fails_with_invalid_catalog(self, cli_runner, invalid_schema_file):
        """validate catalog command fails with invalid catalog."""
        result = cli_runner.invoke(validate, ["catalog", invalid_schema_file])
        assert result.exit_code == 1
        assert "✗ Catalog validation failed" in result.output


# ============================================================================
# EVALUATE COMMANDS TESTS
# ============================================================================


class TestEvaluatePair:
    """Tests for 'evaluate pair' command."""

    def test_evaluates_compatible_pair_summary(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file
    ):
        """evaluate pair command shows compatible pair in summary format."""
        result = cli_runner.invoke(
            evaluate,
            [
                "pair",
                "shirt_001",
                "pants_001",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
                "--format",
                "summary",
            ],
        )
        assert result.exit_code == 0
        assert "✓" in result.output
        assert "Blue Shirt + Black Pants" in result.output
        assert "Compatible: True" in result.output

    def test_evaluates_incompatible_pair_summary(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file
    ):
        """evaluate pair command shows incompatible pair in summary format."""
        result = cli_runner.invoke(
            evaluate,
            [
                "pair",
                "shirt_001",
                "shirt_002",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
                "--format",
                "summary",
            ],
        )
        assert result.exit_code == 1
        assert "✗" in result.output
        assert "Blue Shirt + Red Shirt" in result.output
        assert "Compatible: False" in result.output

    def test_evaluates_pair_json_format(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file
    ):
        """evaluate pair command outputs JSON format."""
        result = cli_runner.invoke(
            evaluate,
            [
                "pair",
                "shirt_001",
                "pants_001",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["item1_id"] == "shirt_001"
        assert data["item2_id"] == "pants_001"
        assert data["compatible"] is True

    def test_evaluates_pair_yaml_format(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file
    ):
        """evaluate pair command outputs YAML format."""
        result = cli_runner.invoke(
            evaluate,
            [
                "pair",
                "shirt_001",
                "pants_001",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
                "--format",
                "yaml",
            ],
        )
        assert result.exit_code == 0
        data = yaml.safe_load(result.output)
        assert data["item1_id"] == "shirt_001"
        assert data["item2_id"] == "pants_001"

    def test_fails_with_nonexistent_item1(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file
    ):
        """evaluate pair command fails when item1 doesn't exist."""
        result = cli_runner.invoke(
            evaluate,
            [
                "pair",
                "nonexistent",
                "pants_001",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
            ],
        )
        assert result.exit_code == 1
        assert "✗ Item 'nonexistent' not found" in result.output

    def test_fails_with_nonexistent_item2(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file
    ):
        """evaluate pair command fails when item2 doesn't exist."""
        result = cli_runner.invoke(
            evaluate,
            [
                "pair",
                "shirt_001",
                "nonexistent",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
            ],
        )
        assert result.exit_code == 1
        assert "✗ Item 'nonexistent' not found" in result.output


class TestEvaluateMatrix:
    """Tests for 'evaluate matrix' command."""

    def test_evaluates_matrix_summary_format(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file
    ):
        """evaluate matrix command outputs summary format."""
        result = cli_runner.invoke(
            evaluate,
            [
                "matrix",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
                "--format",
                "summary",
            ],
        )
        assert result.exit_code == 0
        assert "Compatibility Matrix" in result.output
        assert "Blue Shirt" in result.output or "Black Pants" in result.output
        assert "Compatible pairs:" in result.output

    def test_evaluates_matrix_json_format(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file, tmp_path
    ):
        """evaluate matrix command outputs JSON format."""
        output_file = tmp_path / "matrix_test.json"
        result = cli_runner.invoke(
            evaluate,
            [
                "matrix",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
                "--format",
                "json",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
        assert "results" in data
        assert "catalog_name" in data
        assert len(data["results"]) > 0

    def test_evaluates_matrix_csv_format(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file
    ):
        """evaluate matrix command outputs CSV format."""
        result = cli_runner.invoke(
            evaluate,
            [
                "matrix",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
                "--format",
                "csv",
            ],
        )
        assert result.exit_code == 0
        assert "shirt_001" in result.output
        assert "pants_001" in result.output
        assert "," in result.output  # CSV delimiter

    def test_evaluates_matrix_with_output_file(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file, tmp_path
    ):
        """evaluate matrix command writes to output file."""
        output_file = tmp_path / "matrix.json"
        result = cli_runner.invoke(
            evaluate,
            [
                "matrix",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
                "--format",
                "json",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
        assert "results" in data


class TestEvaluateItem:
    """Tests for 'evaluate item' command."""

    def test_evaluates_item_against_catalog(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file
    ):
        """evaluate item command compares item against catalog."""
        result = cli_runner.invoke(
            evaluate,
            [
                "item",
                "shirt_001",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
            ],
        )
        assert result.exit_code == 0
        assert "Blue Shirt" in result.output
        assert "Compatible items" in result.output

    def test_evaluates_item_json_format(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file
    ):
        """evaluate item command outputs JSON format."""
        result = cli_runner.invoke(
            evaluate,
            [
                "item",
                "shirt_001",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_fails_with_nonexistent_item(
        self, cli_runner, sample_catalog_file, sample_ruleset_file, sample_schema_file
    ):
        """evaluate item command fails when item doesn't exist."""
        result = cli_runner.invoke(
            evaluate,
            [
                "item",
                "nonexistent",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--schema",
                sample_schema_file,
            ],
        )
        assert result.exit_code == 1
        assert "✗ Item 'nonexistent' not found" in result.output


class TestEvaluateCluster:
    """Tests for 'evaluate cluster' command."""

    def test_validates_valid_cluster_summary_format(
        self,
        cli_runner,
        sample_catalog_file,
        sample_ruleset_file,
        sample_cluster_ruleset_file,
        sample_schema_file,
    ):
        """evaluate cluster command validates a valid cluster."""
        result = cli_runner.invoke(
            evaluate,
            [
                "cluster",
                "shirt_001",
                "pants_001",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--cluster-rules",
                sample_cluster_ruleset_file,
                "--schema",
                sample_schema_file,
            ],
        )
        assert result.exit_code == 0
        assert "✓ Valid cluster" in result.output
        assert "Pairwise Compatibility" in result.output
        assert "Cluster Rules" in result.output

    def test_validates_invalid_cluster_pairwise_incompatible(
        self,
        cli_runner,
        sample_catalog_file,
        sample_ruleset_file,
        sample_cluster_ruleset_file,
        sample_schema_file,
    ):
        """evaluate cluster command detects pairwise incompatible items."""
        # shirt_001 and shirt_002 have same category, should be incompatible
        result = cli_runner.invoke(
            evaluate,
            [
                "cluster",
                "shirt_001",
                "shirt_002",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--cluster-rules",
                sample_cluster_ruleset_file,
                "--schema",
                sample_schema_file,
            ],
        )
        assert result.exit_code == 1
        assert "✗ Invalid cluster" in result.output
        assert "incompatible pair" in result.output.lower()

    def test_validates_cluster_json_format(
        self,
        cli_runner,
        sample_catalog_file,
        sample_ruleset_file,
        sample_cluster_ruleset_file,
        sample_schema_file,
    ):
        """evaluate cluster command outputs JSON format."""
        result = cli_runner.invoke(
            evaluate,
            [
                "cluster",
                "shirt_001",
                "pants_001",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--cluster-rules",
                sample_cluster_ruleset_file,
                "--schema",
                sample_schema_file,
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "item_ids" in data
        assert "is_valid" in data
        assert "pairwise_compatible" in data
        assert "cluster_rules_valid" in data
        assert data["item_ids"] == ["shirt_001", "pants_001"]
        assert data["is_valid"] is True

    def test_validates_cluster_yaml_format(
        self,
        cli_runner,
        sample_catalog_file,
        sample_ruleset_file,
        sample_cluster_ruleset_file,
        sample_schema_file,
    ):
        """evaluate cluster command outputs YAML format."""
        result = cli_runner.invoke(
            evaluate,
            [
                "cluster",
                "shirt_001",
                "pants_001",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--cluster-rules",
                sample_cluster_ruleset_file,
                "--schema",
                sample_schema_file,
                "--format",
                "yaml",
            ],
        )
        assert result.exit_code == 0
        data = yaml.safe_load(result.output)
        assert "item_ids" in data
        assert "is_valid" in data
        assert data["is_valid"] is True

    def test_fails_with_nonexistent_item(
        self,
        cli_runner,
        sample_catalog_file,
        sample_ruleset_file,
        sample_cluster_ruleset_file,
        sample_schema_file,
    ):
        """evaluate cluster command fails when item doesn't exist."""
        result = cli_runner.invoke(
            evaluate,
            [
                "cluster",
                "shirt_001",
                "nonexistent",
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--cluster-rules",
                sample_cluster_ruleset_file,
                "--schema",
                sample_schema_file,
            ],
        )
        assert result.exit_code == 1
        assert "✗ Items not found in catalog" in result.output
        assert "nonexistent" in result.output

    def test_requires_at_least_one_item(self, cli_runner):
        """evaluate cluster command requires at least one item ID."""
        result = cli_runner.invoke(
            evaluate,
            [
                "cluster",
                "--catalog",
                "fake.yaml",
                "--rules",
                "fake.yaml",
                "--cluster-rules",
                "fake.yaml",
            ],
        )
        assert result.exit_code != 0  # Should fail with missing arguments

    def test_validates_three_item_cluster(
        self,
        cli_runner,
        sample_catalog_file,
        sample_ruleset_file,
        sample_cluster_ruleset_file,
        sample_schema_file,
    ):
        """evaluate cluster command validates a 3-item cluster."""
        result = cli_runner.invoke(
            evaluate,
            [
                "cluster",
                "shirt_001",
                "pants_001",
                "shirt_002",  # Added a third item
                "--catalog",
                sample_catalog_file,
                "--rules",
                sample_ruleset_file,
                "--cluster-rules",
                sample_cluster_ruleset_file,
                "--schema",
                sample_schema_file,
            ],
        )
        # Should fail because shirt_001 and shirt_002 are incompatible
        assert result.exit_code == 1
        assert "✗ Invalid cluster" in result.output


# ============================================================================
# SHOW COMMANDS TESTS
# ============================================================================


class TestShowSchema:
    """Tests for 'show schema' command."""

    def test_shows_schema_info(self, cli_runner, sample_schema_file):
        """show schema command displays schema information."""
        result = cli_runner.invoke(show, ["schema", sample_schema_file])
        assert result.exit_code == 0
        assert "test_schema" in result.output
        assert "1.0.0" in result.output
        assert "Dimensions" in result.output
        assert "category" in result.output

    def test_shows_schema_json_format(self, cli_runner, sample_schema_file):
        """show schema command outputs JSON format."""
        result = cli_runner.invoke(show, ["schema", sample_schema_file, "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "test_schema"
        assert data["version"] == "1.0.0"

    def test_fails_with_invalid_schema(self, cli_runner, invalid_schema_file):
        """show schema command fails with invalid schema."""
        result = cli_runner.invoke(show, ["schema", invalid_schema_file])
        assert result.exit_code == 1


class TestShowCatalog:
    """Tests for 'show catalog' command."""

    def test_shows_catalog_info(self, cli_runner, sample_catalog_file):
        """show catalog command displays catalog information."""
        result = cli_runner.invoke(show, ["catalog", sample_catalog_file])
        assert result.exit_code == 0
        assert "test_catalog" in result.output
        assert "Items" in result.output
        assert "shirt_001" in result.output
        assert "Blue Shirt" in result.output

    def test_shows_catalog_json_format(self, cli_runner, sample_catalog_file):
        """show catalog command outputs JSON format."""
        result = cli_runner.invoke(show, ["catalog", sample_catalog_file, "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "test_catalog"
        assert len(data["items"]) == 3

    def test_shows_catalog_table_format(self, cli_runner, sample_catalog_file):
        """show catalog command displays table format."""
        result = cli_runner.invoke(show, ["catalog", sample_catalog_file, "--format", "table"])
        assert result.exit_code == 0
        assert "shirt_001" in result.output
        assert "Blue Shirt" in result.output
        assert "ID" in result.output and "Name" in result.output  # Table headers

    def test_fails_with_invalid_catalog(self, cli_runner, invalid_schema_file):
        """show catalog command fails with invalid catalog."""
        result = cli_runner.invoke(show, ["catalog", invalid_schema_file])
        assert result.exit_code == 1


# ============================================================================
# MAIN CLI TESTS
# ============================================================================


class TestMainCLI:
    """Tests for main CLI group."""

    def test_main_help(self, cli_runner):
        """Main CLI shows help message."""
        result = cli_runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Rulate" in result.output
        assert "validate" in result.output
        assert "evaluate" in result.output
        assert "show" in result.output

    def test_main_version(self, cli_runner):
        """Main CLI shows version."""
        result = cli_runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_validate_help(self, cli_runner):
        """validate command group shows help."""
        result = cli_runner.invoke(validate, ["--help"])
        assert result.exit_code == 0
        assert "schema" in result.output
        assert "rules" in result.output
        assert "catalog" in result.output

    def test_evaluate_help(self, cli_runner):
        """evaluate command group shows help."""
        result = cli_runner.invoke(evaluate, ["--help"])
        assert result.exit_code == 0
        assert "pair" in result.output
        assert "matrix" in result.output
        assert "item" in result.output
        assert "cluster" in result.output

    def test_show_help(self, cli_runner):
        """show command group shows help."""
        result = cli_runner.invoke(show, ["--help"])
        assert result.exit_code == 0
        assert "schema" in result.output
        assert "catalog" in result.output
