"""
Operators for evaluating rule conditions against item pairs.

Operators are the building blocks of rule conditions. They take two items
and return a boolean result plus an explanation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from rulate.models.catalog import Item


class Operator(ABC):
    """
    Base class for all operators.

    Operators evaluate conditions against two items and return a boolean result
    plus a human-readable explanation.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the operator with configuration.

        Args:
            config: Configuration dictionary from the rule condition
        """
        self.config = config

    @abstractmethod
    def evaluate(self, item1: Item, item2: Item) -> Tuple[bool, str]:
        """
        Evaluate the condition against two items.

        Args:
            item1: First item
            item2: Second item

        Returns:
            Tuple of (result, explanation)
            - result: True if condition is met, False otherwise
            - explanation: Human-readable explanation of the result
        """
        pass


# Field Comparison Operators


class EqualsOperator(Operator):
    """
    Check if both items have the same value for a field.

    Config:
        field: The field name to compare

    Example:
        {"equals": {"field": "body_zone"}}
        Returns True if both items have the same body_zone value
    """

    def evaluate(self, item1: Item, item2: Item) -> Tuple[bool, str]:
        field = self.config.get("field")
        if not field:
            return False, "No field specified for equals operator"

        value1 = item1.get_attribute(field)
        value2 = item2.get_attribute(field)

        if value1 is None or value2 is None:
            return False, f"One or both items missing '{field}' attribute"

        result = value1 == value2
        if result:
            return True, f"Both items have {field}='{value1}'"
        else:
            return False, f"Different {field} values: '{value1}' vs '{value2}'"


class HasDifferentOperator(Operator):
    """
    Check if both items have different values for a field.

    Config:
        field: The field name to compare

    Example:
        {"has_different": {"field": "layer"}}
        Returns True if items have different layer values
    """

    def evaluate(self, item1: Item, item2: Item) -> Tuple[bool, str]:
        field = self.config.get("field")
        if not field:
            return False, "No field specified for has_different operator"

        value1 = item1.get_attribute(field)
        value2 = item2.get_attribute(field)

        if value1 is None or value2 is None:
            return True, f"One or both items missing '{field}' attribute (treated as different)"

        result = value1 != value2
        if result:
            return True, f"Different {field} values: '{value1}' vs '{value2}'"
        else:
            return False, f"Same {field} value: '{value1}'"


class AbsDiffOperator(Operator):
    """
    Check if absolute difference between numeric values is within a threshold.

    Config:
        field: The field name to compare
        max: Maximum allowed difference

    Example:
        {"abs_diff": {"field": "formality", "max": 2}}
        Returns True if formality difference is <= 2
    """

    def evaluate(self, item1: Item, item2: Item) -> Tuple[bool, str]:
        field = self.config.get("field")
        max_diff = self.config.get("max")

        if not field:
            return False, "No field specified for abs_diff operator"
        if max_diff is None:
            return False, "No max specified for abs_diff operator"

        value1 = item1.get_attribute(field)
        value2 = item2.get_attribute(field)

        if value1 is None or value2 is None:
            return False, f"One or both items missing '{field}' attribute"

        try:
            diff = abs(float(value1) - float(value2))
            result = diff <= max_diff
            if result:
                return True, f"{field} difference {diff:.1f} is within threshold {max_diff}"
            else:
                return False, f"{field} difference {diff:.1f} exceeds threshold {max_diff}"
        except (ValueError, TypeError):
            return False, f"Cannot compute numeric difference for {field}"


class AnyEqualsOperator(Operator):
    """
    Check if either item has a specific value for a field.

    Config:
        field: The field name to check
        value: The value to match

    Example:
        {"any_equals": {"field": "season", "value": "all_season"}}
        Returns True if either item has season="all_season"
    """

    def evaluate(self, item1: Item, item2: Item) -> Tuple[bool, str]:
        field = self.config.get("field")
        target_value = self.config.get("value")

        if not field:
            return False, "No field specified for any_equals operator"
        if target_value is None:
            return False, "No value specified for any_equals operator"

        value1 = item1.get_attribute(field)
        value2 = item2.get_attribute(field)

        if value1 == target_value or value2 == target_value:
            return True, f"At least one item has {field}='{target_value}'"
        else:
            return False, f"Neither item has {field}='{target_value}' (values: '{value1}', '{value2}')"


class AnyMissingOperator(Operator):
    """
    Check if either item is missing a field.

    Config:
        field: The field name to check

    Example:
        {"any_missing": {"field": "formality"}}
        Returns True if either item doesn't have a formality value
    """

    def evaluate(self, item1: Item, item2: Item) -> Tuple[bool, str]:
        field = self.config.get("field")

        if not field:
            return False, "No field specified for any_missing operator"

        value1 = item1.get_attribute(field)
        value2 = item2.get_attribute(field)

        if value1 is None or value2 is None:
            return True, f"At least one item is missing '{field}' attribute"
        else:
            return False, f"Both items have '{field}' attribute"


# Logical Operators


class AllOperator(Operator):
    """
    Logical AND - all sub-conditions must be true.

    Config:
        List of sub-condition dictionaries

    Example:
        {"all": [
            {"equals": {"field": "body_zone"}},
            {"has_different": {"field": "layer"}}
        ]}
    """

    def __init__(self, config: Any):
        # For AllOperator, config is a list of conditions
        self.conditions = config if isinstance(config, list) else []

    def evaluate(self, item1: Item, item2: Item) -> Tuple[bool, str]:
        if not self.conditions:
            return False, "No conditions specified for 'all' operator"

        from rulate.engine.condition_evaluator import evaluate_condition

        results = []
        for condition in self.conditions:
            result, reason = evaluate_condition(condition, item1, item2)
            results.append((result, reason))
            if not result:
                return False, f"AND failed: {reason}"

        return True, "All conditions passed"


class AnyOperator(Operator):
    """
    Logical OR - at least one sub-condition must be true.

    Config:
        List of sub-condition dictionaries

    Example:
        {"any": [
            {"equals": {"field": "season"}},
            {"any_equals": {"field": "season", "value": "all_season"}}
        ]}
    """

    def __init__(self, config: Any):
        # For AnyOperator, config is a list of conditions
        self.conditions = config if isinstance(config, list) else []

    def evaluate(self, item1: Item, item2: Item) -> Tuple[bool, str]:
        if not self.conditions:
            return False, "No conditions specified for 'any' operator"

        from rulate.engine.condition_evaluator import evaluate_condition

        reasons = []
        for condition in self.conditions:
            result, reason = evaluate_condition(condition, item1, item2)
            if result:
                return True, f"OR succeeded: {reason}"
            reasons.append(reason)

        return False, f"All OR conditions failed: {'; '.join(reasons)}"


class NotOperator(Operator):
    """
    Logical NOT - negate a condition.

    Config:
        Single sub-condition dictionary

    Example:
        {"not": {"equals": {"field": "category"}}}
    """

    def __init__(self, config: Any):
        self.condition = config

    def evaluate(self, item1: Item, item2: Item) -> Tuple[bool, str]:
        if not self.condition:
            return False, "No condition specified for 'not' operator"

        from rulate.engine.condition_evaluator import evaluate_condition

        result, reason = evaluate_condition(self.condition, item1, item2)
        return not result, f"NOT {reason}"


# Operator registry for lookup
OPERATOR_REGISTRY = {
    "equals": EqualsOperator,
    "has_different": HasDifferentOperator,
    "abs_diff": AbsDiffOperator,
    "any_equals": AnyEqualsOperator,
    "any_missing": AnyMissingOperator,
    "all": AllOperator,
    "any": AnyOperator,
    "or": AnyOperator,  # Alias for 'any'
    "not": NotOperator,
}
