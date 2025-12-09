"""
Tests for the main evaluation engine.

This module tests the core evaluation functions that orchestrate rule evaluation,
schema validation, and result generation.
"""

import pytest

from rulate.engine.evaluator import evaluate_item_against_catalog, evaluate_matrix, evaluate_pair
from rulate.models.catalog import Catalog, Item
from rulate.models.rule import Rule, RuleSet, RuleType

# ============================================================================
# evaluate_pair() Tests
# ============================================================================


class TestEvaluatePair:
    """Tests for evaluate_pair() function."""

    def test_returns_compatible_when_all_rules_pass(
        self, item_blue_shirt, item_blue_pants, simple_schema
    ):
        """Test that items are compatible when all rules pass."""
        # Blue shirt (formality=2) + Blue pants (formality=2)
        # Different categories, same formality
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                # Exclusion: same category (doesn't apply, they're different)
                Rule(
                    name="different_categories",
                    type=RuleType.EXCLUSION,
                    enabled=True,
                    condition={"equals": {"field": "category"}},
                ),
                # Requirement: formality difference <= 2 (passes)
                Rule(
                    name="similar_formality",
                    type=RuleType.REQUIREMENT,
                    enabled=True,
                    condition={"abs_diff": {"field": "formality", "max": 2}},
                ),
            ],
        )

        result = evaluate_pair(item_blue_shirt, item_blue_pants, ruleset, simple_schema)

        assert result.compatible is True
        assert result.item1_id == item_blue_shirt.id
        assert result.item2_id == item_blue_pants.id
        assert len(result.rules_evaluated) == 2
        assert all(rule_eval.passed for rule_eval in result.rules_evaluated)
        assert result.metadata["ruleset_name"] == "test_rules"
        assert result.metadata["schema_name"] == simple_schema.name

    def test_returns_incompatible_when_exclusion_rule_applies(
        self, item_blue_shirt, item_red_shirt, simple_schema
    ):
        """Test that items are incompatible when exclusion rule applies."""
        # Both are shirts (same category) → exclusion applies
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                Rule(
                    name="same_category_excluded",
                    type=RuleType.EXCLUSION,
                    enabled=True,
                    condition={"equals": {"field": "category"}},
                ),
            ],
        )

        result = evaluate_pair(item_blue_shirt, item_red_shirt, ruleset, simple_schema)

        assert result.compatible is False
        assert len(result.rules_evaluated) == 1
        # Exclusion rule: condition TRUE → rule FAILS → passed=False
        assert result.rules_evaluated[0].passed is False
        assert "shirt" in result.rules_evaluated[0].reason

    def test_returns_incompatible_when_requirement_rule_fails(
        self, item_blue_shirt, item_black_pants, simple_schema
    ):
        """Test that items are incompatible when requirement rule fails."""
        # Formality: 2 vs 5 (diff=3) → requirement fails
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                Rule(
                    name="similar_formality",
                    type=RuleType.REQUIREMENT,
                    enabled=True,
                    condition={"abs_diff": {"field": "formality", "max": 2}},
                ),
            ],
        )

        result = evaluate_pair(item_blue_shirt, item_black_pants, ruleset, simple_schema)

        assert result.compatible is False
        assert len(result.rules_evaluated) == 1
        # Requirement rule: condition FALSE → rule FAILS → passed=False
        assert result.rules_evaluated[0].passed is False
        assert "exceeds" in result.rules_evaluated[0].reason

    def test_exclusion_rule_passed_field_logic(self, item_blue_shirt, item_blue_pants, simple_schema):
        """Test that exclusion rules have correct 'passed' field logic."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                Rule(
                    name="same_category",
                    type=RuleType.EXCLUSION,
                    enabled=True,
                    condition={"equals": {"field": "category"}},
                ),
            ],
        )

        result = evaluate_pair(item_blue_shirt, item_blue_pants, ruleset, simple_schema)

        # Condition: equals category → FALSE (shirt != pants)
        # Exclusion doesn't apply → rule PASSES → passed=True
        assert result.compatible is True
        assert result.rules_evaluated[0].passed is True

    def test_requirement_rule_passed_field_logic(self, item_blue_shirt, item_red_shirt, simple_schema):
        """Test that requirement rules have correct 'passed' field logic."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                Rule(
                    name="similar_formality",
                    type=RuleType.REQUIREMENT,
                    enabled=True,
                    condition={"abs_diff": {"field": "formality", "max": 2}},
                ),
            ],
        )

        result = evaluate_pair(item_blue_shirt, item_red_shirt, ruleset, simple_schema)

        # Condition: abs_diff(2, 4) <= 2 → TRUE
        # Requirement met → rule PASSES → passed=True
        assert result.compatible is True
        assert result.rules_evaluated[0].passed is True

    def test_evaluates_complex_nested_rules(self, item_blue_shirt, item_red_shirt, simple_schema):
        """Test evaluation with complex nested conditions."""
        ruleset = RuleSet(
            name="complex_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                Rule(
                    name="complex_exclusion",
                    type=RuleType.EXCLUSION,
                    enabled=True,
                    condition={
                        "all": [
                            {"equals": {"field": "category"}},
                            {"not": {"has_different": {"field": "color"}}},
                        ]
                    },
                ),
            ],
        )

        result = evaluate_pair(item_blue_shirt, item_red_shirt, ruleset, simple_schema)

        # Same category (shirt) AND same color → would be excluded
        # But they have different colors → exclusion doesn't apply
        assert result.compatible is True
        assert result.rules_evaluated[0].passed is True

    def test_validates_items_against_schema(self, simple_schema):
        """Test that schema validation is performed when provided."""
        invalid_item = Item(id="invalid", name="Invalid", attributes={"category": "invalid_category"})
        valid_item = Item(id="valid", name="Valid", attributes={"category": "shirt", "color": "blue"})

        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        with pytest.raises(ValueError, match="Schema validation failed"):
            evaluate_pair(invalid_item, valid_item, ruleset, simple_schema, validate_schema=True)

    def test_skips_schema_validation_when_disabled(self, simple_schema):
        """Test that schema validation can be disabled."""
        invalid_item = Item(id="invalid", name="Invalid", attributes={"category": "invalid_category"})
        valid_item = Item(id="valid", name="Valid", attributes={"category": "shirt", "color": "blue"})

        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        # Should not raise error when validation disabled
        result = evaluate_pair(invalid_item, valid_item, ruleset, simple_schema, validate_schema=False)
        assert result is not None

    def test_skips_schema_validation_when_no_schema_provided(self, item_blue_shirt, item_red_shirt):
        """Test that no validation occurs when schema not provided."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref="some_schema",
            rules=[],
        )

        # Should not raise error when no schema provided
        result = evaluate_pair(item_blue_shirt, item_red_shirt, ruleset, schema=None)
        assert result is not None
        assert result.metadata["schema_name"] is None

    def test_evaluates_only_enabled_rules(self, item_blue_shirt, item_red_shirt, simple_schema):
        """Test that only enabled rules are evaluated."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                Rule(
                    name="enabled_rule",
                    type=RuleType.EXCLUSION,
                    enabled=True,
                    condition={"equals": {"field": "category"}},
                ),
                Rule(
                    name="disabled_rule",
                    type=RuleType.REQUIREMENT,
                    enabled=False,
                    condition={"abs_diff": {"field": "formality", "max": 0}},  # Would fail
                ),
            ],
        )

        result = evaluate_pair(item_blue_shirt, item_red_shirt, ruleset, simple_schema)

        # Only enabled rule evaluated (disabled rule would make it incompatible)
        assert len(result.rules_evaluated) == 1
        assert result.rules_evaluated[0].rule_name == "enabled_rule"

    def test_handles_rule_evaluation_errors(self, item_blue_shirt, item_red_shirt, simple_schema):
        """Test that rule evaluation errors are caught and handled."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                Rule(
                    name="invalid_rule",
                    type=RuleType.REQUIREMENT,
                    enabled=True,
                    condition={"unknown_operator": {"field": "category"}},
                ),
            ],
        )

        result = evaluate_pair(item_blue_shirt, item_red_shirt, ruleset, simple_schema)

        # Error should be caught and items marked incompatible
        assert result.compatible is False
        assert len(result.rules_evaluated) == 1
        assert result.rules_evaluated[0].passed is False
        assert "error" in result.rules_evaluated[0].reason.lower()

    def test_compatible_items_show_all_rules_passed(
        self, item_blue_shirt, item_blue_pants, simple_schema
    ):
        """Test that compatible items have all rules showing as passed."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                Rule(
                    name="rule1",
                    type=RuleType.EXCLUSION,
                    enabled=True,
                    condition={"equals": {"field": "category"}},
                ),
                Rule(
                    name="rule2",
                    type=RuleType.REQUIREMENT,
                    enabled=True,
                    condition={"abs_diff": {"field": "formality", "max": 2}},
                ),
            ],
        )

        result = evaluate_pair(item_blue_shirt, item_blue_pants, ruleset, simple_schema)

        assert result.compatible is True
        # All rules should show as passed for compatible items
        assert all(rule_eval.passed for rule_eval in result.rules_evaluated)
        assert len([r for r in result.rules_evaluated if r.passed]) == 2

    def test_incompatible_items_show_at_least_one_failed_rule(
        self, item_blue_shirt, item_red_shirt, simple_schema
    ):
        """Test that incompatible items have at least one failed rule."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                Rule(
                    name="same_category",
                    type=RuleType.EXCLUSION,
                    enabled=True,
                    condition={"equals": {"field": "category"}},  # Will apply (both shirts)
                ),
            ],
        )

        result = evaluate_pair(item_blue_shirt, item_red_shirt, ruleset, simple_schema)

        assert result.compatible is False
        # At least one rule should show as failed
        failed_rules = [r for r in result.rules_evaluated if not r.passed]
        assert len(failed_rules) >= 1

    def test_empty_ruleset(self, item_blue_shirt, item_red_shirt, simple_schema):
        """Test evaluation with empty ruleset (no rules)."""
        ruleset = RuleSet(
            name="empty_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        result = evaluate_pair(item_blue_shirt, item_red_shirt, ruleset, simple_schema)

        # No rules → compatible
        assert result.compatible is True
        assert len(result.rules_evaluated) == 0


# ============================================================================
# evaluate_matrix() Tests
# ============================================================================


class TestEvaluateMatrix:
    """Tests for evaluate_matrix() function."""

    def test_evaluates_all_pairs_in_catalog(self, simple_catalog, simple_schema):
        """Test that all unique pairs are evaluated."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        matrix = evaluate_matrix(simple_catalog, ruleset, simple_schema)

        # 5 items → C(5,2) = 10 pairs
        assert len(matrix.results) == 10
        assert matrix.catalog_name == simple_catalog.name
        assert matrix.ruleset_name == ruleset.name
        assert matrix.schema_name == simple_schema.name

    def test_excludes_self_comparisons_by_default(self, simple_catalog, simple_schema):
        """Test that self-comparisons are excluded by default."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        matrix = evaluate_matrix(simple_catalog, ruleset, simple_schema, include_self=False)

        # No pair should have same item IDs
        for result in matrix.results:
            assert result.item1_id != result.item2_id

    def test_includes_self_comparisons_when_enabled(self, simple_catalog, simple_schema):
        """Test that self-comparisons can be included."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        matrix = evaluate_matrix(simple_catalog, ruleset, simple_schema, include_self=True)

        # 5 items with self → 5 + C(5,2) = 5 + 10 = 15 pairs
        assert len(matrix.results) == 15

        # Should have some self-comparisons
        self_comparisons = [r for r in matrix.results if r.item1_id == r.item2_id]
        assert len(self_comparisons) == 5

    def test_raises_error_for_empty_catalog(self, simple_schema):
        """Test that empty catalog raises ValueError."""
        empty_catalog = Catalog(name="empty", schema_ref=simple_schema.name, items=[])
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        with pytest.raises(ValueError, match="Cannot evaluate empty catalog"):
            evaluate_matrix(empty_catalog, ruleset, simple_schema)

    def test_validates_all_items_against_schema(self, simple_schema):
        """Test that all items are validated against schema."""
        catalog_with_invalid = Catalog(
            name="test",
            schema_ref=simple_schema.name,
            items=[
                Item(id="valid", name="Valid", attributes={"category": "shirt", "color": "blue"}),
                Item(id="invalid", name="Invalid", attributes={"category": "invalid_category"}),
            ],
        )
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        with pytest.raises(ValueError, match="Schema validation failed"):
            evaluate_matrix(catalog_with_invalid, ruleset, simple_schema, validate_schema=True)

    def test_skips_validation_when_disabled(self, simple_schema):
        """Test that validation can be skipped."""
        catalog_with_invalid = Catalog(
            name="test",
            schema_ref=simple_schema.name,
            items=[
                Item(id="valid", name="Valid", attributes={"category": "shirt", "color": "blue"}),
                Item(id="invalid", name="Invalid", attributes={"category": "invalid_category"}),
            ],
        )
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        # Should not raise when validation disabled
        matrix = evaluate_matrix(catalog_with_invalid, ruleset, simple_schema, validate_schema=False)
        assert len(matrix.results) == 1  # 1 pair

    def test_applies_rules_to_all_pairs(self, simple_catalog, simple_schema):
        """Test that rules are applied to all pairs."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                Rule(
                    name="same_category",
                    type=RuleType.EXCLUSION,
                    enabled=True,
                    condition={"equals": {"field": "category"}},
                ),
            ],
        )

        matrix = evaluate_matrix(simple_catalog, ruleset, simple_schema)

        # All results should have rule evaluations
        assert all(len(result.rules_evaluated) > 0 for result in matrix.results)

        # Some pairs should be incompatible (same category)
        incompatible = [r for r in matrix.results if not r.compatible]
        assert len(incompatible) > 0

    def test_small_catalog_with_two_items(self, simple_schema):
        """Test matrix evaluation with minimal catalog (2 items)."""
        catalog = Catalog(
            name="small",
            schema_ref=simple_schema.name,
            items=[
                Item(id="i1", name="I1", attributes={"category": "shirt", "color": "blue"}),
                Item(id="i2", name="I2", attributes={"category": "pants", "color": "black"}),
            ],
        )
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        matrix = evaluate_matrix(catalog, ruleset, simple_schema)

        # 2 items → 1 pair
        assert len(matrix.results) == 1
        assert matrix.results[0].item1_id == "i1"
        assert matrix.results[0].item2_id == "i2"

    def test_no_duplicate_pairs(self, simple_catalog, simple_schema):
        """Test that no duplicate pairs are generated."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        matrix = evaluate_matrix(simple_catalog, ruleset, simple_schema)

        # Check for duplicate pairs (both orders)
        pairs = set()
        for result in matrix.results:
            pair = tuple(sorted([result.item1_id, result.item2_id]))
            assert pair not in pairs, f"Duplicate pair found: {pair}"
            pairs.add(pair)


# ============================================================================
# evaluate_item_against_catalog() Tests
# ============================================================================


class TestEvaluateItemAgainstCatalog:
    """Tests for evaluate_item_against_catalog() function."""

    def test_evaluates_item_against_all_catalog_items(
        self, item_blue_shirt, simple_catalog, simple_schema
    ):
        """Test that item is compared against all catalog items."""
        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        results = evaluate_item_against_catalog(item_blue_shirt, simple_catalog, ruleset, simple_schema)

        # Item compared against 5 catalog items, but should exclude itself
        # Blue shirt IS in the catalog, so 5 - 1 = 4 comparisons
        assert len(results) == 4

    def test_excludes_self_comparison(self, simple_catalog, simple_schema):
        """Test that item is not compared against itself."""
        # Use an item from the catalog
        item = simple_catalog.items[0]

        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        results = evaluate_item_against_catalog(item, simple_catalog, ruleset, simple_schema)

        # Should not compare item with itself
        assert all(r.item1_id != r.item2_id for r in results)
        assert all(r.item1_id == item.id for r in results)

    def test_compares_new_item_against_catalog(self, simple_catalog, simple_schema):
        """Test comparing a new item (not in catalog) against catalog."""
        new_item = Item(
            id="new_item",
            name="New Item",
            attributes={"category": "shirt", "color": "green", "formality": 3},
        )

        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        results = evaluate_item_against_catalog(new_item, simple_catalog, ruleset, simple_schema)

        # New item not in catalog → compare against all 5 items
        assert len(results) == 5
        assert all(r.item1_id == new_item.id for r in results)

    def test_applies_rules_to_all_comparisons(self, simple_catalog, simple_schema):
        """Test that rules are applied to all comparisons."""
        new_item = Item(
            id="new_item",
            name="New Item",
            attributes={"category": "shirt", "color": "green", "formality": 3},
        )

        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                Rule(
                    name="same_category",
                    type=RuleType.EXCLUSION,
                    enabled=True,
                    condition={"equals": {"field": "category"}},
                ),
            ],
        )

        results = evaluate_item_against_catalog(new_item, simple_catalog, ruleset, simple_schema)

        # All results should have rule evaluations
        assert all(len(r.rules_evaluated) > 0 for r in results)

        # New shirt compared against catalog shirts → should be incompatible
        incompatible_with_shirts = [
            r for r in results if not r.compatible and r.item2_id in ["blue_shirt", "red_shirt"]
        ]
        assert len(incompatible_with_shirts) == 2

    def test_validates_item_against_schema(self, simple_catalog, simple_schema):
        """Test that item is validated against schema."""
        invalid_item = Item(
            id="invalid",
            name="Invalid",
            attributes={"category": "invalid_category"},
        )

        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        with pytest.raises(ValueError, match="Schema validation failed"):
            evaluate_item_against_catalog(
                invalid_item, simple_catalog, ruleset, simple_schema, validate_schema=True
            )

    def test_skips_validation_when_disabled(self, simple_catalog, simple_schema):
        """Test that validation can be skipped."""
        invalid_item = Item(
            id="invalid",
            name="Invalid",
            attributes={"category": "invalid_category"},
        )

        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        # Should not raise when validation disabled
        results = evaluate_item_against_catalog(
            invalid_item, simple_catalog, ruleset, simple_schema, validate_schema=False
        )
        assert len(results) == 5

    def test_returns_empty_list_for_single_item_catalog(self, simple_schema):
        """Test that single-item catalog returns empty results when comparing same item."""
        item = Item(id="i1", name="I1", attributes={"category": "shirt", "color": "blue"})
        catalog = Catalog(name="single", schema_ref=simple_schema.name, items=[item])

        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        results = evaluate_item_against_catalog(item, catalog, ruleset, simple_schema)

        # Same item in catalog → no comparisons
        assert len(results) == 0

    def test_finds_compatible_items(self, simple_catalog, simple_schema):
        """Test identifying compatible items in catalog."""
        new_item = Item(
            id="new_pants",
            name="New Pants",
            attributes={"category": "pants", "color": "gray", "formality": 3},
        )

        ruleset = RuleSet(
            name="test_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[
                Rule(
                    name="different_categories",
                    type=RuleType.REQUIREMENT,
                    enabled=True,
                    condition={"has_different": {"field": "category"}},
                ),
            ],
        )

        results = evaluate_item_against_catalog(new_item, simple_catalog, ruleset, simple_schema)

        # New pants should be compatible with shirts/shoes, incompatible with other pants
        compatible = [r for r in results if r.compatible]
        incompatible = [r for r in results if not r.compatible]

        assert len(compatible) > 0
        assert len(incompatible) > 0
