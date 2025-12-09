"""
Evaluation models for storing comparison results.

These models capture the results of evaluating item pairs against rules.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RuleEvaluation(BaseModel):
    """
    Result of evaluating a single rule against an item pair.

    Captures whether the rule passed and provides a human-readable explanation.

    Example:
        RuleEvaluation(
            rule_name="same_body_zone_exclusion",
            passed=True,
            reason="Different body zones (torso vs legs)"
        )
    """

    rule_name: str = Field(..., description="Name of the rule that was evaluated")
    passed: bool = Field(..., description="Whether the rule evaluation passed")
    reason: str = Field(..., description="Human-readable explanation of the result")

    def __str__(self) -> str:
        """String representation of the evaluation."""
        status = "✓ PASS" if self.passed else "✗ FAIL"
        return f"{status}: {self.rule_name} - {self.reason}"


class ComparisonResult(BaseModel):
    """
    Result of comparing two items against a ruleset.

    Contains the final compatibility decision and details of each rule evaluation.

    For boolean compatibility:
    - Exclusion rules: ANY fail → incompatible
    - Requirement rules: ALL must pass → compatible
    - Result is compatible only if all exclusions pass AND all requirements pass

    Example:
        ComparisonResult(
            item1_id="shirt_001",
            item2_id="pants_001",
            compatible=True,
            rules_evaluated=[
                RuleEvaluation(rule_name="same_zone", passed=True, ...),
                RuleEvaluation(rule_name="formality", passed=True, ...),
            ]
        )
    """

    item1_id: str = Field(..., description="ID of the first item")
    item2_id: str = Field(..., description="ID of the second item")
    compatible: bool = Field(..., description="Whether the items are compatible")
    rules_evaluated: list[RuleEvaluation] = Field(
        default_factory=list, description="Detailed results for each rule"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata (catalog, ruleset names, etc.)"
    )
    evaluated_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp of evaluation"
    )

    def get_failed_rules(self) -> list[RuleEvaluation]:
        """
        Get all rules that failed.

        Returns:
            List of RuleEvaluation objects where passed=False
        """
        return [eval for eval in self.rules_evaluated if not eval.passed]

    def get_passed_rules(self) -> list[RuleEvaluation]:
        """
        Get all rules that passed.

        Returns:
            List of RuleEvaluation objects where passed=True
        """
        return [eval for eval in self.rules_evaluated if eval.passed]

    def get_summary(self) -> str:
        """
        Get a human-readable summary of the comparison.

        Returns:
            A formatted string describing the result
        """
        status = "COMPATIBLE" if self.compatible else "INCOMPATIBLE"
        total_rules = len(self.rules_evaluated)
        passed_count = len(self.get_passed_rules())
        failed_count = len(self.get_failed_rules())

        summary = f"{status}: {self.item1_id} <-> {self.item2_id}\n"
        summary += f"Rules: {passed_count}/{total_rules} passed"

        if failed_count > 0:
            summary += "\nFailed rules:"
            for eval in self.get_failed_rules():
                summary += f"\n  - {eval.rule_name}: {eval.reason}"

        return summary

    def __str__(self) -> str:
        """String representation of the comparison result."""
        return self.get_summary()


class EvaluationMatrix(BaseModel):
    """
    Results of evaluating all pairwise combinations in a catalog.

    This is useful for visualizing compatibility across an entire collection.

    Example:
        EvaluationMatrix(
            catalog_name="my_wardrobe",
            ruleset_name="wardrobe_rules_v1",
            results=[
                ComparisonResult(item1_id="shirt_001", item2_id="pants_001", ...),
                ComparisonResult(item1_id="shirt_001", item2_id="pants_002", ...),
                ...
            ]
        )
    """

    catalog_name: str = Field(..., description="Name of the catalog that was evaluated")
    ruleset_name: str = Field(..., description="Name of the ruleset that was used")
    schema_name: str = Field(..., description="Name of the schema")
    results: list[ComparisonResult] = Field(
        default_factory=list, description="All pairwise comparison results"
    )
    evaluated_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp of evaluation"
    )

    def get_result(self, item1_id: str, item2_id: str) -> ComparisonResult | None:
        """
        Get the comparison result for a specific pair.

        Args:
            item1_id: ID of the first item
            item2_id: ID of the second item

        Returns:
            The ComparisonResult, or None if not found
        """
        for result in self.results:
            if (result.item1_id == item1_id and result.item2_id == item2_id) or (
                result.item1_id == item2_id and result.item2_id == item1_id
            ):
                return result
        return None

    def get_compatible_pairs(self) -> list[ComparisonResult]:
        """Get all compatible pairs."""
        return [result for result in self.results if result.compatible]

    def get_incompatible_pairs(self) -> list[ComparisonResult]:
        """Get all incompatible pairs."""
        return [result for result in self.results if not result.compatible]

    def get_compatible_items_for(self, item_id: str) -> list[str]:
        """
        Get all items compatible with a specific item.

        Args:
            item_id: The item ID to find compatible items for

        Returns:
            List of item IDs that are compatible
        """
        compatible = []
        for result in self.get_compatible_pairs():
            if result.item1_id == item_id:
                compatible.append(result.item2_id)
            elif result.item2_id == item_id:
                compatible.append(result.item1_id)
        return compatible

    def get_summary_stats(self) -> dict[str, Any]:
        """
        Get summary statistics about the evaluation.

        Returns:
            Dictionary with statistics
        """
        total = len(self.results)
        compatible = len(self.get_compatible_pairs())
        incompatible = len(self.get_incompatible_pairs())

        return {
            "total_comparisons": total,
            "compatible_pairs": compatible,
            "incompatible_pairs": incompatible,
            "compatibility_rate": compatible / total if total > 0 else 0,
        }
