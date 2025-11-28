"""
Comprehensive tests for Rule and RuleSet models.

Tests cover:
- Rule creation, validation, and field constraints
- RuleSet creation, validation, and rule management
- Rule filtering by type and enabled status
- Edge cases and error handling
"""

import pytest

from rulate.models.rule import Rule, RuleSet, RuleType


class TestRuleType:
    """Tests for the RuleType enum."""

    def test_has_exclusion_type(self):
        """RuleType includes EXCLUSION."""
        assert RuleType.EXCLUSION == "exclusion"

    def test_has_requirement_type(self):
        """RuleType includes REQUIREMENT."""
        assert RuleType.REQUIREMENT == "requirement"

    def test_has_custom_type(self):
        """RuleType includes CUSTOM."""
        assert RuleType.CUSTOM == "custom"


class TestRule:
    """Tests for the Rule model."""

    def test_creates_rule_with_required_fields(self):
        """Rule can be created with minimal required fields."""
        rule = Rule(
            name="test_rule",
            type=RuleType.EXCLUSION,
            condition={"equals": {"field": "color"}},
        )
        assert rule.name == "test_rule"
        assert rule.type == RuleType.EXCLUSION
        assert rule.condition == {"equals": {"field": "color"}}
        assert rule.enabled is True  # Default value
        assert rule.description is None

    def test_creates_rule_with_all_fields(self):
        """Rule can be created with all fields."""
        rule = Rule(
            name="test_rule",
            type=RuleType.REQUIREMENT,
            description="Test rule description",
            condition={"abs_diff": {"field": "formality", "max": 1}},
            enabled=False,
        )
        assert rule.name == "test_rule"
        assert rule.type == RuleType.REQUIREMENT
        assert rule.description == "Test rule description"
        assert rule.condition == {"abs_diff": {"field": "formality", "max": 1}}
        assert rule.enabled is False

    def test_accepts_exclusion_type(self):
        """Rule accepts EXCLUSION type."""
        rule = Rule(
            name="test_rule",
            type=RuleType.EXCLUSION,
            condition={"equals": {"field": "color"}},
        )
        assert rule.type == RuleType.EXCLUSION

    def test_accepts_requirement_type(self):
        """Rule accepts REQUIREMENT type."""
        rule = Rule(
            name="test_rule",
            type=RuleType.REQUIREMENT,
            condition={"equals": {"field": "color"}},
        )
        assert rule.type == RuleType.REQUIREMENT

    def test_accepts_custom_type(self):
        """Rule accepts CUSTOM type."""
        rule = Rule(
            name="test_rule",
            type=RuleType.CUSTOM,
            condition={"custom_operator": {}},
        )
        assert rule.type == RuleType.CUSTOM

    def test_defaults_enabled_to_true(self):
        """Rule defaults enabled to True when not specified."""
        rule = Rule(
            name="test_rule",
            type=RuleType.EXCLUSION,
            condition={"equals": {"field": "color"}},
        )
        assert rule.enabled is True

    def test_raises_error_for_empty_name(self):
        """Rule name cannot be empty string."""
        with pytest.raises(ValueError, match="Rule name cannot be empty"):
            Rule(
                name="",
                type=RuleType.EXCLUSION,
                condition={"equals": {"field": "color"}},
            )

    def test_raises_error_for_whitespace_only_name(self):
        """Rule name cannot be whitespace only."""
        with pytest.raises(ValueError, match="Rule name cannot be empty"):
            Rule(
                name="   ",
                type=RuleType.EXCLUSION,
                condition={"equals": {"field": "color"}},
            )

    def test_raises_error_for_name_with_spaces(self):
        """Rule name cannot contain spaces."""
        with pytest.raises(ValueError, match="must be alphanumeric"):
            Rule(
                name="test rule",
                type=RuleType.EXCLUSION,
                condition={"equals": {"field": "color"}},
            )

    def test_raises_error_for_name_with_special_chars(self):
        """Rule name cannot contain special characters."""
        with pytest.raises(ValueError, match="must be alphanumeric"):
            Rule(
                name="test@rule",
                type=RuleType.EXCLUSION,
                condition={"equals": {"field": "color"}},
            )

    def test_accepts_name_with_underscores(self):
        """Rule name can contain underscores."""
        rule = Rule(
            name="test_rule_name",
            type=RuleType.EXCLUSION,
            condition={"equals": {"field": "color"}},
        )
        assert rule.name == "test_rule_name"

    def test_accepts_name_with_hyphens(self):
        """Rule name can contain hyphens."""
        rule = Rule(
            name="test-rule-name",
            type=RuleType.EXCLUSION,
            condition={"equals": {"field": "color"}},
        )
        assert rule.name == "test-rule-name"

    def test_accepts_name_with_numbers(self):
        """Rule name can contain numbers."""
        rule = Rule(
            name="test_rule_123",
            type=RuleType.EXCLUSION,
            condition={"equals": {"field": "color"}},
        )
        assert rule.name == "test_rule_123"

    def test_raises_error_for_empty_condition(self):
        """Rule condition cannot be empty dict."""
        with pytest.raises(ValueError, match="Condition cannot be empty"):
            Rule(
                name="test_rule",
                type=RuleType.EXCLUSION,
                condition={},
            )

    def test_raises_error_for_non_dict_condition(self):
        """Rule condition must be a dictionary."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
            Rule(
                name="test_rule",
                type=RuleType.EXCLUSION,
                condition="not a dict",  # type: ignore
            )

    def test_accepts_nested_condition(self):
        """Rule accepts nested condition dictionaries."""
        rule = Rule(
            name="test_rule",
            type=RuleType.EXCLUSION,
            condition={
                "all": [
                    {"equals": {"field": "color"}},
                    {"has_different": {"field": "size"}},
                ]
            },
        )
        assert "all" in rule.condition


class TestRuleSet:
    """Tests for the RuleSet model."""

    def test_creates_ruleset_with_required_fields(self):
        """RuleSet can be created with minimal required fields."""
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
        )
        assert ruleset.name == "test_ruleset"
        assert ruleset.version == "1.0.0"
        assert ruleset.schema_ref == "test_schema"
        assert ruleset.rules == []
        assert ruleset.description is None

    def test_creates_ruleset_with_all_fields(self):
        """RuleSet can be created with all fields."""
        rules = [
            Rule(name="rule1", type=RuleType.EXCLUSION, condition={"equals": {"field": "color"}}),
            Rule(name="rule2", type=RuleType.REQUIREMENT, condition={"abs_diff": {"field": "formality", "max": 1}}),
        ]
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
            description="Test ruleset description",
            rules=rules,
        )
        assert ruleset.name == "test_ruleset"
        assert ruleset.version == "1.0.0"
        assert ruleset.schema_ref == "test_schema"
        assert ruleset.description == "Test ruleset description"
        assert len(ruleset.rules) == 2

    def test_raises_error_for_empty_name(self):
        """RuleSet name cannot be empty string."""
        with pytest.raises(ValueError, match="RuleSet name cannot be empty"):
            RuleSet(name="", version="1.0.0", schema_ref="test_schema")

    def test_raises_error_for_whitespace_only_name(self):
        """RuleSet name cannot be whitespace only."""
        with pytest.raises(ValueError, match="RuleSet name cannot be empty"):
            RuleSet(name="   ", version="1.0.0", schema_ref="test_schema")

    def test_raises_error_for_invalid_version_format(self):
        """RuleSet version must be in format 'major.minor.patch'."""
        with pytest.raises(ValueError, match="Version must be in format"):
            RuleSet(name="test_ruleset", version="1.0", schema_ref="test_schema")

    def test_raises_error_for_version_with_four_parts(self):
        """RuleSet version cannot have four parts."""
        with pytest.raises(ValueError, match="Version must be in format"):
            RuleSet(name="test_ruleset", version="1.0.0.0", schema_ref="test_schema")

    def test_raises_error_for_version_with_non_numeric_parts(self):
        """RuleSet version parts must be integers."""
        with pytest.raises(ValueError, match="Version components must be integers"):
            RuleSet(name="test_ruleset", version="1.0.beta", schema_ref="test_schema")

    def test_accepts_semantic_version(self):
        """RuleSet accepts valid semantic version."""
        ruleset = RuleSet(name="test_ruleset", version="2.5.13", schema_ref="test_schema")
        assert ruleset.version == "2.5.13"

    def test_get_rule_returns_rule_by_name(self):
        """get_rule() returns rule when name exists."""
        rules = [
            Rule(name="rule1", type=RuleType.EXCLUSION, condition={"equals": {"field": "color"}}),
            Rule(name="rule2", type=RuleType.REQUIREMENT, condition={"abs_diff": {"field": "formality", "max": 1}}),
        ]
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
            rules=rules,
        )

        rule = ruleset.get_rule("rule1")
        assert rule is not None
        assert rule.name == "rule1"
        assert rule.type == RuleType.EXCLUSION

    def test_get_rule_returns_none_when_not_found(self):
        """get_rule() returns None when rule doesn't exist."""
        ruleset = RuleSet(name="test_ruleset", version="1.0.0", schema_ref="test_schema")
        assert ruleset.get_rule("nonexistent") is None

    def test_get_active_rules_returns_only_enabled_rules(self):
        """get_active_rules() returns only enabled rules."""
        rules = [
            Rule(name="rule1", type=RuleType.EXCLUSION, condition={"equals": {"field": "color"}}, enabled=True),
            Rule(name="rule2", type=RuleType.REQUIREMENT, condition={"abs_diff": {"field": "formality", "max": 1}}, enabled=False),
            Rule(name="rule3", type=RuleType.EXCLUSION, condition={"equals": {"field": "size"}}, enabled=True),
        ]
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
            rules=rules,
        )

        active = ruleset.get_active_rules()
        assert len(active) == 2
        assert all(rule.enabled for rule in active)
        assert "rule2" not in [rule.name for rule in active]

    def test_get_active_rules_returns_empty_list_when_all_disabled(self):
        """get_active_rules() returns empty list when all rules disabled."""
        rules = [
            Rule(name="rule1", type=RuleType.EXCLUSION, condition={"equals": {"field": "color"}}, enabled=False),
        ]
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
            rules=rules,
        )

        active = ruleset.get_active_rules()
        assert active == []

    def test_get_exclusion_rules_returns_only_exclusion_rules(self):
        """get_exclusion_rules() returns only active exclusion rules."""
        rules = [
            Rule(name="rule1", type=RuleType.EXCLUSION, condition={"equals": {"field": "color"}}, enabled=True),
            Rule(name="rule2", type=RuleType.REQUIREMENT, condition={"abs_diff": {"field": "formality", "max": 1}}, enabled=True),
            Rule(name="rule3", type=RuleType.EXCLUSION, condition={"equals": {"field": "size"}}, enabled=True),
            Rule(name="rule4", type=RuleType.EXCLUSION, condition={"equals": {"field": "category"}}, enabled=False),
        ]
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
            rules=rules,
        )

        exclusions = ruleset.get_exclusion_rules()
        assert len(exclusions) == 2
        assert all(rule.type == RuleType.EXCLUSION for rule in exclusions)
        assert all(rule.enabled for rule in exclusions)

    def test_get_requirement_rules_returns_only_requirement_rules(self):
        """get_requirement_rules() returns only active requirement rules."""
        rules = [
            Rule(name="rule1", type=RuleType.EXCLUSION, condition={"equals": {"field": "color"}}, enabled=True),
            Rule(name="rule2", type=RuleType.REQUIREMENT, condition={"abs_diff": {"field": "formality", "max": 1}}, enabled=True),
            Rule(name="rule3", type=RuleType.REQUIREMENT, condition={"equals": {"field": "size"}}, enabled=True),
            Rule(name="rule4", type=RuleType.REQUIREMENT, condition={"equals": {"field": "category"}}, enabled=False),
        ]
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
            rules=rules,
        )

        requirements = ruleset.get_requirement_rules()
        assert len(requirements) == 2
        assert all(rule.type == RuleType.REQUIREMENT for rule in requirements)
        assert all(rule.enabled for rule in requirements)

    def test_get_custom_rules_returns_only_custom_rules(self):
        """get_custom_rules() returns only active custom rules."""
        rules = [
            Rule(name="rule1", type=RuleType.CUSTOM, condition={"custom_op": {}}, enabled=True),
            Rule(name="rule2", type=RuleType.REQUIREMENT, condition={"abs_diff": {"field": "formality", "max": 1}}, enabled=True),
            Rule(name="rule3", type=RuleType.CUSTOM, condition={"custom_op": {}}, enabled=True),
            Rule(name="rule4", type=RuleType.CUSTOM, condition={"custom_op": {}}, enabled=False),
        ]
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
            rules=rules,
        )

        customs = ruleset.get_custom_rules()
        assert len(customs) == 2
        assert all(rule.type == RuleType.CUSTOM for rule in customs)
        assert all(rule.enabled for rule in customs)

    def test_get_exclusion_rules_returns_empty_list_when_none(self):
        """get_exclusion_rules() returns empty list when no exclusion rules."""
        rules = [
            Rule(name="rule1", type=RuleType.REQUIREMENT, condition={"abs_diff": {"field": "formality", "max": 1}}, enabled=True),
        ]
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
            rules=rules,
        )

        exclusions = ruleset.get_exclusion_rules()
        assert exclusions == []

    def test_get_requirement_rules_returns_empty_list_when_none(self):
        """get_requirement_rules() returns empty list when no requirement rules."""
        rules = [
            Rule(name="rule1", type=RuleType.EXCLUSION, condition={"equals": {"field": "color"}}, enabled=True),
        ]
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
            rules=rules,
        )

        requirements = ruleset.get_requirement_rules()
        assert requirements == []

    def test_get_custom_rules_returns_empty_list_when_none(self):
        """get_custom_rules() returns empty list when no custom rules."""
        rules = [
            Rule(name="rule1", type=RuleType.EXCLUSION, condition={"equals": {"field": "color"}}, enabled=True),
        ]
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
            rules=rules,
        )

        customs = ruleset.get_custom_rules()
        assert customs == []


class TestRuleSetIntegration:
    """Integration tests for RuleSet with multiple rules."""

    def test_filtering_preserves_rule_order(self):
        """Rule filtering methods preserve original order."""
        rules = [
            Rule(name="rule1", type=RuleType.EXCLUSION, condition={"equals": {"field": "a"}}, enabled=True),
            Rule(name="rule2", type=RuleType.EXCLUSION, condition={"equals": {"field": "b"}}, enabled=True),
            Rule(name="rule3", type=RuleType.EXCLUSION, condition={"equals": {"field": "c"}}, enabled=True),
        ]
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
            rules=rules,
        )

        exclusions = ruleset.get_exclusion_rules()
        assert [r.name for r in exclusions] == ["rule1", "rule2", "rule3"]

    def test_mixed_enabled_states_filter_correctly(self):
        """Rules with mixed enabled states filter correctly."""
        rules = [
            Rule(name="rule1", type=RuleType.EXCLUSION, condition={"equals": {"field": "a"}}, enabled=True),
            Rule(name="rule2", type=RuleType.EXCLUSION, condition={"equals": {"field": "b"}}, enabled=False),
            Rule(name="rule3", type=RuleType.REQUIREMENT, condition={"equals": {"field": "c"}}, enabled=True),
            Rule(name="rule4", type=RuleType.REQUIREMENT, condition={"equals": {"field": "d"}}, enabled=False),
        ]
        ruleset = RuleSet(
            name="test_ruleset",
            version="1.0.0",
            schema_ref="test_schema",
            rules=rules,
        )

        exclusions = ruleset.get_exclusion_rules()
        requirements = ruleset.get_requirement_rules()
        active = ruleset.get_active_rules()

        assert len(exclusions) == 1
        assert exclusions[0].name == "rule1"
        assert len(requirements) == 1
        assert requirements[0].name == "rule3"
        assert len(active) == 2
