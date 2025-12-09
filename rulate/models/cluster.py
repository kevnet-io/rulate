"""
Cluster models for analyzing compatibility sets.

These models support finding and analyzing clusters (sets of mutually compatible items)
and defining cluster-level rules that go beyond pairwise compatibility.
"""

import hashlib
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from rulate.models.evaluation import RuleEvaluation


class ClusterRule(BaseModel):
    """
    Rule for validating a set of items as a cluster.

    Unlike pairwise rules (which compare 2 items), cluster rules
    evaluate an entire set of items together to determine if they
    form a valid cluster.

    Example:
        ClusterRule(
            name="minimum_outfit_size",
            type="requirement",
            condition={"min_cluster_size": 3},
            description="An outfit must have at least 3 items"
        )
    """

    name: str = Field(..., description="Unique name for this rule")
    type: Literal["requirement", "exclusion"] = Field(
        ..., description="Whether this is a requirement or exclusion rule"
    )
    enabled: bool = Field(default=True, description="Whether this rule is active")
    description: str | None = Field(None, description="Human-readable description")
    condition: dict[str, Any] = Field(
        ..., description="Condition tree using cluster-level operators"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ClusterRuleSet(BaseModel):
    """
    Set of rules that define valid clusters.

    Works in conjunction with a pairwise RuleSet:
    1. Pairwise RuleSet determines which items CAN go together (pairwise compatibility)
    2. ClusterRuleSet determines which sets FORM a meaningful cluster (set-level constraints)

    Example:
        ClusterRuleSet(
            name="wardrobe_cluster_rules_v1",
            version="1.0.0",
            schema_ref="wardrobe_schema_v1",
            pairwise_ruleset_ref="wardrobe_rules_v1",
            rules=[...]
        )
    """

    name: str = Field(..., description="Unique name for this cluster ruleset")
    version: str = Field(..., description="Version string (e.g., '1.0.0')")
    schema_ref: str = Field(..., description="Name of the schema these rules apply to")
    pairwise_ruleset_ref: str = Field(
        ..., description="Name of the pairwise RuleSet used for compatibility graph"
    )
    rules: list[ClusterRule] = Field(default_factory=list, description="Cluster-level rules")
    description: str | None = Field(None, description="Human-readable description")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def get_requirement_rules(self) -> list[ClusterRule]:
        """Get all enabled requirement rules."""
        return [rule for rule in self.rules if rule.type == "requirement" and rule.enabled]

    def get_exclusion_rules(self) -> list[ClusterRule]:
        """Get all enabled exclusion rules."""
        return [rule for rule in self.rules if rule.type == "exclusion" and rule.enabled]


class Cluster(BaseModel):
    """
    A set of items that are mutually compatible and satisfy cluster rules.

    Represents a maximal clique in the compatibility graph that also
    passes all cluster-level validation rules.

    Example:
        Cluster(
            id="a1b2c3d4e5f6",
            item_ids=["shirt_001", "pants_002", "jacket_005"],
            size=3,
            is_maximal=True,
            is_maximum=False
        )
    """

    id: str = Field(..., description="Unique cluster ID (hash of sorted item IDs)")
    item_ids: list[str] = Field(..., description="Sorted list of item IDs in this cluster")
    size: int = Field(..., description="Number of items in cluster")
    is_maximal: bool = Field(
        ..., description="Whether this cluster cannot be extended with more items"
    )
    is_maximum: bool = Field(..., description="Whether this is one of the largest clusters")
    rule_evaluations: list[RuleEvaluation] = Field(
        default_factory=list, description="Results of cluster rule evaluations"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def contains_item(self, item_id: str) -> bool:
        """Check if this cluster contains a specific item."""
        return item_id in self.item_ids

    def is_subset_of(self, other: "Cluster") -> bool:
        """Check if this cluster is a subset of another cluster."""
        return set(self.item_ids).issubset(set(other.item_ids))

    def is_superset_of(self, other: "Cluster") -> bool:
        """Check if this cluster is a superset of another cluster."""
        return set(self.item_ids).issuperset(set(other.item_ids))

    def overlaps_with(self, other: "Cluster") -> bool:
        """Check if this cluster shares any items with another cluster."""
        return bool(set(self.item_ids) & set(other.item_ids))

    def get_overlap_items(self, other: "Cluster") -> list[str]:
        """Get items shared with another cluster."""
        return sorted(set(self.item_ids) & set(other.item_ids))


class ClusterRelationship(BaseModel):
    """
    Relationship between two clusters.

    Captures subset/superset/overlapping patterns to enable
    navigation and understanding of cluster hierarchies.

    Example:
        ClusterRelationship(
            cluster_id="abc123",
            related_cluster_id="def456",
            relationship_type="subset",
            shared_items=["shirt_001", "pants_002"],
            overlap_size=2
        )
    """

    cluster_id: str = Field(..., description="ID of the first cluster")
    related_cluster_id: str = Field(..., description="ID of the related cluster")
    relationship_type: Literal["subset", "superset", "overlapping"] = Field(
        ..., description="Type of relationship"
    )
    shared_items: list[str] = Field(
        default_factory=list, description="Items shared between clusters"
    )
    overlap_size: int = Field(..., description="Number of shared items")


class ClusterAnalysis(BaseModel):
    """
    Complete analysis of clusters found in a catalog.

    Contains all valid clusters, their relationships, and summary statistics.

    Example:
        ClusterAnalysis(
            catalog_name="wardrobe",
            ruleset_name="wardrobe_rules_v1",
            cluster_ruleset_name="wardrobe_cluster_rules_v1",
            clusters=[...],
            relationships=[...],
            total_clusters=8,
            max_cluster_size=5
        )
    """

    catalog_name: str = Field(..., description="Name of the catalog analyzed")
    ruleset_name: str = Field(..., description="Name of the pairwise ruleset used")
    cluster_ruleset_name: str = Field(..., description="Name of the cluster ruleset used")
    schema_name: str = Field(..., description="Name of the schema")
    clusters: list[Cluster] = Field(
        default_factory=list, description="All valid clusters (sorted by size descending)"
    )
    relationships: list[ClusterRelationship] = Field(
        default_factory=list, description="Relationships between clusters"
    )
    evaluated_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp of analysis"
    )

    # Summary statistics
    total_clusters: int = Field(0, description="Total number of clusters found")
    max_cluster_size: int = Field(0, description="Size of largest cluster")
    min_cluster_size: int = Field(0, description="Size of smallest cluster")
    avg_cluster_size: float = Field(0.0, description="Average cluster size")
    total_items_covered: int = Field(
        0, description="Number of unique items in at least one cluster"
    )

    def get_cluster_by_id(self, cluster_id: str) -> Cluster | None:
        """Get a cluster by its ID."""
        for cluster in self.clusters:
            if cluster.id == cluster_id:
                return cluster
        return None

    def get_clusters_containing_item(self, item_id: str) -> list[Cluster]:
        """Get all clusters that contain a specific item."""
        return [cluster for cluster in self.clusters if cluster.contains_item(item_id)]

    def get_maximum_clusters(self) -> list[Cluster]:
        """Get all clusters marked as maximum (largest size)."""
        return [cluster for cluster in self.clusters if cluster.is_maximum]

    def get_relationships_for_cluster(self, cluster_id: str) -> list[ClusterRelationship]:
        """Get all relationships involving a specific cluster."""
        return [
            rel
            for rel in self.relationships
            if rel.cluster_id == cluster_id or rel.related_cluster_id == cluster_id
        ]

    def get_summary_stats(self) -> dict[str, Any]:
        """Get summary statistics about the analysis."""
        return {
            "total_clusters": self.total_clusters,
            "max_cluster_size": self.max_cluster_size,
            "min_cluster_size": self.min_cluster_size,
            "avg_cluster_size": self.avg_cluster_size,
            "total_items_covered": self.total_items_covered,
            "maximum_clusters": len(self.get_maximum_clusters()),
        }


def generate_cluster_id(item_ids: list[str]) -> str:
    """
    Generate a deterministic ID from a list of item IDs.

    Args:
        item_ids: List of item IDs (will be sorted internally)

    Returns:
        12-character hex string (MD5 hash of sorted, comma-joined IDs)
    """
    sorted_ids = sorted(item_ids)
    content = ",".join(sorted_ids)
    return hashlib.md5(content.encode()).hexdigest()[:12]
