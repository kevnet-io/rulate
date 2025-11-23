"""
Main evaluation engine for comparing items against rules.

This module orchestrates the evaluation process: validating items against schemas,
applying rules, and generating comparison results.
"""

from datetime import datetime
from typing import List, Optional

from rulate.engine.condition_evaluator import evaluate_condition
from rulate.models.catalog import Catalog, Item
from rulate.models.evaluation import ComparisonResult, EvaluationMatrix, RuleEvaluation
from rulate.models.rule import Rule, RuleSet, RuleType
from rulate.models.schema import Schema


def evaluate_pair(
    item1: Item,
    item2: Item,
    ruleset: RuleSet,
    schema: Optional[Schema] = None,
    validate_schema: bool = True,
) -> ComparisonResult:
    """
    Evaluate compatibility between two items.

    Args:
        item1: First item
        item2: Second item
        ruleset: RuleSet to apply
        schema: Optional schema for validation
        validate_schema: Whether to validate items against schema (default True)

    Returns:
        ComparisonResult with compatibility decision and rule evaluations

    Raises:
        ValueError: If schema validation fails
    """
    # Validate items against schema if provided
    if validate_schema and schema:
        try:
            schema.validate_attributes(item1.attributes)
            schema.validate_attributes(item2.attributes)
        except ValueError as e:
            raise ValueError(f"Schema validation failed: {e}")

    rule_evaluations: List[RuleEvaluation] = []

    # Evaluate exclusion rules (any fail → incompatible)
    exclusion_passed = True
    for rule in ruleset.get_exclusion_rules():
        try:
            result, reason = evaluate_condition(rule.condition, item1, item2)
            # For exclusion rules: condition TRUE means exclusion applies (rule FAILS)
            # So passed should be the inverse of the condition result
            rule_passed = not result
            rule_eval = RuleEvaluation(rule_name=rule.name, passed=rule_passed, reason=reason)
            rule_evaluations.append(rule_eval)

            # For exclusion rules, if condition is TRUE, items are INCOMPATIBLE
            # So we want the condition to be FALSE for compatibility
            if result:
                exclusion_passed = False
        except Exception as e:
            rule_eval = RuleEvaluation(
                rule_name=rule.name,
                passed=False,
                reason=f"Error evaluating rule: {str(e)}",
            )
            rule_evaluations.append(rule_eval)
            exclusion_passed = False

    # Evaluate requirement rules (all must pass → compatible)
    requirement_passed = True
    for rule in ruleset.get_requirement_rules():
        try:
            result, reason = evaluate_condition(rule.condition, item1, item2)
            rule_eval = RuleEvaluation(rule_name=rule.name, passed=result, reason=reason)
            rule_evaluations.append(rule_eval)

            # For requirement rules, if condition is FALSE, items are INCOMPATIBLE
            if not result:
                requirement_passed = False
        except Exception as e:
            rule_eval = RuleEvaluation(
                rule_name=rule.name,
                passed=False,
                reason=f"Error evaluating rule: {str(e)}",
            )
            rule_evaluations.append(rule_eval)
            requirement_passed = False

    # Items are compatible if:
    # 1. No exclusion rule condition evaluated to TRUE (all exclusions passed)
    # 2. All requirement rule conditions evaluated to TRUE (all requirements passed)
    compatible = exclusion_passed and requirement_passed

    return ComparisonResult(
        item1_id=item1.id,
        item2_id=item2.id,
        compatible=compatible,
        rules_evaluated=rule_evaluations,
        metadata={
            "ruleset_name": ruleset.name,
            "schema_name": schema.name if schema else None,
        },
        evaluated_at=datetime.now(),
    )


def evaluate_matrix(
    catalog: Catalog,
    ruleset: RuleSet,
    schema: Optional[Schema] = None,
    validate_schema: bool = True,
    include_self: bool = False,
) -> EvaluationMatrix:
    """
    Evaluate all pairwise combinations in a catalog.

    Args:
        catalog: Catalog of items to evaluate
        ruleset: RuleSet to apply
        schema: Optional schema for validation
        validate_schema: Whether to validate items against schema (default True)
        include_self: Whether to include self-comparisons (item vs itself)

    Returns:
        EvaluationMatrix with all pairwise comparison results

    Raises:
        ValueError: If catalog is empty or schema validation fails
    """
    if len(catalog.items) == 0:
        raise ValueError("Cannot evaluate empty catalog")

    results: List[ComparisonResult] = []

    # Generate all pairs (avoiding duplicates: only compare i with j where j > i)
    for i, item1 in enumerate(catalog.items):
        start_j = i if include_self else i + 1
        for item2 in catalog.items[start_j:]:
            if item1.id == item2.id and not include_self:
                continue

            result = evaluate_pair(item1, item2, ruleset, schema, validate_schema)
            results.append(result)

    return EvaluationMatrix(
        catalog_name=catalog.name,
        ruleset_name=ruleset.name,
        schema_name=schema.name if schema else "unknown",
        results=results,
        evaluated_at=datetime.now(),
    )


def evaluate_item_against_catalog(
    item: Item,
    catalog: Catalog,
    ruleset: RuleSet,
    schema: Optional[Schema] = None,
    validate_schema: bool = True,
) -> List[ComparisonResult]:
    """
    Evaluate a single item against all items in a catalog.

    Args:
        item: The item to evaluate
        catalog: Catalog of items to compare against
        ruleset: RuleSet to apply
        schema: Optional schema for validation
        validate_schema: Whether to validate items against schema (default True)

    Returns:
        List of ComparisonResult objects

    Raises:
        ValueError: If schema validation fails
    """
    results: List[ComparisonResult] = []

    for other_item in catalog.items:
        if item.id == other_item.id:
            continue

        result = evaluate_pair(item, other_item, ruleset, schema, validate_schema)
        results.append(result)

    return results
