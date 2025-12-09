"""
Tests for condition evaluators (pairwise and cluster).

This module tests the condition parsing and evaluation logic for both
pairwise and cluster operators.
"""

import pytest

from rulate.engine.cluster_condition_evaluator import (
    evaluate_cluster_condition,
    validate_cluster_condition,
)
from rulate.engine.condition_evaluator import evaluate_condition, validate_condition
from rulate.models.catalog import Item

# ============================================================================
# Pairwise Condition Evaluator Tests
# ============================================================================


class TestEvaluateCondition:
    """Tests for evaluate_condition() function."""

    def test_evaluates_simple_equals_condition(self, item_blue_shirt, item_red_shirt):
        """Test evaluating a simple equals condition."""
        condition = {"equals": {"field": "category"}}
        result, explanation = evaluate_condition(condition, item_blue_shirt, item_red_shirt)
        assert result is True
        assert "category" in explanation

    def test_evaluates_has_different_condition(self, item_blue_shirt, item_red_shirt):
        """Test evaluating a has_different condition."""
        condition = {"has_different": {"field": "color"}}
        result, explanation = evaluate_condition(condition, item_blue_shirt, item_red_shirt)
        assert result is True
        assert "blue" in explanation and "red" in explanation

    def test_evaluates_abs_diff_condition(self, item_blue_shirt, item_red_shirt):
        """Test evaluating an abs_diff condition."""
        condition = {"abs_diff": {"field": "formality", "max": 2}}
        result, explanation = evaluate_condition(condition, item_blue_shirt, item_red_shirt)
        assert result is True

    def test_evaluates_any_equals_condition(self, item_blue_shirt, item_red_shirt):
        """Test evaluating an any_equals condition."""
        condition = {"any_equals": {"field": "color", "value": "blue"}}
        result, explanation = evaluate_condition(condition, item_blue_shirt, item_red_shirt)
        assert result is True

    def test_evaluates_any_missing_condition(self, item_blue_shirt, item_minimal):
        """Test evaluating an any_missing condition."""
        condition = {"any_missing": {"field": "formality"}}
        result, explanation = evaluate_condition(condition, item_blue_shirt, item_minimal)
        assert result is True

    def test_evaluates_all_operator(self, item_blue_shirt, item_red_shirt):
        """Test evaluating an all (AND) logical operator."""
        condition = {"all": [{"equals": {"field": "category"}}, {"has_different": {"field": "color"}}]}
        result, explanation = evaluate_condition(condition, item_blue_shirt, item_red_shirt)
        assert result is True

    def test_evaluates_any_operator(self, item_blue_shirt, item_blue_pants):
        """Test evaluating an any (OR) logical operator."""
        condition = {"any": [{"equals": {"field": "category"}}, {"equals": {"field": "color"}}]}
        result, explanation = evaluate_condition(condition, item_blue_shirt, item_blue_pants)
        assert result is True  # Color matches even if category doesn't

    def test_evaluates_not_operator(self, item_blue_shirt, item_blue_pants):
        """Test evaluating a not (NOT) logical operator."""
        condition = {"not": {"equals": {"field": "category"}}}
        result, explanation = evaluate_condition(condition, item_blue_shirt, item_blue_pants)
        assert result is True

    def test_evaluates_nested_conditions(self, item_blue_shirt, item_red_shirt):
        """Test evaluating deeply nested conditions."""
        condition = {
            "all": [
                {"equals": {"field": "category"}},
                {"any": [{"has_different": {"field": "color"}}, {"equals": {"field": "formality"}}]},
            ]
        }
        result, _ = evaluate_condition(condition, item_blue_shirt, item_red_shirt)
        assert result is True

    def test_raises_error_for_non_dict_condition(self, item_blue_shirt, item_red_shirt):
        """Test that non-dict condition raises ValueError."""
        with pytest.raises(ValueError, match="must be a dictionary"):
            evaluate_condition("invalid", item_blue_shirt, item_red_shirt)

    def test_raises_error_for_empty_condition(self, item_blue_shirt, item_red_shirt):
        """Test that empty dict condition raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            evaluate_condition({}, item_blue_shirt, item_red_shirt)

    def test_raises_error_for_multiple_operators(self, item_blue_shirt, item_red_shirt):
        """Test that multiple operators in one condition raises ValueError."""
        with pytest.raises(ValueError, match="exactly one operator"):
            evaluate_condition(
                {"equals": {"field": "color"}, "has_different": {"field": "size"}},
                item_blue_shirt,
                item_red_shirt,
            )

    def test_raises_error_for_unknown_operator(self, item_blue_shirt, item_red_shirt):
        """Test that unknown operator raises ValueError."""
        with pytest.raises(ValueError, match="Unknown operator"):
            evaluate_condition({"invalid_op": {"field": "color"}}, item_blue_shirt, item_red_shirt)

    def test_handles_operator_evaluation_errors_gracefully(self, item_blue_shirt, item_red_shirt):
        """Test that operator evaluation errors are caught and returned."""
        # AbsDiffOperator with non-numeric values will fail
        condition = {"abs_diff": {"field": "category", "max": 2}}
        result, explanation = evaluate_condition(condition, item_blue_shirt, item_red_shirt)
        assert result is False
        assert "cannot compute" in explanation.lower()


class TestValidateCondition:
    """Tests for validate_condition() function."""

    def test_validates_simple_equals_condition(self):
        """Test validating a simple equals condition."""
        condition = {"equals": {"field": "category"}}
        assert validate_condition(condition) is True

    def test_validates_has_different_condition(self):
        """Test validating a has_different condition."""
        condition = {"has_different": {"field": "color"}}
        assert validate_condition(condition) is True

    def test_validates_abs_diff_condition(self):
        """Test validating an abs_diff condition."""
        condition = {"abs_diff": {"field": "formality", "max": 2}}
        assert validate_condition(condition) is True

    def test_validates_all_operator_with_sub_conditions(self):
        """Test validating an all operator with sub-conditions."""
        condition = {"all": [{"equals": {"field": "category"}}, {"has_different": {"field": "color"}}]}
        assert validate_condition(condition) is True

    def test_validates_any_operator_with_sub_conditions(self):
        """Test validating an any operator with sub-conditions."""
        condition = {"any": [{"equals": {"field": "category"}}, {"equals": {"field": "color"}}]}
        assert validate_condition(condition) is True

    def test_validates_not_operator_with_sub_condition(self):
        """Test validating a not operator with sub-condition."""
        condition = {"not": {"equals": {"field": "category"}}}
        assert validate_condition(condition) is True

    def test_validates_nested_conditions(self):
        """Test validating deeply nested conditions."""
        condition = {
            "all": [
                {"equals": {"field": "category"}},
                {"any": [{"has_different": {"field": "color"}}, {"not": {"equals": {"field": "size"}}}]},
            ]
        }
        assert validate_condition(condition) is True

    def test_raises_error_for_non_dict_condition(self):
        """Test that non-dict condition raises ValueError."""
        with pytest.raises(ValueError, match="must be a dictionary"):
            validate_condition("invalid")

    def test_raises_error_for_empty_condition(self):
        """Test that empty dict condition raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_condition({})

    def test_raises_error_for_multiple_operators(self):
        """Test that multiple operators raise ValueError."""
        with pytest.raises(ValueError, match="exactly one operator"):
            validate_condition({"equals": {"field": "color"}, "has_different": {"field": "size"}})

    def test_raises_error_for_unknown_operator(self):
        """Test that unknown operator raises ValueError."""
        with pytest.raises(ValueError, match="Unknown operator"):
            validate_condition({"invalid_op": {"field": "color"}})

    def test_raises_error_for_all_operator_without_list(self):
        """Test that all operator without list raises ValueError."""
        with pytest.raises(ValueError, match="requires a list"):
            validate_condition({"all": {"field": "color"}})

    def test_raises_error_for_any_operator_without_list(self):
        """Test that any operator without list raises ValueError."""
        with pytest.raises(ValueError, match="requires a list"):
            validate_condition({"any": {"field": "color"}})

    def test_raises_error_for_invalid_sub_condition_in_all(self):
        """Test that invalid sub-condition in all operator raises ValueError."""
        with pytest.raises(ValueError, match="Unknown operator"):
            validate_condition({"all": [{"equals": {"field": "category"}}, {"invalid_op": {}}]})

    def test_raises_error_for_invalid_sub_condition_in_not(self):
        """Test that invalid sub-condition in not operator raises ValueError."""
        with pytest.raises(ValueError, match="Unknown operator"):
            validate_condition({"not": {"invalid_op": {"field": "color"}}})


# ============================================================================
# Cluster Condition Evaluator Tests
# ============================================================================


class TestEvaluateClusterCondition:
    """Tests for evaluate_cluster_condition() function."""

    def test_evaluates_min_cluster_size_condition(self, sample_items_list):
        """Test evaluating a min_cluster_size condition."""
        condition = {"min_cluster_size": 3}
        result, explanation = evaluate_cluster_condition(condition, sample_items_list)
        assert result is True
        assert "4 items" in explanation

    def test_evaluates_max_cluster_size_condition(self, sample_items_list):
        """Test evaluating a max_cluster_size condition."""
        condition = {"max_cluster_size": 10}
        result, explanation = evaluate_cluster_condition(condition, sample_items_list)
        assert result is True

    def test_evaluates_unique_values_condition(self):
        """Test evaluating a unique_values condition."""
        items = [
            Item(id="i1", name="I1", attributes={"color": "red"}),
            Item(id="i2", name="I2", attributes={"color": "blue"}),
            Item(id="i3", name="I3", attributes={"color": "green"}),
        ]
        condition = {"unique_values": {"field": "color"}}
        result, _ = evaluate_cluster_condition(condition, items)
        assert result is True

    def test_evaluates_has_item_with_condition(self, sample_items_list):
        """Test evaluating a has_item_with condition."""
        condition = {"has_item_with": {"field": "category", "value": "shoes"}}
        result, explanation = evaluate_cluster_condition(condition, sample_items_list)
        assert result is True

    def test_evaluates_count_by_field_condition(self, sample_items_list):
        """Test evaluating a count_by_field condition."""
        condition = {"count_by_field": {"field": "category", "min": 2}}
        result, explanation = evaluate_cluster_condition(condition, sample_items_list)
        assert result is True

    def test_evaluates_formality_range_condition(self):
        """Test evaluating a formality_range condition."""
        items = [
            Item(id="i1", name="I1", attributes={"formality": 2}),
            Item(id="i2", name="I2", attributes={"formality": 3}),
            Item(id="i3", name="I3", attributes={"formality": 4}),
        ]
        condition = {"formality_range": {"max_diff": 2}}
        result, _ = evaluate_cluster_condition(condition, items)
        assert result is True

    def test_evaluates_cluster_all_operator(self, sample_items_list):
        """Test evaluating a cluster all (AND) logical operator."""
        condition = {"all": [{"min_cluster_size": 3}, {"max_cluster_size": 10}]}
        result, explanation = evaluate_cluster_condition(condition, sample_items_list)
        assert result is True

    def test_evaluates_cluster_any_operator(self, sample_items_list):
        """Test evaluating a cluster any (OR) logical operator."""
        condition = {"any": [{"min_cluster_size": 10}, {"max_cluster_size": 5}]}
        result, explanation = evaluate_cluster_condition(condition, sample_items_list)
        assert result is True  # Max size passes

    def test_evaluates_cluster_not_operator(self, sample_items_list):
        """Test evaluating a cluster not (NOT) logical operator."""
        condition = {"not": {"min_cluster_size": 10}}
        result, explanation = evaluate_cluster_condition(condition, sample_items_list)
        assert result is True

    def test_evaluates_nested_cluster_conditions(self, sample_items_list):
        """Test evaluating deeply nested cluster conditions."""
        condition = {
            "all": [
                {"min_cluster_size": 3},
                {"any": [{"max_cluster_size": 5}, {"has_item_with": {"field": "category", "value": "shoes"}}]},
            ]
        }
        result, _ = evaluate_cluster_condition(condition, sample_items_list)
        assert result is True

    def test_raises_error_for_non_dict_condition(self, sample_items_list):
        """Test that non-dict condition raises ValueError."""
        with pytest.raises(ValueError, match="must be a dictionary"):
            evaluate_cluster_condition("invalid", sample_items_list)

    def test_raises_error_for_empty_condition(self, sample_items_list):
        """Test that empty dict condition raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            evaluate_cluster_condition({}, sample_items_list)

    def test_raises_error_for_multiple_operators(self, sample_items_list):
        """Test that multiple operators in one condition raises ValueError."""
        with pytest.raises(ValueError, match="exactly one operator"):
            evaluate_cluster_condition(
                {"min_cluster_size": 3, "max_cluster_size": 10}, sample_items_list
            )

    def test_raises_error_for_unknown_operator(self, sample_items_list):
        """Test that unknown cluster operator raises ValueError."""
        with pytest.raises(ValueError, match="Unknown cluster operator"):
            evaluate_cluster_condition({"invalid_cluster_op": {}}, sample_items_list)

    def test_handles_operator_evaluation_errors_gracefully(self):
        """Test that operator evaluation errors are caught and returned."""
        # FormalityRangeOperator with non-numeric formality values will fail
        items = [
            Item(id="i1", name="I1", attributes={"formality": "high"}),
            Item(id="i2", name="I2", attributes={"formality": 3}),
        ]
        condition = {"formality_range": {"max_diff": 1}}
        result, explanation = evaluate_cluster_condition(condition, items)
        assert result is False
        assert "invalid" in explanation.lower()


class TestValidateClusterCondition:
    """Tests for validate_cluster_condition() function."""

    def test_validates_min_cluster_size_condition(self):
        """Test validating a min_cluster_size condition."""
        condition = {"min_cluster_size": 3}
        assert validate_cluster_condition(condition) is True

    def test_validates_max_cluster_size_condition(self):
        """Test validating a max_cluster_size condition."""
        condition = {"max_cluster_size": 10}
        assert validate_cluster_condition(condition) is True

    def test_validates_unique_values_condition(self):
        """Test validating a unique_values condition."""
        condition = {"unique_values": {"field": "color"}}
        assert validate_cluster_condition(condition) is True

    def test_validates_has_item_with_condition(self):
        """Test validating a has_item_with condition."""
        condition = {"has_item_with": {"field": "category", "value": "shoes"}}
        assert validate_cluster_condition(condition) is True

    def test_validates_count_by_field_condition(self):
        """Test validating a count_by_field condition."""
        condition = {"count_by_field": {"field": "category", "min": 2, "max": 5}}
        assert validate_cluster_condition(condition) is True

    def test_validates_formality_range_condition(self):
        """Test validating a formality_range condition."""
        condition = {"formality_range": {"max_diff": 2}}
        assert validate_cluster_condition(condition) is True

    def test_validates_cluster_all_operator_with_sub_conditions(self):
        """Test validating a cluster all operator with sub-conditions."""
        condition = {"all": [{"min_cluster_size": 3}, {"max_cluster_size": 10}]}
        assert validate_cluster_condition(condition) is True

    def test_validates_cluster_any_operator_with_sub_conditions(self):
        """Test validating a cluster any operator with sub-conditions."""
        condition = {"any": [{"min_cluster_size": 5}, {"has_item_with": {"field": "category", "value": "top"}}]}
        assert validate_cluster_condition(condition) is True

    def test_validates_cluster_not_operator_with_sub_condition(self):
        """Test validating a cluster not operator with sub-condition."""
        condition = {"not": {"max_cluster_size": 10}}
        assert validate_cluster_condition(condition) is True

    def test_validates_nested_cluster_conditions(self):
        """Test validating deeply nested cluster conditions."""
        condition = {
            "all": [
                {"min_cluster_size": 3},
                {
                    "any": [
                        {"max_cluster_size": 5},
                        {"not": {"has_item_with": {"field": "category", "value": "accessory"}}},
                    ]
                },
            ]
        }
        assert validate_cluster_condition(condition) is True

    def test_raises_error_for_non_dict_condition(self):
        """Test that non-dict condition raises ValueError."""
        with pytest.raises(ValueError, match="must be a dictionary"):
            validate_cluster_condition("invalid")

    def test_raises_error_for_empty_condition(self):
        """Test that empty dict condition raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_cluster_condition({})

    def test_raises_error_for_multiple_operators(self):
        """Test that multiple operators raise ValueError."""
        with pytest.raises(ValueError, match="exactly one operator"):
            validate_cluster_condition({"min_cluster_size": 3, "max_cluster_size": 10})

    def test_raises_error_for_unknown_operator(self):
        """Test that unknown cluster operator raises ValueError."""
        with pytest.raises(ValueError, match="Unknown cluster operator"):
            validate_cluster_condition({"invalid_cluster_op": {}})

    def test_raises_error_for_all_operator_without_list(self):
        """Test that all operator without list raises ValueError."""
        with pytest.raises(ValueError, match="requires a list"):
            validate_cluster_condition({"all": {"min_cluster_size": 3}})

    def test_raises_error_for_any_operator_without_list(self):
        """Test that any operator without list raises ValueError."""
        with pytest.raises(ValueError, match="requires a list"):
            validate_cluster_condition({"any": {"max_cluster_size": 10}})

    def test_raises_error_for_invalid_sub_condition_in_all(self):
        """Test that invalid sub-condition in all operator raises ValueError."""
        with pytest.raises(ValueError, match="Unknown cluster operator"):
            validate_cluster_condition(
                {"all": [{"min_cluster_size": 3}, {"invalid_cluster_op": {}}]}
            )

    def test_raises_error_for_invalid_sub_condition_in_not(self):
        """Test that invalid sub-condition in not operator raises ValueError."""
        with pytest.raises(ValueError, match="Unknown cluster operator"):
            validate_cluster_condition({"not": {"invalid_cluster_op": {}}})
