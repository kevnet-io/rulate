"""
Cluster evaluation engine for validating item sets against cluster rules.

This module provides validation functions for checking whether a set of items
forms a valid cluster according to cluster-level rules.
"""

from rulate.engine.cluster_condition_evaluator import evaluate_cluster_condition
from rulate.models.catalog import Item
from rulate.models.cluster import ClusterRuleSet
from rulate.models.evaluation import RuleEvaluation


def validate_cluster(
    items: list[Item], cluster_ruleset: ClusterRuleSet
) -> tuple[bool, list[RuleEvaluation]]:
    """
    Validate a set of items against cluster rules.

    Args:
        items: List of items to validate as a cluster
        cluster_ruleset: ClusterRuleSet with validation rules

    Returns:
        Tuple of (is_valid, rule_evaluations)
        - is_valid: True if all rules pass
        - rule_evaluations: List of RuleEvaluation objects
    """
    rule_evaluations: list[RuleEvaluation] = []

    # Evaluate exclusion rules (any TRUE → invalid cluster)
    for rule in cluster_ruleset.get_exclusion_rules():
        try:
            result, reason = evaluate_cluster_condition(rule.condition, items)
            # For exclusion rules: condition TRUE means exclusion applies (cluster invalid)
            passed = not result
            rule_evaluations.append(
                RuleEvaluation(rule_name=rule.name, passed=passed, reason=reason)
            )
            if not passed:
                return False, rule_evaluations
        except Exception as e:
            rule_evaluations.append(
                RuleEvaluation(
                    rule_name=rule.name,
                    passed=False,
                    reason=f"Error evaluating rule: {str(e)}",
                )
            )
            return False, rule_evaluations

    # Evaluate requirement rules (all must be TRUE)
    for rule in cluster_ruleset.get_requirement_rules():
        try:
            result, reason = evaluate_cluster_condition(rule.condition, items)
            rule_evaluations.append(
                RuleEvaluation(rule_name=rule.name, passed=result, reason=reason)
            )
            if not result:
                return False, rule_evaluations
        except Exception as e:
            rule_evaluations.append(
                RuleEvaluation(
                    rule_name=rule.name,
                    passed=False,
                    reason=f"Error evaluating rule: {str(e)}",
                )
            )
            return False, rule_evaluations

    return True, rule_evaluations
