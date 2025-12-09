"""
Utilities for loading schemas, rules, and catalogs from YAML/JSON files.

These functions handle parsing file formats and converting them into Pydantic models.
"""

import json
from pathlib import Path
from typing import Any

import yaml

from rulate.models.catalog import Catalog
from rulate.models.cluster import ClusterRuleSet
from rulate.models.rule import RuleSet
from rulate.models.schema import Schema


def load_yaml_or_json(file_path: str | Path) -> dict[str, Any]:
    """
    Load a YAML or JSON file and return its contents as a dictionary.

    Args:
        file_path: Path to the file (can be .yaml, .yml, or .json)

    Returns:
        Dictionary representation of the file contents

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is unsupported or invalid
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()

    try:
        with open(path, encoding="utf-8") as f:
            if suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    raise ValueError(f"Expected dictionary in {file_path}, got {type(data)}")
                return data
            elif suffix == ".json":
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError(f"Expected dictionary in {file_path}, got {type(data)}")
                return data
            else:
                raise ValueError(
                    f"Unsupported file format: {suffix}. Use .yaml, .yml, or .json"
                )
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {file_path}: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {file_path}: {e}")


def load_schema(file_path: str | Path) -> Schema:
    """
    Load a schema from a YAML or JSON file.

    Args:
        file_path: Path to the schema file

    Returns:
        A validated Schema object

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is invalid or schema validation fails

    Example:
        schema = load_schema("examples/wardrobe/schema.yaml")
    """
    data = load_yaml_or_json(file_path)
    try:
        return Schema(**data)
    except Exception as e:
        raise ValueError(f"Failed to load schema from {file_path}: {e}")


def load_ruleset(file_path: str | Path) -> RuleSet:
    """
    Load a ruleset from a YAML or JSON file.

    Args:
        file_path: Path to the ruleset file

    Returns:
        A validated RuleSet object

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is invalid or ruleset validation fails

    Example:
        ruleset = load_ruleset("examples/wardrobe/rules.yaml")
    """
    data = load_yaml_or_json(file_path)
    try:
        return RuleSet(**data)
    except Exception as e:
        raise ValueError(f"Failed to load ruleset from {file_path}: {e}")


def load_catalog(file_path: str | Path) -> Catalog:
    """
    Load a catalog from a YAML or JSON file.

    Args:
        file_path: Path to the catalog file

    Returns:
        A validated Catalog object

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is invalid or catalog validation fails

    Example:
        catalog = load_catalog("examples/wardrobe/catalog.yaml")
    """
    data = load_yaml_or_json(file_path)
    try:
        return Catalog(**data)
    except Exception as e:
        raise ValueError(f"Failed to load catalog from {file_path}: {e}")


def load_schema_from_string(content: str, format: str = "yaml") -> Schema:
    """
    Load a schema from a string.

    Args:
        content: The schema content as a string
        format: Either "yaml" or "json"

    Returns:
        A validated Schema object

    Raises:
        ValueError: If the content is invalid
    """
    try:
        if format == "yaml":
            data = yaml.safe_load(content)
        elif format == "json":
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported format: {format}")
        return Schema(**data)
    except Exception as e:
        raise ValueError(f"Failed to load schema from string: {e}")


def load_ruleset_from_string(content: str, format: str = "yaml") -> RuleSet:
    """
    Load a ruleset from a string.

    Args:
        content: The ruleset content as a string
        format: Either "yaml" or "json"

    Returns:
        A validated RuleSet object

    Raises:
        ValueError: If the content is invalid
    """
    try:
        if format == "yaml":
            data = yaml.safe_load(content)
        elif format == "json":
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported format: {format}")
        return RuleSet(**data)
    except Exception as e:
        raise ValueError(f"Failed to load ruleset from string: {e}")


def load_catalog_from_string(content: str, format: str = "yaml") -> Catalog:
    """
    Load a catalog from a string.

    Args:
        content: The catalog content as a string
        format: Either "yaml" or "json"

    Returns:
        A validated Catalog object

    Raises:
        ValueError: If the content is invalid
    """
    try:
        if format == "yaml":
            data = yaml.safe_load(content)
        elif format == "json":
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported format: {format}")
        return Catalog(**data)
    except Exception as e:
        raise ValueError(f"Failed to load catalog from string: {e}")


def load_cluster_ruleset(file_path: str | Path) -> ClusterRuleSet:
    """
    Load a cluster ruleset from a YAML or JSON file.

    Args:
        file_path: Path to the cluster ruleset file

    Returns:
        A validated ClusterRuleSet object

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is invalid or cluster ruleset validation fails

    Example:
        cluster_ruleset = load_cluster_ruleset("examples/wardrobe/cluster_rules.yaml")
    """
    data = load_yaml_or_json(file_path)
    try:
        return ClusterRuleSet(**data)
    except Exception as e:
        raise ValueError(f"Failed to load cluster ruleset from {file_path}: {e}")


def load_cluster_ruleset_from_string(content: str, format: str = "yaml") -> ClusterRuleSet:
    """
    Load a cluster ruleset from a string.

    Args:
        content: The cluster ruleset content as a string
        format: Either "yaml" or "json"

    Returns:
        A validated ClusterRuleSet object

    Raises:
        ValueError: If the content is invalid
    """
    try:
        if format == "yaml":
            data = yaml.safe_load(content)
        elif format == "json":
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported format: {format}")
        return ClusterRuleSet(**data)
    except Exception as e:
        raise ValueError(f"Failed to load cluster ruleset from string: {e}")
