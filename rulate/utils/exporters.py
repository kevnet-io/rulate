"""
Utilities for exporting schemas, rules, and catalogs to YAML/JSON files.

These functions handle converting Pydantic models back into file formats.
"""

import json
from pathlib import Path
from typing import Union

import yaml

from rulate.models.catalog import Catalog
from rulate.models.evaluation import ComparisonResult, EvaluationMatrix
from rulate.models.rule import RuleSet
from rulate.models.schema import Schema


def export_to_yaml(obj: Union[Schema, RuleSet, Catalog], file_path: Union[str, Path]) -> None:
    """
    Export a model object to a YAML file.

    Args:
        obj: The object to export (Schema, RuleSet, or Catalog)
        file_path: Path where the YAML file should be written

    Raises:
        IOError: If the file cannot be written

    Example:
        export_to_yaml(schema, "output/schema.yaml")
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert Pydantic model to dict, excluding defaults where possible
    data = obj.model_dump(mode="python", exclude_none=False)

    try:
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                indent=2,
            )
    except Exception as e:
        raise IOError(f"Failed to write YAML to {file_path}: {e}")


def export_to_json(
    obj: Union[Schema, RuleSet, Catalog, ComparisonResult, EvaluationMatrix],
    file_path: Union[str, Path],
    indent: int = 2,
) -> None:
    """
    Export a model object to a JSON file.

    Args:
        obj: The object to export
        file_path: Path where the JSON file should be written
        indent: Number of spaces for indentation (default: 2)

    Raises:
        IOError: If the file cannot be written

    Example:
        export_to_json(catalog, "output/catalog.json")
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert Pydantic model to JSON-serializable dict
    data = obj.model_dump(mode="python")

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
    except Exception as e:
        raise IOError(f"Failed to write JSON to {file_path}: {e}")


def to_yaml_string(obj: Union[Schema, RuleSet, Catalog]) -> str:
    """
    Convert a model object to a YAML string.

    Args:
        obj: The object to convert

    Returns:
        YAML representation as a string

    Example:
        yaml_str = to_yaml_string(schema)
        print(yaml_str)
    """
    data = obj.model_dump(mode="python", exclude_none=False)
    return yaml.dump(
        data, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2
    )


def to_json_string(
    obj: Union[Schema, RuleSet, Catalog, ComparisonResult, EvaluationMatrix], indent: int = 2
) -> str:
    """
    Convert a model object to a JSON string.

    Args:
        obj: The object to convert
        indent: Number of spaces for indentation (default: 2)

    Returns:
        JSON representation as a string

    Example:
        json_str = to_json_string(catalog)
        print(json_str)
    """
    data = obj.model_dump(mode="python")
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)


def export_evaluation_matrix_to_csv(matrix: EvaluationMatrix, file_path: Union[str, Path]) -> None:
    """
    Export an evaluation matrix to CSV format.

    Creates a matrix-style CSV where rows and columns are item IDs
    and cells contain compatibility (1 for compatible, 0 for incompatible).

    Args:
        matrix: The EvaluationMatrix to export
        file_path: Path where the CSV file should be written

    Raises:
        IOError: If the file cannot be written

    Example:
        export_evaluation_matrix_to_csv(matrix, "output/compatibility.csv")
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Collect all unique item IDs
    item_ids = set()
    for result in matrix.results:
        item_ids.add(result.item1_id)
        item_ids.add(result.item2_id)
    item_ids = sorted(item_ids)

    # Build compatibility lookup
    compat_lookup = {}
    for result in matrix.results:
        key1 = (result.item1_id, result.item2_id)
        key2 = (result.item2_id, result.item1_id)
        value = 1 if result.compatible else 0
        compat_lookup[key1] = value
        compat_lookup[key2] = value

    try:
        with open(path, "w", encoding="utf-8") as f:
            # Write header
            f.write("," + ",".join(item_ids) + "\n")

            # Write rows
            for row_id in item_ids:
                row = [row_id]
                for col_id in item_ids:
                    if row_id == col_id:
                        row.append("1")  # Item is compatible with itself
                    else:
                        value = compat_lookup.get((row_id, col_id), "")
                        row.append(str(value))
                f.write(",".join(row) + "\n")
    except Exception as e:
        raise IOError(f"Failed to write CSV to {file_path}: {e}")
