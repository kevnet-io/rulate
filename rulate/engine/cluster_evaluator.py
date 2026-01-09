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
    max_cluster_size: int | None = None,
    max_clusters: int | None = None,
) -> ClusterAnalysis:
    """
    Find all valid clusters using integrated two-level rule evaluation.

    This algorithm uses a modified Bron-Kerbosch approach that validates cluster
    rules DURING recursion rather than after. This provides:
    - Early pruning of invalid branches
    - Efficient discovery of all valid clusters
    - No false negatives from maximal-only validation

    Phase 1: Build compatibility graph from pairwise rules
    Phase 2: Find maximal cliques with integrated cluster validation
    Phase 3: Analyze relationships and statistics

    Args:
        catalog: Items to cluster
        pairwise_ruleset: Rules for item-pair compatibility
        cluster_ruleset: Rules for valid clusters (domain rules only)
        schema: Schema for validation
        min_cluster_size: Minimum items per cluster (default 2)
        max_cluster_size: Maximum items per cluster (None = unlimited)
        max_clusters: Limit number of results (None = all)

    Returns:
        ClusterAnalysis with all valid clusters and relationships

    Raises:
        ValueError: If catalog is empty or validation fails

    Note:
        Size constraints (min/max_cluster_size) are search parameters, not rules.
        cluster_ruleset should contain only domain-specific rules like
        formality_consistency, season_consistency, etc.
    """
    if len(catalog.items) == 0:
        raise ValueError("Cannot find clusters in empty catalog")

    # PHASE 1: Build compatibility graph from pairwise rules
    matrix = evaluate_matrix(catalog, pairwise_ruleset, schema)
    adjacency = _build_adjacency_from_matrix(matrix)

    # PHASE 2: Find maximal cliques with integrated cluster validation
    all_item_ids = set(item.id for item in catalog.items)
    seen_clusters: set[frozenset[str]] = set()
    found_clusters: list[set[str]] = []
    validation_count = [0]  # Mutable counter for tracking

    _bron_kerbosch_with_cluster_rules(
        R=set(),
        P=all_item_ids.copy(),
        X=set(),
        adjacency=adjacency,
        cluster_ruleset=cluster_ruleset,
        catalog=catalog,
        min_size=min_cluster_size,
        max_size=max_cluster_size,
        max_clusters=max_clusters,
        seen_clusters=seen_clusters,
        found_clusters=found_clusters,
        validation_count=validation_count,
    )

    # Convert to Cluster objects
    valid_clusters: list[Cluster] = []
    for clique in found_clusters:
        # Get items for this clique
        items_maybe_none = [catalog.get_item(item_id) for item_id in clique]
        items: list[Item] = [item for item in items_maybe_none if item is not None]

        if len(items) < min_cluster_size:
            continue

        # Get rule evaluations (already validated during search)
        _, rule_evals = validate_cluster(items, cluster_ruleset)

        cluster = Cluster(
            id=generate_cluster_id(list(clique)),
            item_ids=sorted(clique),
            size=len(clique),
            is_maximal=True,  # All results are maximal within cluster rules
            is_maximum=False,  # Will be set later
            rule_evaluations=rule_evals,
            metadata={
                "pairwise_ruleset": pairwise_ruleset.name,
                "cluster_ruleset": cluster_ruleset.name,
                "validations": validation_count[0],
            },
        )
        valid_clusters.append(cluster)

    # PHASE 3: Sort and analyze
    valid_clusters.sort(key=lambda c: c.size, reverse=True)

    # Mark maximum clusters (largest size)
    if valid_clusters:
        max_size = valid_clusters[0].size
        for cluster in valid_clusters:
            cluster.is_maximum = cluster.size == max_size

    # Find relationships between clusters
    relationships = _find_relationships(valid_clusters)

    # Calculate statistics
    total_clusters = len(valid_clusters)
    max_cluster_size_found = valid_clusters[0].size if valid_clusters else 0
    min_cluster_size_found = valid_clusters[-1].size if valid_clusters else 0
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
        max_cluster_size=max_cluster_size_found,
        min_cluster_size=min_cluster_size_found,
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


def _bron_kerbosch_with_cluster_rules(
    R: set[str],
    P: set[str],
    X: set[str],
    adjacency: dict[str, set[str]],
    cluster_ruleset: ClusterRuleSet,
    catalog: Catalog,
    min_size: int,
    max_size: int | None,
    max_clusters: int | None,
    seen_clusters: set[frozenset[str]],
    found_clusters: list[set[str]],
    validation_count: list[int],
) -> bool:
    """
    Modified Bron-Kerbosch that validates cluster rules during recursion.

    This integrated approach prunes invalid branches early and ensures we find
    ALL valid clusters, not just those that happen to be maximal in the pairwise
    compatibility graph.

    Key differences from standard Bron-Kerbosch:
    1. Validates cluster rules when R >= min_size (early pruning)
    2. Deduplicates using seen_clusters set
    3. Supports early stopping via max_clusters limit
    4. Returns bool to signal whether search should continue

    Args:
        R: Current clique being built
        P: Candidate vertices that could extend R
        X: Vertices already processed (to avoid duplicates)
        adjacency: Adjacency list representation of graph
        cluster_ruleset: Rules to validate clusters against
        catalog: Catalog containing items
        min_size: Minimum cluster size to validate
        max_size: Maximum cluster size (None = unlimited)
        max_clusters: Maximum results to find (None = all)
        seen_clusters: Set of frozensets for deduplication
        found_clusters: List to accumulate found clusters
        validation_count: Mutable counter for tracking validations

    Returns:
        True if search should continue, False if max_clusters reached

    Reference:
        Based on Bron-Kerbosch algorithm with integrated constraint validation
    """
    # Check if we've hit the cluster limit
    if max_clusters and len(found_clusters) >= max_clusters:
        return False

    # Base case: R is maximal when no more vertices can be added
    if len(P) == 0 and len(X) == 0:
        if len(R) >= min_size:
            cluster_key = frozenset(R)
            if cluster_key not in seen_clusters:
                seen_clusters.add(cluster_key)
                found_clusters.append(R.copy())
        return len(found_clusters) < max_clusters if max_clusters else True

    # Check max size constraint
    if max_size is not None and len(R) >= max_size:
        if len(R) >= min_size:
            # Final validation at max size
            items = [item for item in catalog.items if item.id in R]
            is_valid, _ = validate_cluster(items, cluster_ruleset)
            validation_count[0] += 1

            if is_valid:
                cluster_key = frozenset(R)
                if cluster_key not in seen_clusters:
                    seen_clusters.add(cluster_key)
                    found_clusters.append(R.copy())
        return len(found_clusters) < max_clusters if max_clusters else True

    # Pivoting: choose a vertex u from P ∪ X to minimize branching
    pivot = _choose_pivot(P, X, adjacency)

    # Iterate over vertices in P that are NOT neighbors of pivot
    if pivot:
        candidates = P - adjacency.get(pivot, set())
    else:
        candidates = P.copy()

    for v in list(candidates):
        new_R = R | {v}

        # Check if we've already seen this cluster
        cluster_key = frozenset(new_R)
        if cluster_key in seen_clusters:
            P = P - {v}
            X = X | {v}
            continue

        # CLUSTER RULE VALIDATION: Only validate if R is large enough
        should_recurse = True
        if len(new_R) >= min_size:
            # Now we can validate against cluster rules
            items = [item for item in catalog.items if item.id in new_R]
            is_valid, _ = validate_cluster(items, cluster_ruleset)
            validation_count[0] += 1
            should_recurse = is_valid
        # else: R too small to validate, allow recursion to continue

        if should_recurse:
            neighbors = adjacency.get(v, set())
            should_continue = _bron_kerbosch_with_cluster_rules(
                R=new_R,
                P=P & neighbors,
                X=X & neighbors,
                adjacency=adjacency,
                cluster_ruleset=cluster_ruleset,
                catalog=catalog,
                min_size=min_size,
                max_size=max_size,
                max_clusters=max_clusters,
                seen_clusters=seen_clusters,
                found_clusters=found_clusters,
                validation_count=validation_count,
            )
            if not should_continue:
                return False

        P = P - {v}
        X = X | {v}

    return True


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
