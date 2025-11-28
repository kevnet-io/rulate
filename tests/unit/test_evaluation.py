"""
Comprehensive tests for evaluation models.

Tests cover:
- RuleEvaluation creation and string representation
- ComparisonResult creation and analysis methods
- EvaluationMatrix creation and query methods
- Edge cases and filtering logic
"""

from datetime import datetime

import pytest

from rulate.models.evaluation import ComparisonResult, EvaluationMatrix, RuleEvaluation


class TestRuleEvaluation:
    """Tests for the RuleEvaluation model."""

    def test_creates_rule_evaluation_with_all_fields(self):
        """RuleEvaluation can be created with all required fields."""
        eval = RuleEvaluation(
            rule_name="test_rule",
            passed=True,
            reason="Test passed because condition met",
        )
        assert eval.rule_name == "test_rule"
        assert eval.passed is True
        assert eval.reason == "Test passed because condition met"

    def test_str_representation_for_passed_rule(self):
        """__str__ shows PASS status for passed rules."""
        eval = RuleEvaluation(
            rule_name="test_rule",
            passed=True,
            reason="Condition met",
        )
        result = str(eval)
        assert "✓ PASS" in result
        assert "test_rule" in result
        assert "Condition met" in result

    def test_str_representation_for_failed_rule(self):
        """__str__ shows FAIL status for failed rules."""
        eval = RuleEvaluation(
            rule_name="test_rule",
            passed=False,
            reason="Condition not met",
        )
        result = str(eval)
        assert "✗ FAIL" in result
        assert "test_rule" in result
        assert "Condition not met" in result


class TestComparisonResult:
    """Tests for the ComparisonResult model."""

    def test_creates_comparison_result_with_required_fields(self):
        """ComparisonResult can be created with minimal required fields."""
        result = ComparisonResult(
            item1_id="item_001",
            item2_id="item_002",
            compatible=True,
        )
        assert result.item1_id == "item_001"
        assert result.item2_id == "item_002"
        assert result.compatible is True
        assert result.rules_evaluated == []
        assert result.metadata == {}
        assert isinstance(result.evaluated_at, datetime)

    def test_creates_comparison_result_with_all_fields(self):
        """ComparisonResult can be created with all fields."""
        rules = [
            RuleEvaluation(rule_name="rule1", passed=True, reason="Passed"),
            RuleEvaluation(rule_name="rule2", passed=True, reason="Passed"),
        ]
        metadata = {"catalog": "test_catalog", "ruleset": "test_rules"}
        timestamp = datetime(2024, 1, 1, 12, 0, 0)

        result = ComparisonResult(
            item1_id="item_001",
            item2_id="item_002",
            compatible=True,
            rules_evaluated=rules,
            metadata=metadata,
            evaluated_at=timestamp,
        )

        assert len(result.rules_evaluated) == 2
        assert result.metadata == metadata
        assert result.evaluated_at == timestamp

    def test_get_failed_rules_returns_only_failed_rules(self):
        """get_failed_rules() returns only rules where passed=False."""
        rules = [
            RuleEvaluation(rule_name="rule1", passed=True, reason="Passed"),
            RuleEvaluation(rule_name="rule2", passed=False, reason="Failed"),
            RuleEvaluation(rule_name="rule3", passed=False, reason="Failed"),
        ]
        result = ComparisonResult(
            item1_id="item_001",
            item2_id="item_002",
            compatible=False,
            rules_evaluated=rules,
        )

        failed = result.get_failed_rules()
        assert len(failed) == 2
        assert all(not rule.passed for rule in failed)
        assert failed[0].rule_name == "rule2"
        assert failed[1].rule_name == "rule3"

    def test_get_failed_rules_returns_empty_list_when_all_passed(self):
        """get_failed_rules() returns empty list when all rules passed."""
        rules = [
            RuleEvaluation(rule_name="rule1", passed=True, reason="Passed"),
            RuleEvaluation(rule_name="rule2", passed=True, reason="Passed"),
        ]
        result = ComparisonResult(
            item1_id="item_001",
            item2_id="item_002",
            compatible=True,
            rules_evaluated=rules,
        )

        failed = result.get_failed_rules()
        assert failed == []

    def test_get_passed_rules_returns_only_passed_rules(self):
        """get_passed_rules() returns only rules where passed=True."""
        rules = [
            RuleEvaluation(rule_name="rule1", passed=True, reason="Passed"),
            RuleEvaluation(rule_name="rule2", passed=False, reason="Failed"),
            RuleEvaluation(rule_name="rule3", passed=True, reason="Passed"),
        ]
        result = ComparisonResult(
            item1_id="item_001",
            item2_id="item_002",
            compatible=False,
            rules_evaluated=rules,
        )

        passed = result.get_passed_rules()
        assert len(passed) == 2
        assert all(rule.passed for rule in passed)
        assert passed[0].rule_name == "rule1"
        assert passed[1].rule_name == "rule3"

    def test_get_passed_rules_returns_empty_list_when_all_failed(self):
        """get_passed_rules() returns empty list when all rules failed."""
        rules = [
            RuleEvaluation(rule_name="rule1", passed=False, reason="Failed"),
            RuleEvaluation(rule_name="rule2", passed=False, reason="Failed"),
        ]
        result = ComparisonResult(
            item1_id="item_001",
            item2_id="item_002",
            compatible=False,
            rules_evaluated=rules,
        )

        passed = result.get_passed_rules()
        assert passed == []

    def test_get_summary_shows_compatible_status(self):
        """get_summary() shows COMPATIBLE status when compatible."""
        rules = [
            RuleEvaluation(rule_name="rule1", passed=True, reason="Passed"),
            RuleEvaluation(rule_name="rule2", passed=True, reason="Passed"),
        ]
        result = ComparisonResult(
            item1_id="item_001",
            item2_id="item_002",
            compatible=True,
            rules_evaluated=rules,
        )

        summary = result.get_summary()
        assert "COMPATIBLE" in summary
        assert "item_001" in summary
        assert "item_002" in summary
        assert "2/2 passed" in summary

    def test_get_summary_shows_incompatible_status(self):
        """get_summary() shows INCOMPATIBLE status when not compatible."""
        rules = [
            RuleEvaluation(rule_name="rule1", passed=True, reason="Passed"),
            RuleEvaluation(rule_name="rule2", passed=False, reason="Failed condition"),
        ]
        result = ComparisonResult(
            item1_id="item_001",
            item2_id="item_002",
            compatible=False,
            rules_evaluated=rules,
        )

        summary = result.get_summary()
        assert "INCOMPATIBLE" in summary
        assert "1/2 passed" in summary
        assert "Failed rules:" in summary
        assert "rule2" in summary
        assert "Failed condition" in summary

    def test_get_summary_handles_no_rules(self):
        """get_summary() handles case with no rules."""
        result = ComparisonResult(
            item1_id="item_001",
            item2_id="item_002",
            compatible=True,
            rules_evaluated=[],
        )

        summary = result.get_summary()
        assert "COMPATIBLE" in summary
        assert "0/0 passed" in summary

    def test_str_representation_calls_get_summary(self):
        """__str__ returns the same as get_summary()."""
        rules = [
            RuleEvaluation(rule_name="rule1", passed=True, reason="Passed"),
        ]
        result = ComparisonResult(
            item1_id="item_001",
            item2_id="item_002",
            compatible=True,
            rules_evaluated=rules,
        )

        assert str(result) == result.get_summary()


class TestEvaluationMatrix:
    """Tests for the EvaluationMatrix model."""

    def test_creates_evaluation_matrix_with_required_fields(self):
        """EvaluationMatrix can be created with minimal required fields."""
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
        )
        assert matrix.catalog_name == "test_catalog"
        assert matrix.ruleset_name == "test_rules"
        assert matrix.schema_name == "test_schema"
        assert matrix.results == []
        assert isinstance(matrix.evaluated_at, datetime)

    def test_creates_evaluation_matrix_with_results(self):
        """EvaluationMatrix can be created with results."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=True),
            ComparisonResult(item1_id="item_001", item2_id="item_003", compatible=False),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )
        assert len(matrix.results) == 2

    def test_get_result_finds_pair_in_forward_order(self):
        """get_result() finds pair when IDs are in forward order."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=True),
            ComparisonResult(item1_id="item_001", item2_id="item_003", compatible=False),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        result = matrix.get_result("item_001", "item_002")
        assert result is not None
        assert result.item1_id == "item_001"
        assert result.item2_id == "item_002"

    def test_get_result_finds_pair_in_reverse_order(self):
        """get_result() finds pair when IDs are in reverse order."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=True),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        # Query in reverse order
        result = matrix.get_result("item_002", "item_001")
        assert result is not None
        assert result.item1_id == "item_001"
        assert result.item2_id == "item_002"

    def test_get_result_returns_none_when_not_found(self):
        """get_result() returns None when pair doesn't exist."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=True),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        result = matrix.get_result("item_001", "item_999")
        assert result is None

    def test_get_compatible_pairs_returns_only_compatible(self):
        """get_compatible_pairs() returns only compatible results."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=True),
            ComparisonResult(item1_id="item_001", item2_id="item_003", compatible=False),
            ComparisonResult(item1_id="item_002", item2_id="item_003", compatible=True),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        compatible = matrix.get_compatible_pairs()
        assert len(compatible) == 2
        assert all(result.compatible for result in compatible)

    def test_get_compatible_pairs_returns_empty_list_when_none(self):
        """get_compatible_pairs() returns empty list when all incompatible."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=False),
            ComparisonResult(item1_id="item_001", item2_id="item_003", compatible=False),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        compatible = matrix.get_compatible_pairs()
        assert compatible == []

    def test_get_incompatible_pairs_returns_only_incompatible(self):
        """get_incompatible_pairs() returns only incompatible results."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=True),
            ComparisonResult(item1_id="item_001", item2_id="item_003", compatible=False),
            ComparisonResult(item1_id="item_002", item2_id="item_003", compatible=False),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        incompatible = matrix.get_incompatible_pairs()
        assert len(incompatible) == 2
        assert all(not result.compatible for result in incompatible)

    def test_get_incompatible_pairs_returns_empty_list_when_none(self):
        """get_incompatible_pairs() returns empty list when all compatible."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=True),
            ComparisonResult(item1_id="item_001", item2_id="item_003", compatible=True),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        incompatible = matrix.get_incompatible_pairs()
        assert incompatible == []

    def test_get_compatible_items_for_returns_compatible_items(self):
        """get_compatible_items_for() returns all compatible item IDs."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=True),
            ComparisonResult(item1_id="item_001", item2_id="item_003", compatible=False),
            ComparisonResult(item1_id="item_001", item2_id="item_004", compatible=True),
            ComparisonResult(item1_id="item_002", item2_id="item_003", compatible=True),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        compatible = matrix.get_compatible_items_for("item_001")
        assert len(compatible) == 2
        assert "item_002" in compatible
        assert "item_004" in compatible
        assert "item_003" not in compatible

    def test_get_compatible_items_for_handles_reverse_pairs(self):
        """get_compatible_items_for() handles pairs where query item is item2."""
        results = [
            ComparisonResult(item1_id="item_002", item2_id="item_001", compatible=True),
            ComparisonResult(item1_id="item_003", item2_id="item_001", compatible=True),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        compatible = matrix.get_compatible_items_for("item_001")
        assert len(compatible) == 2
        assert "item_002" in compatible
        assert "item_003" in compatible

    def test_get_compatible_items_for_returns_empty_list_when_none(self):
        """get_compatible_items_for() returns empty list when no compatible items."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=False),
            ComparisonResult(item1_id="item_001", item2_id="item_003", compatible=False),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        compatible = matrix.get_compatible_items_for("item_001")
        assert compatible == []

    def test_get_compatible_items_for_returns_empty_list_when_item_not_in_matrix(self):
        """get_compatible_items_for() returns empty list when item not found."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=True),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        compatible = matrix.get_compatible_items_for("item_999")
        assert compatible == []

    def test_get_summary_stats_returns_correct_counts(self):
        """get_summary_stats() returns correct counts and rate."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=True),
            ComparisonResult(item1_id="item_001", item2_id="item_003", compatible=False),
            ComparisonResult(item1_id="item_001", item2_id="item_004", compatible=True),
            ComparisonResult(item1_id="item_002", item2_id="item_003", compatible=True),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        stats = matrix.get_summary_stats()
        assert stats["total_comparisons"] == 4
        assert stats["compatible_pairs"] == 3
        assert stats["incompatible_pairs"] == 1
        assert stats["compatibility_rate"] == 0.75

    def test_get_summary_stats_handles_empty_matrix(self):
        """get_summary_stats() handles empty matrix without division by zero."""
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=[],
        )

        stats = matrix.get_summary_stats()
        assert stats["total_comparisons"] == 0
        assert stats["compatible_pairs"] == 0
        assert stats["incompatible_pairs"] == 0
        assert stats["compatibility_rate"] == 0

    def test_get_summary_stats_calculates_100_percent_rate(self):
        """get_summary_stats() calculates 100% compatibility rate correctly."""
        results = [
            ComparisonResult(item1_id="item_001", item2_id="item_002", compatible=True),
            ComparisonResult(item1_id="item_001", item2_id="item_003", compatible=True),
        ]
        matrix = EvaluationMatrix(
            catalog_name="test_catalog",
            ruleset_name="test_rules",
            schema_name="test_schema",
            results=results,
        )

        stats = matrix.get_summary_stats()
        assert stats["compatibility_rate"] == 1.0
