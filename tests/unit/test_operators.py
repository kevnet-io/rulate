"""
Tests for operator implementations.

This module tests all pairwise and cluster operators to ensure they correctly
evaluate conditions and return appropriate results and explanations.
"""

import pytest

from rulate.engine.operators import (
    CLUSTER_OPERATOR_REGISTRY,
    OPERATOR_REGISTRY,
    AbsDiffOperator,
    AllOperator,
    AnyEqualsOperator,
    AnyMissingOperator,
    AnyOperator,
    ClusterAllOperator,
    ClusterAnyOperator,
    ClusterNotOperator,
    CountByFieldOperator,
    EqualsOperator,
    FormalityRangeOperator,
    HasDifferentOperator,
    HasItemWithOperator,
    MaxClusterSizeOperator,
    MinClusterSizeOperator,
    NotOperator,
    UniqueValuesOperator,
)
from rulate.models.catalog import Item


# ============================================================================
# Pairwise Operator Tests
# ============================================================================


class TestEqualsOperator:
    """Tests for EqualsOperator."""

    def test_returns_true_when_values_match(self, item_blue_shirt, item_red_shirt):
        """Test that equals returns True when field values match."""
        # Both shirts have category="shirt"
        op = EqualsOperator({"field": "category"})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is True
        assert "category" in explanation
        assert "shirt" in explanation

    def test_returns_false_when_values_differ(self, item_blue_shirt, item_blue_pants):
        """Test that equals returns False when field values differ."""
        op = EqualsOperator({"field": "category"})
        result, explanation = op.evaluate(item_blue_shirt, item_blue_pants)
        assert result is False
        assert "shirt" in explanation
        assert "pants" in explanation

    def test_returns_false_when_field_missing(self, item_blue_shirt, item_minimal):
        """Test equals returns False when one item is missing the field."""
        op = EqualsOperator({"field": "formality"})
        result, explanation = op.evaluate(item_blue_shirt, item_minimal)
        assert result is False
        assert "missing" in explanation.lower()

    def test_returns_false_when_no_field_specified(self, item_blue_shirt, item_red_shirt):
        """Test equals returns False when config has no field."""
        op = EqualsOperator({})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False
        assert "no field specified" in explanation.lower()

    def test_compares_numeric_values(self, item_blue_shirt, item_blue_pants):
        """Test equals works with numeric values."""
        # Both have formality=2
        op = EqualsOperator({"field": "formality"})
        result, explanation = op.evaluate(item_blue_shirt, item_blue_pants)
        assert result is True

    def test_compares_list_values(self):
        """Test equals works with list values."""
        item1 = Item(id="i1", name="I1", attributes={"tags": ["a", "b"]})
        item2 = Item(id="i2", name="I2", attributes={"tags": ["a", "b"]})
        op = EqualsOperator({"field": "tags"})
        result, _ = op.evaluate(item1, item2)
        assert result is True


class TestHasDifferentOperator:
    """Tests for HasDifferentOperator."""

    def test_returns_true_when_values_differ(self, item_blue_shirt, item_red_shirt):
        """Test has_different returns True when values differ."""
        op = HasDifferentOperator({"field": "color"})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is True
        assert "blue" in explanation
        assert "red" in explanation

    def test_returns_false_when_values_match(self, item_blue_shirt, item_blue_pants):
        """Test has_different returns False when values match."""
        op = HasDifferentOperator({"field": "color"})
        result, explanation = op.evaluate(item_blue_shirt, item_blue_pants)
        assert result is False
        assert "same" in explanation.lower()

    def test_returns_true_when_field_missing(self, item_blue_shirt, item_minimal):
        """Test has_different treats missing fields as different."""
        op = HasDifferentOperator({"field": "formality"})
        result, explanation = op.evaluate(item_blue_shirt, item_minimal)
        assert result is True
        assert "missing" in explanation.lower()

    def test_returns_false_when_no_field_specified(self, item_blue_shirt, item_red_shirt):
        """Test has_different returns False when no field specified."""
        op = HasDifferentOperator({})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False
        assert "no field specified" in explanation.lower()


class TestAbsDiffOperator:
    """Tests for AbsDiffOperator."""

    def test_returns_true_when_diff_within_threshold(self, item_blue_shirt, item_blue_pants):
        """Test abs_diff returns True when difference is within threshold."""
        # Both have formality=2, diff=0
        op = AbsDiffOperator({"field": "formality", "max": 1})
        result, explanation = op.evaluate(item_blue_shirt, item_blue_pants)
        assert result is True
        assert "within" in explanation.lower()

    def test_returns_false_when_diff_exceeds_threshold(self, item_blue_shirt, item_black_pants):
        """Test abs_diff returns False when difference exceeds threshold."""
        # formality 2 vs 5, diff=3
        op = AbsDiffOperator({"field": "formality", "max": 2})
        result, explanation = op.evaluate(item_blue_shirt, item_black_pants)
        assert result is False
        assert "exceeds" in explanation.lower()

    def test_returns_true_when_diff_equals_threshold(self, item_blue_shirt, item_red_shirt):
        """Test abs_diff returns True when difference equals threshold exactly."""
        # formality 2 vs 4, diff=2
        op = AbsDiffOperator({"field": "formality", "max": 2})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is True

    def test_works_with_float_values(self):
        """Test abs_diff works with float values."""
        item1 = Item(id="i1", name="I1", attributes={"price": 29.99})
        item2 = Item(id="i2", name="I2", attributes={"price": 35.50})
        op = AbsDiffOperator({"field": "price", "max": 10.0})
        result, _ = op.evaluate(item1, item2)
        assert result is True

    def test_returns_false_when_field_missing(self, item_blue_shirt, item_minimal):
        """Test abs_diff returns False when field missing."""
        op = AbsDiffOperator({"field": "formality", "max": 2})
        result, explanation = op.evaluate(item_blue_shirt, item_minimal)
        assert result is False
        assert "missing" in explanation.lower()

    def test_returns_false_when_no_field_specified(self, item_blue_shirt, item_red_shirt):
        """Test abs_diff returns False when no field specified."""
        op = AbsDiffOperator({"max": 2})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False
        assert "no field specified" in explanation.lower()

    def test_returns_false_when_no_max_specified(self, item_blue_shirt, item_red_shirt):
        """Test abs_diff returns False when no max specified."""
        op = AbsDiffOperator({"field": "formality"})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False
        assert "no max specified" in explanation.lower()

    def test_returns_false_for_non_numeric_values(self):
        """Test abs_diff returns False for non-numeric values."""
        item1 = Item(id="i1", name="I1", attributes={"category": "shirt"})
        item2 = Item(id="i2", name="I2", attributes={"category": "pants"})
        op = AbsDiffOperator({"field": "category", "max": 2})
        result, explanation = op.evaluate(item1, item2)
        assert result is False
        assert "cannot compute" in explanation.lower()


class TestAnyEqualsOperator:
    """Tests for AnyEqualsOperator."""

    def test_returns_true_when_first_item_matches(self, item_blue_shirt, item_red_shirt):
        """Test any_equals returns True when first item matches."""
        op = AnyEqualsOperator({"field": "color", "value": "blue"})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is True
        assert "at least one" in explanation.lower()

    def test_returns_true_when_second_item_matches(self, item_blue_shirt, item_red_shirt):
        """Test any_equals returns True when second item matches."""
        op = AnyEqualsOperator({"field": "color", "value": "red"})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is True

    def test_returns_true_when_both_items_match(self, item_blue_shirt, item_blue_pants):
        """Test any_equals returns True when both items match."""
        op = AnyEqualsOperator({"field": "color", "value": "blue"})
        result, explanation = op.evaluate(item_blue_shirt, item_blue_pants)
        assert result is True

    def test_returns_false_when_neither_matches(self, item_blue_shirt, item_red_shirt):
        """Test any_equals returns False when neither item matches."""
        op = AnyEqualsOperator({"field": "color", "value": "green"})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False
        assert "neither" in explanation.lower()

    def test_returns_false_when_no_field_specified(self, item_blue_shirt, item_red_shirt):
        """Test any_equals returns False when no field specified."""
        op = AnyEqualsOperator({"value": "blue"})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False
        assert "no field specified" in explanation.lower()

    def test_returns_false_when_no_value_specified(self, item_blue_shirt, item_red_shirt):
        """Test any_equals returns False when no value specified."""
        op = AnyEqualsOperator({"field": "color"})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False
        assert "no value specified" in explanation.lower()


class TestAnyMissingOperator:
    """Tests for AnyMissingOperator."""

    def test_returns_true_when_first_item_missing_field(self, item_minimal, item_blue_shirt):
        """Test any_missing returns True when first item missing field."""
        op = AnyMissingOperator({"field": "formality"})
        result, explanation = op.evaluate(item_minimal, item_blue_shirt)
        assert result is True
        assert "missing" in explanation.lower()

    def test_returns_true_when_second_item_missing_field(self, item_blue_shirt, item_minimal):
        """Test any_missing returns True when second item missing field."""
        op = AnyMissingOperator({"field": "formality"})
        result, explanation = op.evaluate(item_blue_shirt, item_minimal)
        assert result is True

    def test_returns_true_when_both_items_missing_field(self, item_minimal):
        """Test any_missing returns True when both items missing field."""
        item2 = Item(id="i2", name="I2", attributes={"category": "pants", "color": "black"})
        op = AnyMissingOperator({"field": "formality"})
        result, explanation = op.evaluate(item_minimal, item2)
        assert result is True

    def test_returns_false_when_both_have_field(self, item_blue_shirt, item_red_shirt):
        """Test any_missing returns False when both items have field."""
        op = AnyMissingOperator({"field": "formality"})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False
        assert "both items have" in explanation.lower()

    def test_returns_false_when_no_field_specified(self, item_blue_shirt, item_red_shirt):
        """Test any_missing returns False when no field specified."""
        op = AnyMissingOperator({})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False
        assert "no field specified" in explanation.lower()


class TestAllOperator:
    """Tests for AllOperator (logical AND)."""

    def test_returns_true_when_all_conditions_pass(self, item_blue_shirt, item_red_shirt):
        """Test all returns True when all sub-conditions pass."""
        op = AllOperator([{"equals": {"field": "category"}}, {"has_different": {"field": "color"}}])
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is True
        assert "all conditions passed" in explanation.lower()

    def test_returns_false_when_one_condition_fails(self, item_blue_shirt, item_blue_pants):
        """Test all returns False when one sub-condition fails."""
        op = AllOperator([{"equals": {"field": "category"}}, {"has_different": {"field": "color"}}])
        result, explanation = op.evaluate(item_blue_shirt, item_blue_pants)
        assert result is False
        assert "and failed" in explanation.lower()

    def test_returns_false_when_all_conditions_fail(self, item_blue_shirt, item_blue_pants):
        """Test all returns False when all sub-conditions fail."""
        op = AllOperator([{"equals": {"field": "color"}}, {"has_different": {"field": "formality"}}])
        result, explanation = op.evaluate(item_blue_shirt, item_blue_pants)
        assert result is False

    def test_returns_false_when_empty_condition_list(self, item_blue_shirt, item_red_shirt):
        """Test all returns False when condition list is empty."""
        op = AllOperator([])
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False
        assert "no conditions" in explanation.lower()

    def test_nested_all_conditions(self, item_blue_shirt, item_red_shirt):
        """Test nested all operators."""
        op = AllOperator(
            [{"equals": {"field": "category"}}, {"all": [{"has_different": {"field": "color"}}]}]
        )
        result, _ = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is True


class TestAnyOperator:
    """Tests for AnyOperator (logical OR)."""

    def test_returns_true_when_first_condition_passes(self, item_blue_shirt, item_red_shirt):
        """Test any returns True when first condition passes."""
        op = AnyOperator([{"equals": {"field": "category"}}, {"equals": {"field": "color"}}])
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is True
        assert "or succeeded" in explanation.lower()

    def test_returns_true_when_second_condition_passes(self, item_blue_shirt, item_blue_pants):
        """Test any returns True when second condition passes."""
        op = AnyOperator([{"equals": {"field": "category"}}, {"equals": {"field": "color"}}])
        result, explanation = op.evaluate(item_blue_shirt, item_blue_pants)
        assert result is True

    def test_returns_true_when_all_conditions_pass(self, item_blue_shirt, item_blue_pants):
        """Test any returns True when all conditions pass."""
        op = AnyOperator([{"has_different": {"field": "category"}}, {"equals": {"field": "color"}}])
        result, explanation = op.evaluate(item_blue_shirt, item_blue_pants)
        assert result is True

    def test_returns_false_when_all_conditions_fail(self, item_blue_shirt, item_blue_pants):
        """Test any returns False when all conditions fail."""
        op = AnyOperator([{"equals": {"field": "category"}}, {"has_different": {"field": "color"}}])
        result, explanation = op.evaluate(item_blue_shirt, item_blue_pants)
        assert result is False
        assert "all or conditions failed" in explanation.lower()

    def test_returns_false_when_empty_condition_list(self, item_blue_shirt, item_red_shirt):
        """Test any returns False when condition list is empty."""
        op = AnyOperator([])
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False
        assert "no conditions" in explanation.lower()


class TestNotOperator:
    """Tests for NotOperator (logical NOT)."""

    def test_returns_true_when_condition_fails(self, item_blue_shirt, item_blue_pants):
        """Test not returns True when sub-condition fails."""
        op = NotOperator({"equals": {"field": "category"}})
        result, explanation = op.evaluate(item_blue_shirt, item_blue_pants)
        assert result is True
        assert "not" in explanation.lower()

    def test_returns_false_when_condition_passes(self, item_blue_shirt, item_red_shirt):
        """Test not returns False when sub-condition passes."""
        op = NotOperator({"equals": {"field": "category"}})
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False

    def test_nested_not_operators(self, item_blue_shirt, item_red_shirt):
        """Test double negation (not not)."""
        op = NotOperator({"not": {"equals": {"field": "category"}}})
        result, _ = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is True  # not not True = True

    def test_returns_false_when_no_condition(self, item_blue_shirt, item_red_shirt):
        """Test not returns False when no condition specified."""
        op = NotOperator(None)
        result, explanation = op.evaluate(item_blue_shirt, item_red_shirt)
        assert result is False
        assert "no condition" in explanation.lower()


# ============================================================================
# Cluster Operator Tests
# ============================================================================


class TestMinClusterSizeOperator:
    """Tests for MinClusterSizeOperator."""

    def test_returns_true_when_size_meets_minimum(self, sample_items_list):
        """Test min_cluster_size returns True when cluster meets minimum."""
        op = MinClusterSizeOperator(3)
        result, explanation = op.evaluate(sample_items_list)  # 4 items
        assert result is True
        assert "4 items" in explanation

    def test_returns_true_when_size_equals_minimum(self, sample_items_list):
        """Test min_cluster_size returns True when size equals minimum."""
        op = MinClusterSizeOperator(4)
        result, explanation = op.evaluate(sample_items_list)  # 4 items
        assert result is True

    def test_returns_false_when_size_below_minimum(self, sample_items_list):
        """Test min_cluster_size returns False when size below minimum."""
        op = MinClusterSizeOperator(5)
        result, explanation = op.evaluate(sample_items_list)  # 4 items
        assert result is False
        assert "only 4" in explanation

    def test_accepts_dict_config(self, sample_items_list):
        """Test min_cluster_size accepts dict config."""
        op = MinClusterSizeOperator({"value": 3})
        result, _ = op.evaluate(sample_items_list)
        assert result is True

    def test_with_empty_cluster(self):
        """Test min_cluster_size with empty cluster."""
        op = MinClusterSizeOperator(1)
        result, _ = op.evaluate([])
        assert result is False


class TestMaxClusterSizeOperator:
    """Tests for MaxClusterSizeOperator."""

    def test_returns_true_when_size_below_maximum(self, sample_items_list):
        """Test max_cluster_size returns True when size below maximum."""
        op = MaxClusterSizeOperator(5)
        result, explanation = op.evaluate(sample_items_list)  # 4 items
        assert result is True
        assert "4 items" in explanation

    def test_returns_true_when_size_equals_maximum(self, sample_items_list):
        """Test max_cluster_size returns True when size equals maximum."""
        op = MaxClusterSizeOperator(4)
        result, explanation = op.evaluate(sample_items_list)  # 4 items
        assert result is True

    def test_returns_false_when_size_exceeds_maximum(self, sample_items_list):
        """Test max_cluster_size returns False when size exceeds maximum."""
        op = MaxClusterSizeOperator(3)
        result, explanation = op.evaluate(sample_items_list)  # 4 items
        assert result is False
        assert "exceeds" in explanation.lower()

    def test_accepts_dict_config(self, sample_items_list):
        """Test max_cluster_size accepts dict config."""
        op = MaxClusterSizeOperator({"value": 10})
        result, _ = op.evaluate(sample_items_list)
        assert result is True


class TestUniqueValuesOperator:
    """Tests for UniqueValuesOperator."""

    def test_returns_true_when_all_values_unique(self):
        """Test unique_values returns True when all field values unique."""
        # Create items with unique colors
        items = [
            Item(id="i1", name="I1", attributes={"color": "red"}),
            Item(id="i2", name="I2", attributes={"color": "blue"}),
            Item(id="i3", name="I3", attributes={"color": "green"}),
        ]
        op = UniqueValuesOperator({"field": "color"})
        result, explanation = op.evaluate(items)
        assert result is True
        assert "unique" in explanation.lower()

    def test_returns_false_when_duplicate_values(self):
        """Test unique_values returns False when duplicate values exist."""
        items = [
            Item(id="i1", name="I1", attributes={"category": "shirt"}),
            Item(id="i2", name="I2", attributes={"category": "pants"}),
            Item(id="i3", name="I3", attributes={"category": "shirt"}),  # duplicate
        ]
        op = UniqueValuesOperator({"field": "category"})
        result, explanation = op.evaluate(items)
        assert result is False
        assert "duplicate" in explanation.lower()

    def test_ignores_none_values(self):
        """Test unique_values ignores None values."""
        items = [
            Item(id="i1", name="I1", attributes={"category": "shirt"}),
            Item(id="i2", name="I2", attributes={"category": "pants"}),
            Item(id="i3", name="I3", attributes={"other": "value"}),  # missing category
        ]
        op = UniqueValuesOperator({"field": "category"})
        result, _ = op.evaluate(items)
        assert result is True  # Only 2 non-None values, both unique

    def test_returns_true_for_empty_cluster(self):
        """Test unique_values returns True for empty cluster."""
        op = UniqueValuesOperator({"field": "category"})
        result, _ = op.evaluate([])
        assert result is True

    def test_returns_false_when_no_field_specified(self, sample_items_list):
        """Test unique_values returns False when no field specified."""
        op = UniqueValuesOperator({})
        result, explanation = op.evaluate(sample_items_list)
        assert result is False
        assert "no field specified" in explanation.lower()


class TestHasItemWithOperator:
    """Tests for HasItemWithOperator."""

    def test_returns_true_when_item_matches(self, sample_items_list):
        """Test has_item_with returns True when matching item exists."""
        op = HasItemWithOperator({"field": "category", "value": "shoes"})
        result, explanation = op.evaluate(sample_items_list)
        assert result is True
        assert "found" in explanation.lower()

    def test_returns_false_when_no_item_matches(self, sample_items_list):
        """Test has_item_with returns False when no matching item."""
        op = HasItemWithOperator({"field": "category", "value": "jacket"})
        result, explanation = op.evaluate(sample_items_list)
        assert result is False
        assert "no items" in explanation.lower()

    def test_counts_multiple_matches(self):
        """Test has_item_with counts multiple matching items."""
        items = [
            Item(id="i1", name="I1", attributes={"category": "shirt"}),
            Item(id="i2", name="I2", attributes={"category": "shirt"}),
            Item(id="i3", name="I3", attributes={"category": "pants"}),
        ]
        op = HasItemWithOperator({"field": "category", "value": "shirt"})
        result, explanation = op.evaluate(items)
        assert result is True
        assert "2" in explanation  # Found 2 items

    def test_returns_false_when_no_field_specified(self, sample_items_list):
        """Test has_item_with returns False when no field specified."""
        op = HasItemWithOperator({"value": "shirt"})
        result, explanation = op.evaluate(sample_items_list)
        assert result is False
        assert "no field specified" in explanation.lower()

    def test_returns_false_when_no_value_specified(self, sample_items_list):
        """Test has_item_with returns False when no value specified."""
        op = HasItemWithOperator({"field": "category"})
        result, explanation = op.evaluate(sample_items_list)
        assert result is False
        assert "no value specified" in explanation.lower()


class TestCountByFieldOperator:
    """Tests for CountByFieldOperator."""

    def test_returns_true_when_meets_min_count(self, sample_items_list):
        """Test count_by_field returns True when distinct count meets minimum."""
        # 3 distinct categories: shirt, pants, shoes
        op = CountByFieldOperator({"field": "category", "min": 3})
        result, explanation = op.evaluate(sample_items_list)
        assert result is True
        assert "3 distinct" in explanation

    def test_returns_false_when_below_min_count(self, sample_items_list):
        """Test count_by_field returns False when below minimum."""
        op = CountByFieldOperator({"field": "category", "min": 5})
        result, explanation = op.evaluate(sample_items_list)
        assert result is False
        assert "only 3" in explanation.lower()

    def test_returns_true_when_below_max_count(self, sample_items_list):
        """Test count_by_field returns True when below maximum."""
        op = CountByFieldOperator({"field": "category", "max": 5})
        result, explanation = op.evaluate(sample_items_list)
        assert result is True

    def test_returns_false_when_exceeds_max_count(self, sample_items_list):
        """Test count_by_field returns False when exceeds maximum."""
        op = CountByFieldOperator({"field": "category", "max": 2})
        result, explanation = op.evaluate(sample_items_list)
        assert result is False
        assert "too many" in explanation.lower()

    def test_works_with_min_and_max(self, sample_items_list):
        """Test count_by_field works with both min and max."""
        op = CountByFieldOperator({"field": "category", "min": 2, "max": 4})
        result, _ = op.evaluate(sample_items_list)
        assert result is True

    def test_ignores_none_values(self):
        """Test count_by_field ignores None values."""
        items = [
            Item(id="i1", name="I1", attributes={"category": "shirt"}),
            Item(id="i2", name="I2", attributes={"category": "pants"}),
            Item(id="i3", name="I3", attributes={"other": "value"}),  # missing category
        ]
        op = CountByFieldOperator({"field": "category", "min": 2})
        result, _ = op.evaluate(items)
        assert result is True  # 2 distinct non-None values

    def test_returns_false_when_no_field_specified(self, sample_items_list):
        """Test count_by_field returns False when no field specified."""
        op = CountByFieldOperator({"min": 2})
        result, explanation = op.evaluate(sample_items_list)
        assert result is False
        assert "no field specified" in explanation.lower()

    def test_returns_false_when_all_values_none(self):
        """Test count_by_field returns False when all values are None."""
        items = [
            Item(id="i1", name="I1", attributes={"other": "value"}),
            Item(id="i2", name="I2", attributes={"other": "value"}),
        ]
        op = CountByFieldOperator({"field": "category", "min": 1})
        result, explanation = op.evaluate(items)
        assert result is False
        assert "no" in explanation.lower()


class TestFormalityRangeOperator:
    """Tests for FormalityRangeOperator."""

    def test_returns_true_when_within_range(self):
        """Test formality_range returns True when range is within max_diff."""
        items = [
            Item(id="i1", name="I1", attributes={"formality": 2}),
            Item(id="i2", name="I2", attributes={"formality": 3}),
            Item(id="i3", name="I3", attributes={"formality": 4}),
        ]
        op = FormalityRangeOperator({"max_diff": 2})
        result, explanation = op.evaluate(items)
        assert result is True
        assert "2-4" in explanation  # Shows range

    def test_returns_false_when_exceeds_range(self):
        """Test formality_range returns False when range exceeds max_diff."""
        items = [
            Item(id="i1", name="I1", attributes={"formality": 1}),
            Item(id="i2", name="I2", attributes={"formality": 5}),
        ]
        op = FormalityRangeOperator({"max_diff": 2})
        result, explanation = op.evaluate(items)
        assert result is False
        assert "exceeds" in explanation.lower()

    def test_works_with_float_formality(self):
        """Test formality_range works with float values."""
        items = [
            Item(id="i1", name="I1", attributes={"formality": 2.5}),
            Item(id="i2", name="I2", attributes={"formality": 3.5}),
        ]
        op = FormalityRangeOperator({"max_diff": 1})
        result, _ = op.evaluate(items)
        assert result is True

    def test_ignores_none_values(self):
        """Test formality_range ignores None values."""
        items = [
            Item(id="i1", name="I1", attributes={"formality": 2}),
            Item(id="i2", name="I2", attributes={"formality": 3}),
            Item(id="i3", name="I3", attributes={"other": "value"}),  # missing formality
        ]
        op = FormalityRangeOperator({"max_diff": 1})
        result, _ = op.evaluate(items)
        assert result is True  # Range 2-3, diff=1

    def test_returns_true_when_all_values_none(self):
        """Test formality_range returns True when all formality values None."""
        items = [
            Item(id="i1", name="I1", attributes={"category": "shirt"}),
            Item(id="i2", name="I2", attributes={"category": "pants"}),
        ]
        op = FormalityRangeOperator({"max_diff": 1})
        result, _ = op.evaluate(items)
        assert result is True  # No formality values to check

    def test_returns_false_for_invalid_formality_value(self):
        """Test formality_range returns False for non-numeric formality."""
        items = [
            Item(id="i1", name="I1", attributes={"formality": "high"}),
            Item(id="i2", name="I2", attributes={"formality": 3}),
        ]
        op = FormalityRangeOperator({"max_diff": 1})
        result, explanation = op.evaluate(items)
        assert result is False
        assert "invalid" in explanation.lower()

    def test_returns_false_when_no_max_diff_specified(self, sample_items_list):
        """Test formality_range returns False when no max_diff specified."""
        op = FormalityRangeOperator({})
        result, explanation = op.evaluate(sample_items_list)
        assert result is False
        assert "no max_diff" in explanation.lower()


class TestClusterAllOperator:
    """Tests for ClusterAllOperator (cluster logical AND)."""

    def test_returns_true_when_all_conditions_pass(self, sample_items_list):
        """Test cluster all returns True when all sub-conditions pass."""
        op = ClusterAllOperator([{"min_cluster_size": 3}, {"max_cluster_size": 10}])
        result, explanation = op.evaluate(sample_items_list)
        assert result is True
        assert "all conditions passed" in explanation.lower()

    def test_returns_false_when_one_condition_fails(self, sample_items_list):
        """Test cluster all returns False when one condition fails."""
        op = ClusterAllOperator([{"min_cluster_size": 3}, {"max_cluster_size": 3}])
        result, explanation = op.evaluate(sample_items_list)  # 4 items
        assert result is False
        assert "and failed" in explanation.lower()

    def test_returns_false_when_empty_condition_list(self, sample_items_list):
        """Test cluster all returns False when condition list empty."""
        op = ClusterAllOperator([])
        result, explanation = op.evaluate(sample_items_list)
        assert result is False
        assert "no conditions" in explanation.lower()


class TestClusterAnyOperator:
    """Tests for ClusterAnyOperator (cluster logical OR)."""

    def test_returns_true_when_first_condition_passes(self, sample_items_list):
        """Test cluster any returns True when first condition passes."""
        op = ClusterAnyOperator([{"min_cluster_size": 3}, {"max_cluster_size": 2}])
        result, explanation = op.evaluate(sample_items_list)  # 4 items
        assert result is True
        assert "or succeeded" in explanation.lower()

    def test_returns_true_when_second_condition_passes(self, sample_items_list):
        """Test cluster any returns True when second condition passes."""
        op = ClusterAnyOperator([{"min_cluster_size": 10}, {"max_cluster_size": 5}])
        result, explanation = op.evaluate(sample_items_list)  # 4 items
        assert result is True

    def test_returns_false_when_all_conditions_fail(self, sample_items_list):
        """Test cluster any returns False when all conditions fail."""
        op = ClusterAnyOperator([{"min_cluster_size": 10}, {"max_cluster_size": 2}])
        result, explanation = op.evaluate(sample_items_list)  # 4 items
        assert result is False
        assert "all or conditions failed" in explanation.lower()

    def test_returns_false_when_empty_condition_list(self, sample_items_list):
        """Test cluster any returns False when condition list empty."""
        op = ClusterAnyOperator([])
        result, explanation = op.evaluate(sample_items_list)
        assert result is False
        assert "no conditions" in explanation.lower()


class TestClusterNotOperator:
    """Tests for ClusterNotOperator (cluster logical NOT)."""

    def test_returns_true_when_condition_fails(self, sample_items_list):
        """Test cluster not returns True when sub-condition fails."""
        op = ClusterNotOperator({"min_cluster_size": 10})
        result, explanation = op.evaluate(sample_items_list)  # 4 items
        assert result is True
        assert "not" in explanation.lower()

    def test_returns_false_when_condition_passes(self, sample_items_list):
        """Test cluster not returns False when sub-condition passes."""
        op = ClusterNotOperator({"min_cluster_size": 3})
        result, explanation = op.evaluate(sample_items_list)  # 4 items
        assert result is False

    def test_returns_false_when_no_condition(self, sample_items_list):
        """Test cluster not returns False when no condition specified."""
        op = ClusterNotOperator(None)
        result, explanation = op.evaluate(sample_items_list)
        assert result is False
        assert "no condition" in explanation.lower()


# ============================================================================
# Operator Registry Tests
# ============================================================================


class TestOperatorRegistry:
    """Tests for operator registry lookups."""

    def test_all_pairwise_operators_registered(self):
        """Test that all pairwise operators are in the registry."""
        expected = [
            "equals",
            "has_different",
            "abs_diff",
            "any_equals",
            "any_missing",
            "all",
            "any",
            "or",
            "not",
        ]
        for op_name in expected:
            assert op_name in OPERATOR_REGISTRY, f"Missing operator: {op_name}"

    def test_all_cluster_operators_registered(self):
        """Test that all cluster operators are in the registry."""
        expected = [
            "min_cluster_size",
            "max_cluster_size",
            "unique_values",
            "has_item_with",
            "count_by_field",
            "formality_range",
            "all",
            "any",
            "or",
            "not",
        ]
        for op_name in expected:
            assert op_name in CLUSTER_OPERATOR_REGISTRY, f"Missing cluster operator: {op_name}"

    def test_or_is_alias_for_any(self):
        """Test that 'or' is an alias for 'any'."""
        assert OPERATOR_REGISTRY["or"] == OPERATOR_REGISTRY["any"]
        assert CLUSTER_OPERATOR_REGISTRY["or"] == CLUSTER_OPERATOR_REGISTRY["any"]
