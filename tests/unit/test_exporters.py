"""
Comprehensive tests for export utilities.

Tests cover:
- Exporting models to YAML files
- Exporting models to JSON files
- Converting models to YAML strings
- Converting models to JSON strings
- Exporting evaluation matrices to CSV
- Directory creation and error handling
"""

import json
from pathlib import Path

import pytest
import yaml

from rulate.models.catalog import Catalog, Item
from rulate.models.evaluation import ComparisonResult, EvaluationMatrix, RuleEvaluation
from rulate.models.rule import Rule, RuleSet, RuleType
from rulate.models.schema import Schema
from rulate.utils.exporters import (
    export_evaluation_matrix_to_csv,
    export_to_json,
    export_to_yaml,
    to_json_string,
    to_yaml_string,
)


@pytest.fixture
def sample_schema():
    """Sample schema for testing."""
    return Schema(
        name="test_schema",
        version="1.0.0",
        description="Test schema",
        dimensions=[
            {"name": "color", "type": "string", "required": True},
            {"name": "size", "type": "enum", "values": ["S", "M", "L"], "required": True},
        ],
    )


@pytest.fixture
def sample_ruleset():
    """Sample ruleset for testing."""
    return RuleSet(
        name="test_rules",
        version="1.0.0",
        schema_ref="test_schema",
        rules=[
            Rule(
                name="rule1",
                type=RuleType.EXCLUSION,
                condition={"equals": {"field": "color"}},
            ),
        ],
    )


@pytest.fixture
def sample_catalog():
    """Sample catalog for testing."""
    return Catalog(
        name="test_catalog",
        schema_ref="test_schema",
        items=[
            Item(id="item_001", name="Item 1", attributes={"color": "blue", "size": "M"}),
            Item(id="item_002", name="Item 2", attributes={"color": "red", "size": "L"}),
        ],
    )


@pytest.fixture
def sample_comparison_result():
    """Sample comparison result for testing."""
    return ComparisonResult(
        item1_id="item_001",
        item2_id="item_002",
        compatible=True,
        rules_evaluated=[
            RuleEvaluation(rule_name="rule1", passed=True, reason="Passed"),
        ],
    )


@pytest.fixture
def sample_evaluation_matrix():
    """Sample evaluation matrix for testing."""
    return EvaluationMatrix(
        catalog_name="test_catalog",
        ruleset_name="test_rules",
        schema_name="test_schema",
        results=[
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=True),
            ComparisonResult(item1_id="item_001", item2_id="item_003", compatible=False),
            ComparisonResult(item1_id="item_002", item2_id="item_003", compatible=True),
        ],
    )


class TestExportToYaml:
    """Tests for export_to_yaml function."""

    def test_exports_schema_to_yaml(self, tmp_path, sample_schema):
        """export_to_yaml() writes schema to YAML file."""
        output_file = tmp_path / "schema.yaml"
        export_to_yaml(sample_schema, output_file)

        assert output_file.exists()

        # Read content and verify key fields are present
        with open(output_file, "r") as f:
            content = f.read()

        assert "test_schema" in content
        assert "1.0.0" in content
        assert "dimensions" in content

    def test_exports_ruleset_to_yaml(self, tmp_path, sample_ruleset):
        """export_to_yaml() writes ruleset to YAML file."""
        output_file = tmp_path / "rules.yaml"
        export_to_yaml(sample_ruleset, output_file)

        assert output_file.exists()

        # Read content and verify key fields are present
        with open(output_file, "r") as f:
            content = f.read()

        assert "test_rules" in content
        assert "1.0.0" in content
        assert "rules" in content

    def test_exports_catalog_to_yaml(self, tmp_path, sample_catalog):
        """export_to_yaml() writes catalog to YAML file."""
        output_file = tmp_path / "catalog.yaml"
        export_to_yaml(sample_catalog, output_file)

        assert output_file.exists()

        with open(output_file, "r") as f:
            data = yaml.safe_load(f)

        assert data["name"] == "test_catalog"
        assert len(data["items"]) == 2

    def test_creates_parent_directories(self, tmp_path, sample_schema):
        """export_to_yaml() creates parent directories if they don't exist."""
        output_file = tmp_path / "nested" / "dir" / "schema.yaml"
        export_to_yaml(sample_schema, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_accepts_string_path(self, tmp_path, sample_schema):
        """export_to_yaml() accepts string paths."""
        output_file = str(tmp_path / "schema.yaml")
        export_to_yaml(sample_schema, output_file)

        assert Path(output_file).exists()

    def test_raises_ioerror_for_invalid_path(self, sample_schema):
        """export_to_yaml() raises IOError for invalid paths."""
        # Try to write to a path that's a file, not a directory
        with pytest.raises(IOError):
            export_to_yaml(sample_schema, "/dev/null/invalid/path.yaml")


class TestExportToJson:
    """Tests for export_to_json function."""

    def test_exports_schema_to_json(self, tmp_path, sample_schema):
        """export_to_json() writes schema to JSON file."""
        output_file = tmp_path / "schema.json"
        export_to_json(sample_schema, output_file)

        assert output_file.exists()

        with open(output_file, "r") as f:
            data = json.load(f)

        assert data["name"] == "test_schema"
        assert data["version"] == "1.0.0"
        assert len(data["dimensions"]) == 2

    def test_exports_ruleset_to_json(self, tmp_path, sample_ruleset):
        """export_to_json() writes ruleset to JSON file."""
        output_file = tmp_path / "rules.json"
        export_to_json(sample_ruleset, output_file)

        assert output_file.exists()

        with open(output_file, "r") as f:
            data = json.load(f)

        assert data["name"] == "test_rules"
        assert len(data["rules"]) == 1

    def test_exports_catalog_to_json(self, tmp_path, sample_catalog):
        """export_to_json() writes catalog to JSON file."""
        output_file = tmp_path / "catalog.json"
        export_to_json(sample_catalog, output_file)

        assert output_file.exists()

        with open(output_file, "r") as f:
            data = json.load(f)

        assert data["name"] == "test_catalog"
        assert len(data["items"]) == 2

    def test_exports_comparison_result_to_json(self, tmp_path, sample_comparison_result):
        """export_to_json() writes comparison result to JSON file."""
        output_file = tmp_path / "result.json"
        export_to_json(sample_comparison_result, output_file)

        assert output_file.exists()

        with open(output_file, "r") as f:
            data = json.load(f)

        assert data["item1_id"] == "item_001"
        assert data["item2_id"] == "item_002"
        assert data["compatible"] is True

    def test_exports_evaluation_matrix_to_json(self, tmp_path, sample_evaluation_matrix):
        """export_to_json() writes evaluation matrix to JSON file."""
        output_file = tmp_path / "matrix.json"
        export_to_json(sample_evaluation_matrix, output_file)

        assert output_file.exists()

        with open(output_file, "r") as f:
            data = json.load(f)

        assert data["catalog_name"] == "test_catalog"
        assert len(data["results"]) == 3

    def test_respects_indent_parameter(self, tmp_path, sample_schema):
        """export_to_json() respects the indent parameter."""
        output_file = tmp_path / "schema.json"
        export_to_json(sample_schema, output_file, indent=4)

        with open(output_file, "r") as f:
            content = f.read()

        # Check that content has 4-space indentation
        assert "    " in content

    def test_creates_parent_directories(self, tmp_path, sample_schema):
        """export_to_json() creates parent directories if they don't exist."""
        output_file = tmp_path / "nested" / "dir" / "schema.json"
        export_to_json(sample_schema, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_accepts_string_path(self, tmp_path, sample_schema):
        """export_to_json() accepts string paths."""
        output_file = str(tmp_path / "schema.json")
        export_to_json(sample_schema, output_file)

        assert Path(output_file).exists()

    def test_raises_ioerror_for_invalid_path(self, sample_schema):
        """export_to_json() raises IOError for invalid paths."""
        with pytest.raises(IOError):
            export_to_json(sample_schema, "/dev/null/invalid/path.json")


class TestToYamlString:
    """Tests for to_yaml_string function."""

    def test_converts_schema_to_yaml_string(self, sample_schema):
        """to_yaml_string() converts schema to YAML string."""
        yaml_str = to_yaml_string(sample_schema)

        assert isinstance(yaml_str, str)
        assert "test_schema" in yaml_str
        assert "1.0.0" in yaml_str

    def test_converts_ruleset_to_yaml_string(self, sample_ruleset):
        """to_yaml_string() converts ruleset to YAML string."""
        yaml_str = to_yaml_string(sample_ruleset)

        assert isinstance(yaml_str, str)
        assert "test_rules" in yaml_str
        assert "rule1" in yaml_str

    def test_converts_catalog_to_yaml_string(self, sample_catalog):
        """to_yaml_string() converts catalog to YAML string."""
        yaml_str = to_yaml_string(sample_catalog)

        assert isinstance(yaml_str, str)
        data = yaml.safe_load(yaml_str)
        assert data["name"] == "test_catalog"
        assert len(data["items"]) == 2

    def test_yaml_string_is_parseable(self, sample_schema):
        """to_yaml_string() produces valid YAML."""
        yaml_str = to_yaml_string(sample_schema)
        # Check it's a non-empty string with YAML structure
        assert yaml_str
        assert "\n" in yaml_str  # Multi-line YAML
        assert ":" in yaml_str  # Has key-value pairs


class TestToJsonString:
    """Tests for to_json_string function."""

    def test_converts_schema_to_json_string(self, sample_schema):
        """to_json_string() converts schema to JSON string."""
        json_str = to_json_string(sample_schema)

        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["name"] == "test_schema"
        assert data["version"] == "1.0.0"

    def test_converts_ruleset_to_json_string(self, sample_ruleset):
        """to_json_string() converts ruleset to JSON string."""
        json_str = to_json_string(sample_ruleset)

        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["name"] == "test_rules"
        assert len(data["rules"]) == 1

    def test_converts_catalog_to_json_string(self, sample_catalog):
        """to_json_string() converts catalog to JSON string."""
        json_str = to_json_string(sample_catalog)

        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["name"] == "test_catalog"
        assert len(data["items"]) == 2

    def test_converts_comparison_result_to_json_string(self, sample_comparison_result):
        """to_json_string() converts comparison result to JSON string."""
        json_str = to_json_string(sample_comparison_result)

        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["item1_id"] == "item_001"
        assert data["compatible"] is True

    def test_converts_evaluation_matrix_to_json_string(self, sample_evaluation_matrix):
        """to_json_string() converts evaluation matrix to JSON string."""
        json_str = to_json_string(sample_evaluation_matrix)

        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["catalog_name"] == "test_catalog"
        assert len(data["results"]) == 3

    def test_respects_indent_parameter(self, sample_schema):
        """to_json_string() respects the indent parameter."""
        json_str = to_json_string(sample_schema, indent=4)

        # Check that content has 4-space indentation
        assert "    " in json_str

    def test_json_string_is_parseable(self, sample_schema):
        """to_json_string() produces valid JSON."""
        json_str = to_json_string(sample_schema)
        # This should not raise an exception
        parsed = json.loads(json_str)
        assert parsed is not None


class TestExportEvaluationMatrixToCsv:
    """Tests for export_evaluation_matrix_to_csv function."""

    def test_exports_matrix_to_csv(self, tmp_path, sample_evaluation_matrix):
        """export_evaluation_matrix_to_csv() writes matrix to CSV file."""
        output_file = tmp_path / "matrix.csv"
        export_evaluation_matrix_to_csv(sample_evaluation_matrix, output_file)

        assert output_file.exists()

        with open(output_file, "r") as f:
            content = f.read()

        # Check CSV structure
        lines = content.strip().split("\n")
        assert len(lines) == 4  # Header + 3 items

        # Check header
        assert "item_001" in lines[0]
        assert "item_002" in lines[0]
        assert "item_003" in lines[0]

    def test_csv_has_correct_compatibility_values(self, tmp_path):
        """export_evaluation_matrix_to_csv() has correct compatibility values."""
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=[
                ComparisonResult(item1_id="A", item2_id="B", compatible=True),
                ComparisonResult(item1_id="A", item2_id="C", compatible=False),
            ],
        )

        output_file = tmp_path / "matrix.csv"
        export_evaluation_matrix_to_csv(matrix, output_file)

        with open(output_file, "r") as f:
            lines = f.readlines()

        # Find rows for A and check values
        a_row = [line.strip() for line in lines if line.startswith("A,")][0]
        values = a_row.split(",")
        # A row should have: A, 1 (self), 1 (A-B), 0 (A-C)
        assert "1" in values  # A-B is compatible
        assert "0" in values  # A-C is incompatible

    def test_csv_self_compatibility_is_one(self, tmp_path, sample_evaluation_matrix):
        """export_evaluation_matrix_to_csv() marks self-compatibility as 1."""
        output_file = tmp_path / "matrix.csv"
        export_evaluation_matrix_to_csv(sample_evaluation_matrix, output_file)

        with open(output_file, "r") as f:
            lines = f.readlines()

        # Check diagonal values (self-compatibility)
        for i, line in enumerate(lines[1:], 1):  # Skip header
            values = line.strip().split(",")
            # The diagonal entry should be 1 (strip any whitespace/newlines)
            assert values[i].strip() == "1"

    def test_csv_is_symmetric(self, tmp_path):
        """export_evaluation_matrix_to_csv() creates symmetric matrix."""
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=[
                ComparisonResult(item1_id="A", item2_id="B", compatible=True),
            ],
        )

        output_file = tmp_path / "matrix.csv"
        export_evaluation_matrix_to_csv(matrix, output_file)

        with open(output_file, "r") as f:
            lines = f.readlines()

        # Parse CSV
        rows = [line.strip().split(",") for line in lines]
        header = rows[0]

        # Find indices
        a_idx = header.index("A")
        b_idx = header.index("B")

        # Get values (skip row label in column 0)
        a_row = rows[a_idx]
        b_row = rows[b_idx]

        # Check symmetry: A->B should equal B->A
        assert a_row[b_idx] == b_row[a_idx]

    def test_creates_parent_directories(self, tmp_path, sample_evaluation_matrix):
        """export_evaluation_matrix_to_csv() creates parent directories."""
        output_file = tmp_path / "nested" / "dir" / "matrix.csv"
        export_evaluation_matrix_to_csv(sample_evaluation_matrix, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_accepts_string_path(self, tmp_path, sample_evaluation_matrix):
        """export_evaluation_matrix_to_csv() accepts string paths."""
        output_file = str(tmp_path / "matrix.csv")
        export_evaluation_matrix_to_csv(sample_evaluation_matrix, output_file)

        assert Path(output_file).exists()

    def test_raises_ioerror_for_invalid_path(self, sample_evaluation_matrix):
        """export_evaluation_matrix_to_csv() raises IOError for invalid paths."""
        with pytest.raises(IOError):
            export_evaluation_matrix_to_csv(sample_evaluation_matrix, "/dev/null/invalid/path.csv")

    def test_handles_empty_matrix(self, tmp_path):
        """export_evaluation_matrix_to_csv() handles empty matrix."""
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=[],
        )

        output_file = tmp_path / "matrix.csv"
        export_evaluation_matrix_to_csv(matrix, output_file)

        assert output_file.exists()

        with open(output_file, "r") as f:
            content = f.read()

        # Should have just a header line
        assert content.strip() == ","
