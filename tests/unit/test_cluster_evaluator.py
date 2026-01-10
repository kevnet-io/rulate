"""
Tests for the cluster evaluation engine.

This module tests cluster rule validation.
"""

from rulate.engine.cluster_evaluator import validate_cluster
from rulate.models.catalog import Item
from rulate.models.cluster import ClusterRule, ClusterRuleSet
from rulate.models.rule import RuleType

# ============================================================================
# Test Classes
# ============================================================================


class TestValidateCluster:
    """Tests for validate_cluster() function."""

    def test_returns_true_for_valid_cluster(self):
        """Test that valid cluster passes all rules."""
        items = [
            Item(id="i1", name="I1", attributes={"category": "shirt"}),
            Item(id="i2", name="I2", attributes={"category": "pants"}),
            Item(id="i3", name="I3", attributes={"category": "shoes"}),
        ]

        cluster_ruleset = ClusterRuleSet(
            name="cluster_rules",
            version="1.0.0",
            schema_ref="test_schema",
            pairwise_ruleset_ref="test_rules",
            rules=[
                ClusterRule(
                    name="min_size",
                    type=RuleType.REQUIREMENT,
                    enabled=True,
                    condition={"unique_values": {"field": "category"}},
                ),
                ClusterRule(
                    name="unique_categories",
                    type=RuleType.REQUIREMENT,
                    enabled=True,
                    condition={"unique_values": {"field": "category"}},
                ),
            ],
        )

        is_valid, rule_evals = validate_cluster(items, cluster_ruleset)

        assert is_valid is True
        assert len(rule_evals) == 2
        assert all(rule_eval.passed for rule_eval in rule_evals)

    def test_returns_false_when_exclusion_rule_applies(self):
        """Test that cluster fails when exclusion rule applies."""
        items = [
            Item(id="i1", name="I1", attributes={"category": "shirt"}),
            Item(id="i2", name="I2", attributes={"category": "shirt"}),  # Duplicate category
        ]

        cluster_ruleset = ClusterRuleSet(
            name="cluster_rules",
            version="1.0.0",
            schema_ref="test_schema",
            pairwise_ruleset_ref="test_rules",
            rules=[
                ClusterRule(
                    name="no_duplicate_categories",
                    type=RuleType.EXCLUSION,
                    enabled=True,
                    condition={"not": {"unique_values": {"field": "category"}}},
                ),
            ],
        )

        is_valid, rule_evals = validate_cluster(items, cluster_ruleset)

        assert is_valid is False
        assert len(rule_evals) == 1
        assert rule_evals[0].passed is False  # Exclusion applies (not unique → TRUE → excluded)

    def test_returns_false_when_requirement_rule_fails(self):
        """Test that cluster fails when requirement rule fails."""
        items = [
            Item(id="i1", name="I1", attributes={"category": "shirt"}),
            Item(id="i2", name="I2", attributes={"category": "shirt"}),  # Duplicate
        ]

        cluster_ruleset = ClusterRuleSet(
            name="cluster_rules",
            version="1.0.0",
            schema_ref="test_schema",
            pairwise_ruleset_ref="test_rules",
            rules=[
                ClusterRule(
                    name="unique_categories",
                    type=RuleType.REQUIREMENT,
                    enabled=True,
                    condition={"unique_values": {"field": "category"}},
                ),
            ],
        )

        is_valid, rule_evals = validate_cluster(items, cluster_ruleset)

        assert is_valid is False
        assert len(rule_evals) == 1
        assert rule_evals[0].passed is False

    def test_exclusion_rule_passed_field_logic(self):
        """Test that exclusion rules have correct 'passed' field logic."""
        items = [
            Item(id="i1", name="I1", attributes={"category": "shirt"}),
            Item(id="i2", name="I2", attributes={"category": "pants"}),
        ]

        cluster_ruleset = ClusterRuleSet(
            name="cluster_rules",
            version="1.0.0",
            schema_ref="test_schema",
            pairwise_ruleset_ref="test_rules",
            rules=[
                ClusterRule(
                    name="no_duplicates",
                    type=RuleType.EXCLUSION,
                    enabled=True,
                    condition={"not": {"unique_values": {"field": "category"}}},
                ),
            ],
        )

        is_valid, rule_evals = validate_cluster(items, cluster_ruleset)

        # Condition: not unique_values → FALSE (categories ARE unique)
        # Exclusion doesn't apply → cluster valid → passed=True
        assert is_valid is True
        assert rule_evals[0].passed is True

    def test_handles_rule_evaluation_errors(self):
        """Test that rule evaluation errors are caught and handled."""
        items = [
            Item(id="i1", name="I1", attributes={"formality": "high"}),  # Invalid type
            Item(id="i2", name="I2", attributes={"formality": 3}),
        ]

        cluster_ruleset = ClusterRuleSet(
            name="cluster_rules",
            version="1.0.0",
            schema_ref="test_schema",
            pairwise_ruleset_ref="test_rules",
            rules=[
                ClusterRule(
                    name="formality_range",
                    type=RuleType.REQUIREMENT,
                    enabled=True,
                    condition={"formality_range": {"max_diff": 1}},
                ),
            ],
        )

        is_valid, rule_evals = validate_cluster(items, cluster_ruleset)

        # Error should make cluster invalid
        assert is_valid is False
        assert len(rule_evals) == 1
        assert rule_evals[0].passed is False
        assert "invalid" in rule_evals[0].reason.lower()

    def test_empty_ruleset(self):
        """Test validation with empty ruleset (no rules)."""
        items = [
            Item(id="i1", name="I1", attributes={"category": "shirt"}),
            Item(id="i2", name="I2", attributes={"category": "pants"}),
        ]

        cluster_ruleset = ClusterRuleSet(
            name="empty_rules",
            version="1.0.0",
            schema_ref="test_schema",
            pairwise_ruleset_ref="test_rules",
            rules=[],
        )

        is_valid, rule_evals = validate_cluster(items, cluster_ruleset)

        # No rules → valid
        assert is_valid is True
        assert len(rule_evals) == 0


# ============================================================================
# _build_adjacency_from_matrix() Tests
# ============================================================================
