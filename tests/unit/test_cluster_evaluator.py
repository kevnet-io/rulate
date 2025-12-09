"""
Tests for the cluster evaluation engine.

This module tests cluster finding using the Bron-Kerbosch algorithm,
cluster rule validation, and relationship analysis.
"""

import pytest

from rulate.engine.cluster_evaluator import (
    _bron_kerbosch,
    _build_adjacency_from_matrix,
    _choose_pivot,
    _find_relationships,
    find_clusters,
    validate_cluster,
)
from rulate.models.catalog import Catalog, Item
from rulate.models.cluster import Cluster, ClusterRule, ClusterRuleSet
from rulate.models.evaluation import ComparisonResult, EvaluationMatrix
from rulate.models.rule import Rule, RuleSet, RuleType

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def cluster_compatible_catalog():
    """Catalog with items designed for cluster testing."""
    return Catalog(
        name="cluster_catalog",
        schema_ref="test_schema",
        items=[
            Item(id="i1", name="I1", attributes={"category": "shirt", "color": "blue", "formality": 2}),
            Item(id="i2", name="I2", attributes={"category": "pants", "color": "blue", "formality": 2}),
            Item(id="i3", name="I3", attributes={"category": "shoes", "color": "brown", "formality": 2}),
            Item(id="i4", name="I4", attributes={"category": "shirt", "color": "red", "formality": 3}),
        ],
    )


@pytest.fixture
def simple_cluster_ruleset():
    """Simple cluster ruleset with basic size constraints."""
    return ClusterRuleSet(
        name="simple_cluster_rules",
        version="1.0.0",
        schema_ref="test_schema",
        pairwise_ruleset_ref="test_rules",
        rules=[
            ClusterRule(
                name="min_size",
                type=RuleType.REQUIREMENT,
                enabled=True,
                condition={"min_cluster_size": 2},
            ),
            ClusterRule(
                name="max_size",
                type=RuleType.REQUIREMENT,
                enabled=True,
                condition={"max_cluster_size": 10},
            ),
        ],
    )


@pytest.fixture
def complex_cluster_ruleset():
    """Complex cluster ruleset with multiple constraints."""
    return ClusterRuleSet(
        name="complex_cluster_rules",
        version="1.0.0",
        schema_ref="test_schema",
        pairwise_ruleset_ref="test_rules",
        rules=[
            ClusterRule(
                name="min_size",
                type=RuleType.REQUIREMENT,
                enabled=True,
                condition={"min_cluster_size": 3},
            ),
            ClusterRule(
                name="unique_categories",
                type=RuleType.REQUIREMENT,
                enabled=True,
                condition={"unique_values": {"field": "category"}},
            ),
            ClusterRule(
                name="formality_consistency",
                type=RuleType.REQUIREMENT,
                enabled=True,
                condition={"formality_range": {"max_diff": 1}},
            ),
        ],
    )


# ============================================================================
# find_clusters() Tests
# ============================================================================


class TestFindClusters:
    """Tests for find_clusters() function."""

    def test_finds_clusters_in_compatible_catalog(
        self, cluster_compatible_catalog, simple_schema, simple_cluster_ruleset
    ):
        """Test finding clusters in a catalog with compatible items."""
        # Very permissive ruleset - everything is compatible
        pairwise_ruleset = RuleSet(
            name="pairwise_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],  # No rules = everything compatible
        )

        analysis = find_clusters(
            cluster_compatible_catalog,
            pairwise_ruleset,
            simple_cluster_ruleset,
            simple_schema,
        )

        # With no pairwise rules, all items are compatible
        # Should find at least one cluster containing all 4 items
        assert analysis.total_clusters > 0
        assert analysis.catalog_name == cluster_compatible_catalog.name
        assert analysis.ruleset_name == pairwise_ruleset.name
        assert analysis.cluster_ruleset_name == simple_cluster_ruleset.name
        assert analysis.max_cluster_size >= 2
        assert analysis.total_items_covered >= 2

    def test_respects_min_cluster_size(self, cluster_compatible_catalog, simple_schema):
        """Test that min_cluster_size parameter is respected."""
        pairwise_ruleset = RuleSet(
            name="pairwise_rules",
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

        cluster_ruleset = ClusterRuleSet(
            name="cluster_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            pairwise_ruleset_ref=pairwise_ruleset.name,
            rules=[],
        )

        analysis = find_clusters(
            cluster_compatible_catalog,
            pairwise_ruleset,
            cluster_ruleset,
            simple_schema,
            min_cluster_size=3,
        )

        # All clusters should have at least 3 items
        assert all(cluster.size >= 3 for cluster in analysis.clusters)

    def test_respects_max_clusters_limit(self, cluster_compatible_catalog, simple_schema):
        """Test that max_clusters parameter limits results."""
        pairwise_ruleset = RuleSet(
            name="pairwise_rules",
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

        cluster_ruleset = ClusterRuleSet(
            name="cluster_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            pairwise_ruleset_ref=pairwise_ruleset.name,
            rules=[],
        )

        analysis = find_clusters(
            cluster_compatible_catalog,
            pairwise_ruleset,
            cluster_ruleset,
            simple_schema,
            max_clusters=2,
        )

        # Should have at most 2 clusters
        assert len(analysis.clusters) <= 2

    def test_raises_error_for_empty_catalog(self, simple_schema, simple_cluster_ruleset):
        """Test that empty catalog raises ValueError."""
        empty_catalog = Catalog(name="empty", schema_ref=simple_schema.name, items=[])
        pairwise_ruleset = RuleSet(
            name="pairwise_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            rules=[],
        )

        with pytest.raises(ValueError, match="Cannot find clusters in empty catalog"):
            find_clusters(empty_catalog, pairwise_ruleset, simple_cluster_ruleset, simple_schema)

    def test_marks_maximum_clusters_correctly(self, cluster_compatible_catalog, simple_schema):
        """Test that maximum clusters (largest size) are marked correctly."""
        pairwise_ruleset = RuleSet(
            name="pairwise_rules",
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

        cluster_ruleset = ClusterRuleSet(
            name="cluster_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            pairwise_ruleset_ref=pairwise_ruleset.name,
            rules=[],
        )

        analysis = find_clusters(
            cluster_compatible_catalog,
            pairwise_ruleset,
            cluster_ruleset,
            simple_schema,
        )

        if analysis.clusters:
            # At least one cluster should be marked as maximum
            maximum_clusters = [c for c in analysis.clusters if c.is_maximum]
            assert len(maximum_clusters) > 0

            # All maximum clusters should have the same size (the largest)
            max_size = analysis.max_cluster_size
            for cluster in maximum_clusters:
                assert cluster.size == max_size

    def test_all_clusters_marked_as_maximal(self, cluster_compatible_catalog, simple_schema):
        """Test that all clusters from Bron-Kerbosch are marked as maximal."""
        pairwise_ruleset = RuleSet(
            name="pairwise_rules",
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

        cluster_ruleset = ClusterRuleSet(
            name="cluster_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            pairwise_ruleset_ref=pairwise_ruleset.name,
            rules=[],
        )

        analysis = find_clusters(
            cluster_compatible_catalog,
            pairwise_ruleset,
            cluster_ruleset,
            simple_schema,
        )

        # All clusters should be maximal (from Bron-Kerbosch)
        assert all(cluster.is_maximal for cluster in analysis.clusters)

    def test_calculates_statistics_correctly(self, cluster_compatible_catalog, simple_schema):
        """Test that cluster statistics are calculated correctly."""
        pairwise_ruleset = RuleSet(
            name="pairwise_rules",
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

        cluster_ruleset = ClusterRuleSet(
            name="cluster_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            pairwise_ruleset_ref=pairwise_ruleset.name,
            rules=[],
        )

        analysis = find_clusters(
            cluster_compatible_catalog,
            pairwise_ruleset,
            cluster_ruleset,
            simple_schema,
        )

        if analysis.clusters:
            # Check statistics match actual clusters
            assert analysis.total_clusters == len(analysis.clusters)
            assert analysis.max_cluster_size == max(c.size for c in analysis.clusters)
            assert analysis.min_cluster_size == min(c.size for c in analysis.clusters)

            # Average should be reasonable
            expected_avg = sum(c.size for c in analysis.clusters) / len(analysis.clusters)
            assert abs(analysis.avg_cluster_size - expected_avg) < 0.01

    def test_filters_clusters_by_cluster_rules(self, cluster_compatible_catalog, simple_schema):
        """Test that cluster rules filter out invalid clusters."""
        pairwise_ruleset = RuleSet(
            name="pairwise_rules",
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

        # Cluster ruleset requiring at least 5 items (impossible with 4-item catalog)
        strict_cluster_ruleset = ClusterRuleSet(
            name="strict_cluster_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            pairwise_ruleset_ref=pairwise_ruleset.name,
            rules=[
                ClusterRule(
                    name="min_size_5",
                    type=RuleType.REQUIREMENT,
                    enabled=True,
                    condition={"min_cluster_size": 5},
                ),
            ],
        )

        analysis = find_clusters(
            cluster_compatible_catalog,
            pairwise_ruleset,
            strict_cluster_ruleset,
            simple_schema,
        )

        # Should have no clusters (impossible constraint)
        assert analysis.total_clusters == 0
        assert len(analysis.clusters) == 0

    def test_no_clusters_when_all_incompatible(self, simple_schema):
        """Test no clusters found when all items are incompatible."""
        catalog = Catalog(
            name="incompatible",
            schema_ref=simple_schema.name,
            items=[
                Item(id="i1", name="I1", attributes={"category": "shirt", "color": "blue"}),
                Item(id="i2", name="I2", attributes={"category": "shirt", "color": "red"}),
                Item(id="i3", name="I3", attributes={"category": "shirt", "color": "green"}),
            ],
        )

        # Same category = incompatible
        pairwise_ruleset = RuleSet(
            name="pairwise_rules",
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

        cluster_ruleset = ClusterRuleSet(
            name="cluster_rules",
            version="1.0.0",
            schema_ref=simple_schema.name,
            pairwise_ruleset_ref=pairwise_ruleset.name,
            rules=[],
        )

        analysis = find_clusters(catalog, pairwise_ruleset, cluster_ruleset, simple_schema)

        # No clusters should be found
        assert analysis.total_clusters == 0
        assert analysis.max_cluster_size == 0


# ============================================================================
# validate_cluster() Tests
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
                    condition={"min_cluster_size": 2},
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


class TestBuildAdjacencyFromMatrix:
    """Tests for _build_adjacency_from_matrix() function."""

    def test_builds_adjacency_list_from_compatible_pairs(self):
        """Test building adjacency list from compatible pairs."""
        matrix = EvaluationMatrix(
            catalog_name="test",
            ruleset_name="test",
            schema_name="test",
            results=[
                ComparisonResult(
                    item1_id="i1",
                    item2_id="i2",
                    compatible=True,
                    rules_evaluated=[],
                ),
                ComparisonResult(
                    item1_id="i2",
                    item2_id="i3",
                    compatible=True,
                    rules_evaluated=[],
                ),
                ComparisonResult(
                    item1_id="i1",
                    item2_id="i3",
                    compatible=False,
                    rules_evaluated=[],
                ),
            ],
        )

        adjacency = _build_adjacency_from_matrix(matrix)

        # i1-i2 compatible, i2-i3 compatible, i1-i3 incompatible
        assert "i2" in adjacency["i1"]
        assert "i1" in adjacency["i2"]
        assert "i3" in adjacency["i2"]
        assert "i2" in adjacency["i3"]
        assert "i3" not in adjacency["i1"]
        assert "i1" not in adjacency["i3"]

    def test_adjacency_is_symmetric(self):
        """Test that adjacency list is symmetric (undirected graph)."""
        matrix = EvaluationMatrix(
            catalog_name="test",
            ruleset_name="test",
            schema_name="test",
            results=[
                ComparisonResult(
                    item1_id="i1",
                    item2_id="i2",
                    compatible=True,
                    rules_evaluated=[],
                ),
            ],
        )

        adjacency = _build_adjacency_from_matrix(matrix)

        # Symmetric: i1→i2 and i2→i1
        assert "i2" in adjacency["i1"]
        assert "i1" in adjacency["i2"]

    def test_excludes_incompatible_pairs(self):
        """Test that incompatible pairs are not in adjacency list."""
        matrix = EvaluationMatrix(
            catalog_name="test",
            ruleset_name="test",
            schema_name="test",
            results=[
                ComparisonResult(
                    item1_id="i1",
                    item2_id="i2",
                    compatible=False,
                    rules_evaluated=[],
                ),
            ],
        )

        adjacency = _build_adjacency_from_matrix(matrix)

        # Incompatible → no edge
        assert "i2" not in adjacency["i1"]
        assert "i1" not in adjacency["i2"]

    def test_initializes_all_items(self):
        """Test that all items get initialized in adjacency list."""
        matrix = EvaluationMatrix(
            catalog_name="test",
            ruleset_name="test",
            schema_name="test",
            results=[
                ComparisonResult(
                    item1_id="i1",
                    item2_id="i2",
                    compatible=False,
                    rules_evaluated=[],
                ),
            ],
        )

        adjacency = _build_adjacency_from_matrix(matrix)

        # Both items should be in adjacency even if not compatible
        assert "i1" in adjacency
        assert "i2" in adjacency


# ============================================================================
# _bron_kerbosch() Tests
# ============================================================================


class TestBronKerbosch:
    """Tests for _bron_kerbosch() algorithm."""

    def test_finds_single_clique_in_triangle(self):
        """Test finding a clique in a triangle graph (3 nodes all connected)."""
        adjacency = {
            "i1": {"i2", "i3"},
            "i2": {"i1", "i3"},
            "i3": {"i1", "i2"},
        }

        cliques = []
        _bron_kerbosch(
            R=set(),
            P=set(adjacency.keys()),
            X=set(),
            adjacency=adjacency,
            cliques=cliques,
        )

        # Triangle is a single maximal clique of size 3
        assert len(cliques) == 1
        assert cliques[0] == {"i1", "i2", "i3"}

    def test_finds_multiple_cliques(self):
        """Test finding multiple cliques in a graph."""
        # Graph: i1-i2-i3 (triangle) and i4-i5 (separate pair)
        adjacency = {
            "i1": {"i2", "i3"},
            "i2": {"i1", "i3"},
            "i3": {"i1", "i2"},
            "i4": {"i5"},
            "i5": {"i4"},
        }

        cliques = []
        _bron_kerbosch(
            R=set(),
            P=set(adjacency.keys()),
            X=set(),
            adjacency=adjacency,
            cliques=cliques,
        )

        # Should find 2 cliques: {i1,i2,i3} and {i4,i5}
        assert len(cliques) == 2
        assert {"i1", "i2", "i3"} in cliques
        assert {"i4", "i5"} in cliques

    def test_finds_no_cliques_in_empty_graph(self):
        """Test that empty graph produces no cliques."""
        adjacency = {}
        cliques = []

        _bron_kerbosch(
            R=set(),
            P=set(adjacency.keys()),
            X=set(),
            adjacency=adjacency,
            cliques=cliques,
        )

        assert len(cliques) == 0

    def test_finds_singleton_cliques_with_isolated_nodes(self):
        """Test graph with isolated nodes (no edges)."""
        adjacency = {
            "i1": set(),
            "i2": set(),
            "i3": set(),
        }

        cliques = []
        _bron_kerbosch(
            R=set(),
            P=set(adjacency.keys()),
            X=set(),
            adjacency=adjacency,
            cliques=cliques,
        )

        # Isolated nodes → each node is a maximal clique of size 1
        assert len(cliques) == 3
        assert all(len(clique) == 1 for clique in cliques)

    def test_finds_maximal_cliques_only(self):
        """Test that only maximal cliques are returned (not subsets)."""
        # Graph: 4-node complete graph (K4)
        adjacency = {
            "i1": {"i2", "i3", "i4"},
            "i2": {"i1", "i3", "i4"},
            "i3": {"i1", "i2", "i4"},
            "i4": {"i1", "i2", "i3"},
        }

        cliques = []
        _bron_kerbosch(
            R=set(),
            P=set(adjacency.keys()),
            X=set(),
            adjacency=adjacency,
            cliques=cliques,
        )

        # K4 has one maximal clique: all 4 nodes
        assert len(cliques) == 1
        assert cliques[0] == {"i1", "i2", "i3", "i4"}


# ============================================================================
# _choose_pivot() Tests
# ============================================================================


class TestChoosePivot:
    """Tests for _choose_pivot() function."""

    def test_chooses_vertex_with_most_neighbors(self):
        """Test that pivot is vertex with most neighbors in P."""
        P = {"i1", "i2", "i3"}
        X = set()
        adjacency = {
            "i1": {"i2", "i3"},  # 2 neighbors in P
            "i2": {"i1"},  # 1 neighbor in P
            "i3": {"i1"},  # 1 neighbor in P
        }

        pivot = _choose_pivot(P, X, adjacency)

        # i1 has the most neighbors in P
        assert pivot == "i1"

    def test_returns_none_for_empty_union(self):
        """Test that None is returned when P ∪ X is empty."""
        pivot = _choose_pivot(set(), set(), {})
        assert pivot is None

    def test_considers_vertices_in_both_p_and_x(self):
        """Test that pivot can be chosen from X as well as P."""
        P = {"i1"}
        X = {"i2", "i3"}
        adjacency = {
            "i1": set(),  # 0 neighbors in P
            "i2": {"i1"},  # 1 neighbor in P
            "i3": set(),  # 0 neighbors in P
        }

        pivot = _choose_pivot(P, X, adjacency)

        # i2 has the most neighbors in P (even though it's in X)
        assert pivot == "i2"


# ============================================================================
# _find_relationships() Tests
# ============================================================================


class TestFindRelationships:
    """Tests for _find_relationships() function."""

    def test_finds_subset_relationship(self):
        """Test detecting subset relationships."""
        clusters = [
            Cluster(
                id="c1",
                item_ids=["i1", "i2"],
                size=2,
                is_maximal=True,
                is_maximum=False,
                rule_evaluations=[],
            ),
            Cluster(
                id="c2",
                item_ids=["i1", "i2", "i3"],
                size=3,
                is_maximal=True,
                is_maximum=True,
                rule_evaluations=[],
            ),
        ]

        relationships = _find_relationships(clusters)

        # c1 is subset of c2, c2 is superset of c1
        subset_rels = [r for r in relationships if r.relationship_type == "subset"]
        superset_rels = [r for r in relationships if r.relationship_type == "superset"]

        assert len(subset_rels) == 1
        assert len(superset_rels) == 1
        assert subset_rels[0].cluster_id == "c1"
        assert subset_rels[0].related_cluster_id == "c2"
        assert superset_rels[0].cluster_id == "c2"
        assert superset_rels[0].related_cluster_id == "c1"

    def test_finds_overlapping_relationship(self):
        """Test detecting overlapping relationships."""
        clusters = [
            Cluster(
                id="c1",
                item_ids=["i1", "i2", "i3"],
                size=3,
                is_maximal=True,
                is_maximum=True,
                rule_evaluations=[],
            ),
            Cluster(
                id="c2",
                item_ids=["i2", "i3", "i4"],
                size=3,
                is_maximal=True,
                is_maximum=True,
                rule_evaluations=[],
            ),
        ]

        relationships = _find_relationships(clusters)

        # Both should have overlapping relationship (symmetric)
        overlapping_rels = [r for r in relationships if r.relationship_type == "overlapping"]

        assert len(overlapping_rels) == 2
        assert overlapping_rels[0].overlap_size == 2  # i2, i3 shared
        assert sorted(overlapping_rels[0].shared_items) == ["i2", "i3"]

    def test_no_relationships_for_disjoint_clusters(self):
        """Test that disjoint clusters have no relationships."""
        clusters = [
            Cluster(
                id="c1",
                item_ids=["i1", "i2"],
                size=2,
                is_maximal=True,
                is_maximum=False,
                rule_evaluations=[],
            ),
            Cluster(
                id="c2",
                item_ids=["i3", "i4"],
                size=2,
                is_maximal=True,
                is_maximum=False,
                rule_evaluations=[],
            ),
        ]

        relationships = _find_relationships(clusters)

        # Disjoint → no relationships
        assert len(relationships) == 0

    def test_ignores_identical_clusters(self):
        """Test that identical clusters are ignored."""
        clusters = [
            Cluster(
                id="c1",
                item_ids=["i1", "i2"],
                size=2,
                is_maximal=True,
                is_maximum=False,
                rule_evaluations=[],
            ),
            Cluster(
                id="c2",
                item_ids=["i1", "i2"],  # Identical to c1
                size=2,
                is_maximal=True,
                is_maximum=False,
                rule_evaluations=[],
            ),
        ]

        relationships = _find_relationships(clusters)

        # Identical clusters should be ignored
        assert len(relationships) == 0

    def test_calculates_overlap_size_correctly(self):
        """Test that overlap size is calculated correctly."""
        clusters = [
            Cluster(
                id="c1",
                item_ids=["i1", "i2", "i3"],
                size=3,
                is_maximal=True,
                is_maximum=False,
                rule_evaluations=[],
            ),
            Cluster(
                id="c2",
                item_ids=["i2", "i3", "i4", "i5"],
                size=4,
                is_maximal=True,
                is_maximum=True,
                rule_evaluations=[],
            ),
        ]

        relationships = _find_relationships(clusters)

        # Overlapping with 2 shared items (i2, i3)
        overlapping_rels = [r for r in relationships if r.relationship_type == "overlapping"]
        assert len(overlapping_rels) == 2
        assert all(r.overlap_size == 2 for r in overlapping_rels)
