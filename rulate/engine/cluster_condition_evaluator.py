"""
Cluster condition evaluator for parsing and evaluating cluster-level rule conditions.

This module handles converting cluster condition dictionaries into cluster operator instances
and evaluating them against lists of items (clusters).
"""

from typing import Any, Dict, List, Tuple

from rulate.engine.operators import CLUSTER_OPERATOR_REGISTRY
from rulate.models.catalog import Item


def evaluate_cluster_condition(
    condition: Dict[str, Any], items: List[Item]
) -> Tuple[bool, str]:
    """
    Evaluate a cluster condition dictionary against a list of items.

    Args:
        condition: Condition dictionary (e.g., {"min_cluster_size": 3})
        items: List of items forming a cluster

    Returns:
        Tuple of (result, explanation)

    Raises:
        ValueError: If condition format is invalid or operator is unknown
    """
    if not isinstance(condition, dict):
        raise ValueError(f"Condition must be a dictionary, got {type(condition)}")

    if len(condition) == 0:
        raise ValueError("Condition cannot be empty")

    # Condition should have exactly one operator key
    if len(condition) > 1:
        raise ValueError(
            f"Condition must have exactly one operator, got {list(condition.keys())}"
        )

    operator_name = list(condition.keys())[0]
    operator_config = condition[operator_name]

    # Look up operator class
    operator_class = CLUSTER_OPERATOR_REGISTRY.get(operator_name)
    if not operator_class:
        raise ValueError(
            f"Unknown cluster operator '{operator_name}'. "
            f"Available: {list(CLUSTER_OPERATOR_REGISTRY.keys())}"
        )

    # Create operator instance and evaluate
    try:
        operator = operator_class(operator_config)
        return operator.evaluate(items)
    except Exception as e:
        return False, f"Error evaluating {operator_name}: {str(e)}"


def validate_cluster_condition(condition: Dict[str, Any]) -> bool:
    """
    Validate that a cluster condition has proper structure.

    Args:
        condition: Condition dictionary to validate

    Returns:
        True if valid

    Raises:
        ValueError: If condition is invalid
    """
    if not isinstance(condition, dict):
        raise ValueError("Condition must be a dictionary")

    if len(condition) == 0:
        raise ValueError("Condition cannot be empty")

    if len(condition) > 1:
        raise ValueError("Condition must have exactly one operator")

    operator_name = list(condition.keys())[0]
    if operator_name not in CLUSTER_OPERATOR_REGISTRY:
        raise ValueError(
            f"Unknown cluster operator '{operator_name}'. "
            f"Available: {list(CLUSTER_OPERATOR_REGISTRY.keys())}"
        )

    # For logical operators, recursively validate sub-conditions
    if operator_name in ["all", "any", "or"]:
        operator_config = condition[operator_name]
        if not isinstance(operator_config, list):
            raise ValueError(f"Operator '{operator_name}' requires a list of conditions")
        for sub_condition in operator_config:
            validate_cluster_condition(sub_condition)
    elif operator_name == "not":
        operator_config = condition[operator_name]
        validate_cluster_condition(operator_config)

    return True
