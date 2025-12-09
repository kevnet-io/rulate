"""
Condition evaluator for parsing and evaluating rule conditions.

This module handles converting condition dictionaries into operator instances
and evaluating them against item pairs.
"""

from typing import Any

from rulate.engine.operators import OPERATOR_REGISTRY, Operator
from rulate.models.catalog import Item


def evaluate_condition(condition: dict[str, Any], item1: Item, item2: Item) -> tuple[bool, str]:
    """
    Evaluate a condition dictionary against two items.

    Args:
        condition: Condition dictionary (e.g., {"equals": {"field": "body_zone"}})
        item1: First item
        item2: Second item

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
    operator_class: type[Operator] | None = OPERATOR_REGISTRY.get(operator_name)
    if not operator_class:
        raise ValueError(
            f"Unknown operator '{operator_name}'. "
            f"Available: {list(OPERATOR_REGISTRY.keys())}"
        )

    # Create operator instance and evaluate
    try:
        operator = operator_class(operator_config)
        return operator.evaluate(item1, item2)
    except Exception as e:
        return False, f"Error evaluating {operator_name}: {str(e)}"


def validate_condition(condition: dict[str, Any]) -> bool:
    """
    Validate that a condition has proper structure.

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
    if operator_name not in OPERATOR_REGISTRY:
        raise ValueError(
            f"Unknown operator '{operator_name}'. "
            f"Available: {list(OPERATOR_REGISTRY.keys())}"
        )

    # For logical operators, recursively validate sub-conditions
    if operator_name in ["all", "any", "or"]:
        operator_config = condition[operator_name]
        if not isinstance(operator_config, list):
            raise ValueError(f"Operator '{operator_name}' requires a list of conditions")
        for sub_condition in operator_config:
            validate_condition(sub_condition)
    elif operator_name == "not":
        operator_config = condition[operator_name]
        validate_condition(operator_config)

    return True
