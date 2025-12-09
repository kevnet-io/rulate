"""
Cluster evaluation engine for finding compatible item sets.

This module implements the cluster finding algorithm using the Bron-Kerbosch
algorithm to find all maximal cliques in a compatibility graph, then validates
them against cluster-level rules.
"""

from datetime import datetime

from rulate.engine.cluster_condition_evaluator import evaluate_cluster_condition
from rulate.engine.evaluator import evaluate_matrix
from rulate.models.catalog import Catalog, Item
from rulate.models.cluster import (
    Cluster,
    ClusterAnalysis,
    ClusterRelationship,
    ClusterRuleSet,
    generate_cluster_id,
)
from rulate.models.evaluation import EvaluationMatrix, RuleEvaluation
from rulate.models.rule import RuleSet
from rulate.models.schema import Schema


def find_clusters(
    catalog: Catalog,
    pairwise_ruleset: RuleSet,
    cluster_ruleset: ClusterRuleSet,
    schema: Schema | None = None,
    min_cluster_size: int = 2,
    max_clusters: int | None = None,
) -> ClusterAnalysis:
    """
    Find all valid clusters using two-level rule evaluation.

    Phase 1: Build compatibility graph from pairwise rules
    Phase 2: Find all maximal cliques (candidate clusters)
    Phase 3: Validate each clique against cluster rules
    Phase 4: Analyze relationships and statistics

    Args:
        catalog: Items to cluster
        pairwise_ruleset: Rules for item-pair compatibility
        cluster_ruleset: Rules for valid clusters
        schema: Schema for validation
        min_cluster_size: Minimum items per cluster (default 2)
        max_clusters: Limit number of results (None = all)

    Returns:
        ClusterAnalysis with all valid clusters and relationships

    Raises:
        ValueError: If catalog is empty or validation fails
    """
    if len(catalog.items) == 0:
        raise ValueError("Cannot find clusters in empty catalog")

    # PHASE 1: Build compatibility graph from pairwise rules
    matrix = evaluate_matrix(catalog, pairwise_ruleset, schema)
    adjacency = _build_adjacency_from_matrix(matrix)

    # PHASE 2: Find all maximal cliques (candidate clusters)
    candidate_cliques: list[set[str]] = []
    all_item_ids = set(item.id for item in catalog.items)

    _bron_kerbosch(
        R=set(),
        P=all_item_ids.copy(),
        X=set(),
        adjacency=adjacency,
        cliques=candidate_cliques,
    )

    # PHASE 3: Validate each clique against cluster rules
    valid_clusters: list[Cluster] = []

    for clique in candidate_cliques:
        if len(clique) < min_cluster_size:
            continue

        # Get items for this clique
        items_maybe_none = [catalog.get_item(item_id) for item_id in clique]
        items: list[Item] = [item for item in items_maybe_none if item is not None]

        if len(items) < min_cluster_size:
            continue

        # Validate against cluster rules
        is_valid, rule_evals = validate_cluster(items, cluster_ruleset)

        if is_valid:
            cluster = Cluster(
                id=generate_cluster_id(list(clique)),
                item_ids=sorted(clique),
                size=len(clique),
                is_maximal=True,  # All Bron-Kerbosch results are maximal
                is_maximum=False,  # Will be set later
                rule_evaluations=rule_evals,
                metadata={
                    "pairwise_ruleset": pairwise_ruleset.name,
                    "cluster_ruleset": cluster_ruleset.name,
                },
            )
            valid_clusters.append(cluster)

    # PHASE 4: Sort, limit, and analyze
    valid_clusters.sort(key=lambda c: c.size, reverse=True)

    if max_clusters and len(valid_clusters) > max_clusters:
        valid_clusters = valid_clusters[:max_clusters]

    # Mark maximum clusters (largest size)
    if valid_clusters:
        max_size = valid_clusters[0].size
        for cluster in valid_clusters:
            cluster.is_maximum = cluster.size == max_size

    # Find relationships between clusters
    relationships = _find_relationships(valid_clusters)

    # Calculate statistics
    total_clusters = len(valid_clusters)
    max_cluster_size = valid_clusters[0].size if valid_clusters else 0
    min_cluster_size = valid_clusters[-1].size if valid_clusters else 0
    avg_cluster_size = (
        sum(c.size for c in valid_clusters) / total_clusters if total_clusters > 0 else 0.0
    )

    # Count unique items covered by clusters
    items_in_clusters = set()
    for cluster in valid_clusters:
        items_in_clusters.update(cluster.item_ids)
    total_items_covered = len(items_in_clusters)

    return ClusterAnalysis(
        catalog_name=catalog.name,
        ruleset_name=pairwise_ruleset.name,
        cluster_ruleset_name=cluster_ruleset.name,
        schema_name=schema.name if schema else "unknown",
        clusters=valid_clusters,
        relationships=relationships,
        evaluated_at=datetime.now(),
        total_clusters=total_clusters,
        max_cluster_size=max_cluster_size,
        min_cluster_size=min_cluster_size,
        avg_cluster_size=avg_cluster_size,
        total_items_covered=total_items_covered,
    )


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


def _build_adjacency_from_matrix(matrix: EvaluationMatrix) -> dict[str, set[str]]:
    """
    Build an adjacency list representation of the compatibility graph.

    Args:
        matrix: EvaluationMatrix from pairwise evaluation

    Returns:
        Dictionary mapping item_id to set of compatible item_ids
    """
    adjacency: dict[str, set[str]] = {}

    # Initialize with empty sets for all items
    all_items = set()
    for result in matrix.results:
        all_items.add(result.item1_id)
        all_items.add(result.item2_id)

    for item_id in all_items:
        adjacency[item_id] = set()

    # Add edges for compatible pairs
    for result in matrix.results:
        if result.compatible:
            adjacency[result.item1_id].add(result.item2_id)
            adjacency[result.item2_id].add(result.item1_id)

    return adjacency


def _bron_kerbosch(
    R: set[str],
    P: set[str],
    X: set[str],
    adjacency: dict[str, set[str]],
    cliques: list[set[str]],
) -> None:
    """
    Bron-Kerbosch algorithm with pivoting for finding all maximal cliques.

    This is a recursive backtracking algorithm that finds all maximal cliques
    in an undirected graph. A clique is a set of vertices where every two
    distinct vertices are adjacent (fully connected subgraph).

    Args:
        R: Current clique being built
        P: Candidate vertices that could extend R
        X: Vertices already processed (to avoid duplicates)
        adjacency: Adjacency list representation of graph
        cliques: List to accumulate found cliques (modified in place)

    Reference:
        Bron, C.; Kerbosch, J. (1973). "Algorithm 457: finding all cliques of an undirected graph"
    """
    if len(P) == 0 and len(X) == 0:
        # R is a maximal clique
        if len(R) > 0:
            cliques.append(R.copy())
        return

    # Pivoting: choose a vertex u from P ∪ X to minimize branching
    pivot = _choose_pivot(P, X, adjacency)

    # Iterate over vertices in P that are NOT neighbors of pivot
    # (This reduces the number of recursive calls)
    if pivot:
        candidates = P - adjacency.get(pivot, set())
    else:
        candidates = P.copy()

    for v in list(candidates):
        neighbors = adjacency.get(v, set())
        _bron_kerbosch(
            R=R | {v},
            P=P & neighbors,
            X=X & neighbors,
            adjacency=adjacency,
            cliques=cliques,
        )
        P = P - {v}
        X = X | {v}


def _choose_pivot(P: set[str], X: set[str], adjacency: dict[str, set[str]]) -> str | None:
    """
    Choose a pivot vertex to minimize branching in Bron-Kerbosch.

    The pivot should be the vertex in P ∪ X with the most neighbors in P.

    Args:
        P: Candidate vertices
        X: Already processed vertices
        adjacency: Adjacency list

    Returns:
        Vertex ID with most neighbors in P, or None if P ∪ X is empty
    """
    union = P | X
    if not union:
        return None

    # Choose vertex with maximum neighbors in P
    max_neighbors = -1
    pivot = None

    for v in union:
        neighbors_in_p = len(adjacency.get(v, set()) & P)
        if neighbors_in_p > max_neighbors:
            max_neighbors = neighbors_in_p
            pivot = v

    return pivot


def _find_relationships(clusters: list[Cluster]) -> list[ClusterRelationship]:
    """
    Analyze and identify relationships between clusters.

    Finds subset, superset, and overlapping relationships.

    Args:
        clusters: List of clusters to analyze

    Returns:
        List of ClusterRelationship objects
    """
    relationships: list[ClusterRelationship] = []

    for i, cluster1 in enumerate(clusters):
        for cluster2 in clusters[i + 1 :]:
            # Determine relationship type
            set1 = set(cluster1.item_ids)
            set2 = set(cluster2.item_ids)

            if set1 == set2:
                # Identical clusters (shouldn't happen, but handle it)
                continue
            elif set1.issubset(set2):
                # cluster1 is a subset of cluster2
                shared = sorted(set1)
                relationships.append(
                    ClusterRelationship(
                        cluster_id=cluster1.id,
                        related_cluster_id=cluster2.id,
                        relationship_type="subset",
                        shared_items=shared,
                        overlap_size=len(shared),
                    )
                )
                # Also add the inverse (superset) relationship
                relationships.append(
                    ClusterRelationship(
                        cluster_id=cluster2.id,
                        related_cluster_id=cluster1.id,
                        relationship_type="superset",
                        shared_items=shared,
                        overlap_size=len(shared),
                    )
                )
            elif set1.issuperset(set2):
                # cluster1 is a superset of cluster2
                shared = sorted(set2)
                relationships.append(
                    ClusterRelationship(
                        cluster_id=cluster1.id,
                        related_cluster_id=cluster2.id,
                        relationship_type="superset",
                        shared_items=shared,
                        overlap_size=len(shared),
                    )
                )
                # Also add the inverse (subset) relationship
                relationships.append(
                    ClusterRelationship(
                        cluster_id=cluster2.id,
                        related_cluster_id=cluster1.id,
                        relationship_type="subset",
                        shared_items=shared,
                        overlap_size=len(shared),
                    )
                )
            elif set1 & set2:
                # Overlapping (some items in common but neither is subset)
                shared = sorted(set1 & set2)
                relationships.append(
                    ClusterRelationship(
                        cluster_id=cluster1.id,
                        related_cluster_id=cluster2.id,
                        relationship_type="overlapping",
                        shared_items=shared,
                        overlap_size=len(shared),
                    )
                )
                # Overlapping is symmetric, so add inverse too
                relationships.append(
                    ClusterRelationship(
                        cluster_id=cluster2.id,
                        related_cluster_id=cluster1.id,
                        relationship_type="overlapping",
                        shared_items=shared,
                        overlap_size=len(shared),
                    )
                )

    return relationships
