"""
Operators for evaluating rule conditions against item pairs and clusters.

Operators are the building blocks of rule conditions. They take two items
(for pairwise operators) or a list of items (for cluster operators)
and return a boolean result plus an explanation.
"""

from abc import ABC, abstractmethod
from typing import Any

from rulate.models.catalog import Item


class Operator(ABC):
    """
    Base class for all operators.

    Operators evaluate conditions against two items and return a boolean result
    plus a human-readable explanation.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the operator with configuration.

        Args:
            config: Configuration dictionary from the rule condition
        """
        self.config = config

    @abstractmethod
    def evaluate(self, item1: Item, item2: Item) -> tuple[bool, str]:
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

    def evaluate(self, item1: Item, item2: Item) -> tuple[bool, str]:
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

    def evaluate(self, item1: Item, item2: Item) -> tuple[bool, str]:
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

    def evaluate(self, item1: Item, item2: Item) -> tuple[bool, str]:
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

    def evaluate(self, item1: Item, item2: Item) -> tuple[bool, str]:
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
            return (
                False,
                f"Neither item has {field}='{target_value}' (values: '{value1}', '{value2}')",
            )


class AnyMissingOperator(Operator):
    """
    Check if either item is missing a field.

    Config:
        field: The field name to check

    Example:
        {"any_missing": {"field": "formality"}}
        Returns True if either item doesn't have a formality value
    """

    def evaluate(self, item1: Item, item2: Item) -> tuple[bool, str]:
        field = self.config.get("field")

        if not field:
            return False, "No field specified for any_missing operator"

        value1 = item1.get_attribute(field)
        value2 = item2.get_attribute(field)

        if value1 is None or value2 is None:
            return True, f"At least one item is missing '{field}' attribute"
        else:
            return False, f"Both items have '{field}' attribute"


class PartLayerConflictOperator(Operator):
    """
    Detect coverage-layer conflicts between items with phasing validation.

    This operator checks if two items have conflicting coverage on the same body
    parts. A conflict occurs when:
    1. Both items cover the same part at the same layer (collision)
    2. Items have inconsistent layer relationships across different parts
       (phasing violation - e.g., A over B on chest but A under B on legs)

    Config:
        field: The field name containing part-layer tuples

    Example:
        {"part_layer_conflict": {"field": "coverage_layers"}}
        Returns False (conflict) if items have conflicting coverage
        Returns True (no conflict) if items can be worn together

    Usage in rules:
        # Exclusion rule: Exclude items with coverage conflicts
        type: exclusion
        condition:
          part_layer_conflict:
            field: "coverage_layers"
    """

    def evaluate(self, item1: Item, item2: Item) -> tuple[bool, str]:
        field = self.config.get("field")
        if not field:
            return False, "No field specified for part_layer_conflict operator"

        tuples1 = item1.get_attribute(field)
        tuples2 = item2.get_attribute(field)

        if tuples1 is None or tuples2 is None:
            return True, f"One or both items missing '{field}' attribute (no conflict)"

        # Build part → layer mappings
        part_to_layer1 = {}
        for tuple_item in tuples1:
            for part in tuple_item["parts"]:
                part_to_layer1[part] = tuple_item["layer"]

        part_to_layer2 = {}
        for tuple_item in tuples2:
            for part in tuple_item["parts"]:
                part_to_layer2[part] = tuple_item["layer"]

        # Find overlapping parts
        overlapping_parts = set(part_to_layer1.keys()) & set(part_to_layer2.keys())

        if not overlapping_parts:
            return True, "No overlapping body parts (no conflict)"

        # Check for consistent layer relationships
        item1_over_item2 = None  # Track relationship consistency
        conflicts = []

        for part in sorted(overlapping_parts):
            layer1 = part_to_layer1[part]
            layer2 = part_to_layer2[part]

            # Same layer = collision
            if layer1 == layer2:
                conflicts.append(f"{part}: both at layer {layer1}")
                continue

            # Track whether item1 is over or under item2
            current_relationship = "over" if layer1 > layer2 else "under"

            if item1_over_item2 is None:
                item1_over_item2 = current_relationship
            elif item1_over_item2 != current_relationship:
                # Inconsistent = phasing violation
                conflicts.append(
                    f"{part}: inconsistent phasing "
                    f"(item1 {current_relationship} item2, expected {item1_over_item2})"
                )

        if conflicts:
            return False, f"Layer conflict detected: {'; '.join(conflicts)}"
        else:
            parts_str = ", ".join(sorted(overlapping_parts))
            return True, f"No conflicts on overlapping parts [{parts_str}]"


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

    def evaluate(self, item1: Item, item2: Item) -> tuple[bool, str]:
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

    def evaluate(self, item1: Item, item2: Item) -> tuple[bool, str]:
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

    def evaluate(self, item1: Item, item2: Item) -> tuple[bool, str]:
        if not self.condition:
            return False, "No condition specified for 'not' operator"

        from rulate.engine.condition_evaluator import evaluate_condition

        result, reason = evaluate_condition(self.condition, item1, item2)
        return not result, f"NOT {reason}"


# Cluster Operators (for set-level evaluation)


class ClusterOperator(ABC):
    """
    Base class for cluster operators.

    Cluster operators evaluate conditions against a list of items (a cluster)
    and return a boolean result plus a human-readable explanation.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the operator with configuration.

        Args:
            config: Configuration dictionary from the rule condition
        """
        self.config = config
        # Store common config values as attributes for easier access
        for key, value in config.items():
            setattr(self, key, value)

    @abstractmethod
    def evaluate(self, items: list[Item]) -> tuple[bool, str]:
        """
        Evaluate the condition against a list of items.

        Args:
            items: List of items forming a cluster

        Returns:
            Tuple of (result, explanation)
            - result: True if condition is met, False otherwise
            - explanation: Human-readable explanation of the result
        """
        pass


class MinClusterSizeOperator(ClusterOperator):
    """
    Require minimum cluster size.

    Config:
        value: Minimum number of items

    Example:
        {"min_cluster_size": 3}
        Returns True if cluster has at least 3 items
    """

    def __init__(self, config: Any):
        # For simple operators, config might just be the value
        if isinstance(config, int):
            self.value = config
        elif isinstance(config, dict):
            self.value = config.get("value", config)
        else:
            self.value = config

    def evaluate(self, items: list[Item]) -> tuple[bool, str]:
        cluster_size = len(items)
        result = cluster_size >= self.value
        if result:
            return True, f"Cluster has {cluster_size} items (min {self.value})"
        else:
            return False, f"Cluster has only {cluster_size} items (need {self.value})"


class MaxClusterSizeOperator(ClusterOperator):
    """
    Enforce maximum cluster size.

    Config:
        value: Maximum number of items

    Example:
        {"max_cluster_size": 8}
        Returns True if cluster has at most 8 items
    """

    def __init__(self, config: Any):
        if isinstance(config, int):
            self.value = config
        elif isinstance(config, dict):
            self.value = config.get("value", config)
        else:
            self.value = config

    def evaluate(self, items: list[Item]) -> tuple[bool, str]:
        cluster_size = len(items)
        result = cluster_size <= self.value
        if result:
            return True, f"Cluster has {cluster_size} items (max {self.value})"
        else:
            return False, f"Cluster has {cluster_size} items (exceeds max {self.value})"


class UniqueValuesOperator(ClusterOperator):
    """
    Ensure field values are unique across all items in cluster.

    Config:
        field: The field name to check

    Example:
        {"unique_values": {"field": "body_zone"}}
        Returns True if all items have different body_zone values
    """

    def evaluate(self, items: list[Item]) -> tuple[bool, str]:
        field = getattr(self, "field", None)
        if not field:
            return False, "No field specified for unique_values operator"

        values = [item.get_attribute(field) for item in items]
        values = [v for v in values if v is not None]

        if not values:
            return True, f"No {field} values to check"

        unique_count = len(set(values))
        total_count = len(values)
        result = unique_count == total_count

        if result:
            return True, f"All {total_count} {field} values are unique"
        else:
            duplicates = total_count - unique_count
            return False, f"Found {duplicates} duplicate {field} value(s)"


class HasItemWithOperator(ClusterOperator):
    """
    Require at least one item matching criteria.

    Config:
        field: The field name to check
        value: The required value

    Example:
        {"has_item_with": {"field": "category", "value": "top"}}
        Returns True if at least one item has category="top"
    """

    def evaluate(self, items: list[Item]) -> tuple[bool, str]:
        field = getattr(self, "field", None)
        value = getattr(self, "value", None)

        if not field:
            return False, "No field specified for has_item_with operator"
        if value is None:
            return False, "No value specified for has_item_with operator"

        matching = [item for item in items if item.get_attribute(field) == value]
        result = len(matching) > 0

        if result:
            return True, f"Found {len(matching)} item(s) with {field}='{value}'"
        else:
            return False, f"No items with {field}='{value}'"


class CountByFieldOperator(ClusterOperator):
    """
    Count distinct values of a field.

    Config:
        field: The field name to count
        min: Minimum distinct values (optional)
        max: Maximum distinct values (optional)

    Example:
        {"count_by_field": {"field": "body_zone", "min": 3}}
        Returns True if cluster covers at least 3 different body zones
    """

    def evaluate(self, items: list[Item]) -> tuple[bool, str]:
        field = getattr(self, "field", None)
        if not field:
            return False, "No field specified for count_by_field operator"

        values = [item.get_attribute(field) for item in items]
        values = [v for v in values if v is not None]

        if not values:
            return False, f"No {field} values to count"

        distinct = len(set(values))
        min_count = getattr(self, "min", None)
        max_count = getattr(self, "max", None)

        if min_count is not None and distinct < min_count:
            return False, f"Only {distinct} distinct {field} value(s) (need {min_count})"
        if max_count is not None and distinct > max_count:
            return False, f"Too many distinct {field} values ({distinct}, max {max_count})"

        return True, f"{distinct} distinct {field} value(s)"


class FormalityRangeOperator(ClusterOperator):
    """
    Ensure all items are within a formality range.

    Config:
        max_diff: Maximum difference between highest and lowest formality

    Example:
        {"formality_range": {"max_diff": 1}}
        Returns True if formality levels differ by at most 1
    """

    def evaluate(self, items: list[Item]) -> tuple[bool, str]:
        max_diff = getattr(self, "max_diff", None)
        if max_diff is None:
            return False, "No max_diff specified for formality_range operator"

        formality_values = []
        for item in items:
            val = item.get_attribute("formality")
            if val is not None:
                try:
                    formality_values.append(float(val))
                except (ValueError, TypeError):
                    return False, f"Invalid formality value for {item.id}: {val}"

        if not formality_values:
            return True, "No formality values to check"

        min_val = min(formality_values)
        max_val = max(formality_values)
        diff = max_val - min_val
        result = diff <= max_diff

        if result:
            return (
                True,
                f"Formality range {min_val:.0f}-{max_val:.0f} (diff={diff:.0f}, max={max_diff})",
            )
        else:
            return (
                False,
                f"Formality range {min_val:.0f}-{max_val:.0f} (diff={diff:.0f} exceeds max {max_diff})",
            )


# Cluster Logical Operators


class ClusterAllOperator(ClusterOperator):
    """
    Logical AND for cluster conditions - all sub-conditions must be true.

    Config:
        List of sub-condition dictionaries

    Example:
        {"all": [
            {"min_cluster_size": 3},
            {"has_item_with": {"field": "category", "value": "top"}}
        ]}
    """

    def __init__(self, config: Any):
        self.conditions = config if isinstance(config, list) else []

    def evaluate(self, items: list[Item]) -> tuple[bool, str]:
        if not self.conditions:
            return False, "No conditions specified for 'all' operator"

        from rulate.engine.cluster_condition_evaluator import evaluate_cluster_condition

        for condition in self.conditions:
            result, reason = evaluate_cluster_condition(condition, items)
            if not result:
                return False, f"AND failed: {reason}"

        return True, "All conditions passed"


class ClusterAnyOperator(ClusterOperator):
    """
    Logical OR for cluster conditions - at least one sub-condition must be true.

    Config:
        List of sub-condition dictionaries

    Example:
        {"any": [
            {"min_cluster_size": 5},
            {"has_item_with": {"field": "category", "value": "accessory"}}
        ]}
    """

    def __init__(self, config: Any):
        self.conditions = config if isinstance(config, list) else []

    def evaluate(self, items: list[Item]) -> tuple[bool, str]:
        if not self.conditions:
            return False, "No conditions specified for 'any' operator"

        from rulate.engine.cluster_condition_evaluator import evaluate_cluster_condition

        reasons = []
        for condition in self.conditions:
            result, reason = evaluate_cluster_condition(condition, items)
            if result:
                return True, f"OR succeeded: {reason}"
            reasons.append(reason)

        return False, f"All OR conditions failed: {'; '.join(reasons)}"


class ClusterNotOperator(ClusterOperator):
    """
    Logical NOT for cluster conditions - negate a condition.

    Config:
        Single sub-condition dictionary

    Example:
        {"not": {"max_cluster_size": 10}}
    """

    def __init__(self, config: Any):
        self.condition = config

    def evaluate(self, items: list[Item]) -> tuple[bool, str]:
        if not self.condition:
            return False, "No condition specified for 'not' operator"

        from rulate.engine.cluster_condition_evaluator import evaluate_cluster_condition

        result, reason = evaluate_cluster_condition(self.condition, items)
        return not result, f"NOT ({reason})"


# Operator registry for lookup
OPERATOR_REGISTRY = {
    "equals": EqualsOperator,
    "has_different": HasDifferentOperator,
    "abs_diff": AbsDiffOperator,
    "any_equals": AnyEqualsOperator,
    "any_missing": AnyMissingOperator,
    "part_layer_conflict": PartLayerConflictOperator,
    "all": AllOperator,
    "any": AnyOperator,
    "or": AnyOperator,  # Alias for 'any'
    "not": NotOperator,
}

# Cluster operator registry
CLUSTER_OPERATOR_REGISTRY = {
    "min_cluster_size": MinClusterSizeOperator,
    "max_cluster_size": MaxClusterSizeOperator,
    "unique_values": UniqueValuesOperator,
    "has_item_with": HasItemWithOperator,
    "count_by_field": CountByFieldOperator,
    "formality_range": FormalityRangeOperator,
    "all": ClusterAllOperator,
    "any": ClusterAnyOperator,
    "or": ClusterAnyOperator,  # Alias for 'any'
    "not": ClusterNotOperator,
}
