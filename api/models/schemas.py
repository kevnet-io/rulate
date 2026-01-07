"""
Pydantic models for API request/response schemas.

These are distinct from the core rulate models and are used for API serialization.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Schema models
class SchemaCreate(BaseModel):
    """Schema for creating a new Schema."""

    name: str
    version: str
    description: str | None = None
    dimensions: list[dict[str, Any]]


class SchemaUpdate(BaseModel):
    """Schema for updating an existing Schema."""

    version: str | None = None
    description: str | None = None
    dimensions: list[dict[str, Any]] | None = None


class SchemaResponse(BaseModel):
    """Schema for Schema API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    version: str
    description: str | None
    dimensions: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime


# RuleSet models
class RuleSetCreate(BaseModel):
    """Schema for creating a new RuleSet."""

    name: str
    version: str
    description: str | None = None
    schema_name: str  # References schema by name
    rules: list[dict[str, Any]]


class RuleSetUpdate(BaseModel):
    """Schema for updating an existing RuleSet."""

    version: str | None = None
    description: str | None = None
    rules: list[dict[str, Any]] | None = None


class RuleSetResponse(BaseModel):
    """Schema for RuleSet API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    version: str
    description: str | None
    schema_name: str
    rules: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime


# ClusterRuleSet models
class ClusterRuleSetCreate(BaseModel):
    """Schema for creating a new ClusterRuleSet."""

    name: str
    version: str
    description: str | None = None
    schema_name: str  # References schema by name
    pairwise_ruleset_name: str  # References pairwise ruleset by name
    rules: list[dict[str, Any]]


class ClusterRuleSetUpdate(BaseModel):
    """Schema for updating an existing ClusterRuleSet."""

    version: str | None = None
    description: str | None = None
    rules: list[dict[str, Any]] | None = None


class ClusterRuleSetResponse(BaseModel):
    """Schema for ClusterRuleSet API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    version: str
    description: str | None
    schema_name: str
    pairwise_ruleset_name: str
    rules: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime


# Catalog models
class CatalogCreate(BaseModel):
    """Schema for creating a new Catalog."""

    name: str
    description: str | None = None
    schema_name: str  # References schema by name
    metadata: dict[str, Any] | None = None


class CatalogUpdate(BaseModel):
    """Schema for updating an existing Catalog."""

    description: str | None = None
    metadata: dict[str, Any] | None = None


class CatalogResponse(BaseModel):
    """Schema for Catalog API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    schema_name: str
    metadata: dict[str, Any]
    item_count: int
    created_at: datetime
    updated_at: datetime


# Item models
class ItemCreate(BaseModel):
    """Schema for creating a new Item."""

    item_id: str  # User-facing ID
    name: str
    attributes: dict[str, Any]
    metadata: dict[str, Any] | None = None


class ItemUpdate(BaseModel):
    """Schema for updating an existing Item."""

    name: str | None = None
    attributes: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class ItemResponse(BaseModel):
    """Schema for Item API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: str
    name: str
    attributes: dict[str, Any]
    metadata: dict[str, Any]
    catalog_name: str
    created_at: datetime
    updated_at: datetime


# Evaluation models
class EvaluatePairRequest(BaseModel):
    """Request schema for pair evaluation."""

    item1_id: str
    item2_id: str
    catalog_name: str
    ruleset_name: str


class EvaluateMatrixRequest(BaseModel):
    """Request schema for matrix evaluation."""

    catalog_name: str
    ruleset_name: str
    include_self: bool = False


class EvaluateItemRequest(BaseModel):
    """Request schema for evaluating one item against all others."""

    item_id: str
    catalog_name: str
    ruleset_name: str


class EvaluateClustersRequest(BaseModel):
    """Request schema for cluster evaluation."""

    catalog_name: str
    ruleset_name: str
    cluster_ruleset_name: str
    min_cluster_size: int = Field(default=2, ge=2)
    max_clusters: int | None = Field(default=None, ge=1)


# Cluster Builder models
class RuleEvaluationResponse(BaseModel):
    """Response schema for a single rule evaluation."""

    rule_name: str
    passed: bool
    reason: str


class ValidateClusterRequest(BaseModel):
    """Request schema for validating a specific cluster."""

    catalog_name: str
    cluster_ruleset_name: str
    item_ids: list[str]


class ValidateClusterResponse(BaseModel):
    """Response schema for cluster validation."""

    item_ids: list[str]
    is_valid: bool
    rule_evaluations: list[RuleEvaluationResponse]


class CandidateResult(BaseModel):
    """Result for a single candidate item evaluation."""

    item_id: str
    is_pairwise_compatible: bool
    cluster_if_added: ValidateClusterResponse


class EvaluateCandidatesRequest(BaseModel):
    """Request schema for evaluating candidate items for a cluster."""

    catalog_name: str
    pairwise_ruleset_name: str
    cluster_ruleset_name: str
    base_item_ids: list[str] = Field(default_factory=list)
    candidate_item_ids: list[str] | None = None  # None = all other items in catalog


class EvaluateCandidatesResponse(BaseModel):
    """Response schema for candidate evaluation."""

    base_validation: ValidateClusterResponse
    candidates: list[CandidateResult]


# Import/Export models
class ImportRequest(BaseModel):
    """Request schema for importing data."""

    data: dict[str, Any]
    format: str = Field(default="yaml", pattern="^(yaml|json)$")


class BulkImportRequest(BaseModel):
    """Request schema for bulk import."""

    schemas: list[dict[str, Any]] | None = None
    rulesets: list[dict[str, Any]] | None = None
    catalogs: list[dict[str, Any]] | None = None


# Generic response models
class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    detail: str | None = None


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: str | None = None
