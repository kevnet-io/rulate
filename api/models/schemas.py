"""
Pydantic models for API request/response schemas.

These are distinct from the core rulate models and are used for API serialization.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Schema models
class SchemaCreate(BaseModel):
    """Schema for creating a new Schema."""

    name: str
    version: str
    description: Optional[str] = None
    dimensions: List[Dict[str, Any]]


class SchemaUpdate(BaseModel):
    """Schema for updating an existing Schema."""

    version: Optional[str] = None
    description: Optional[str] = None
    dimensions: Optional[List[Dict[str, Any]]] = None


class SchemaResponse(BaseModel):
    """Schema for Schema API responses."""

    id: int
    name: str
    version: str
    description: Optional[str]
    dimensions: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# RuleSet models
class RuleSetCreate(BaseModel):
    """Schema for creating a new RuleSet."""

    name: str
    version: str
    description: Optional[str] = None
    schema_name: str  # References schema by name
    rules: List[Dict[str, Any]]


class RuleSetUpdate(BaseModel):
    """Schema for updating an existing RuleSet."""

    version: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[List[Dict[str, Any]]] = None


class RuleSetResponse(BaseModel):
    """Schema for RuleSet API responses."""

    id: int
    name: str
    version: str
    description: Optional[str]
    schema_name: str
    rules: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Catalog models
class CatalogCreate(BaseModel):
    """Schema for creating a new Catalog."""

    name: str
    description: Optional[str] = None
    schema_name: str  # References schema by name
    metadata: Optional[Dict[str, Any]] = None


class CatalogUpdate(BaseModel):
    """Schema for updating an existing Catalog."""

    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CatalogResponse(BaseModel):
    """Schema for Catalog API responses."""

    id: int
    name: str
    description: Optional[str]
    schema_name: str
    metadata: Dict[str, Any]
    item_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Item models
class ItemCreate(BaseModel):
    """Schema for creating a new Item."""

    item_id: str  # User-facing ID
    name: str
    attributes: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class ItemUpdate(BaseModel):
    """Schema for updating an existing Item."""

    name: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ItemResponse(BaseModel):
    """Schema for Item API responses."""

    id: int
    item_id: str
    name: str
    attributes: Dict[str, Any]
    metadata: Dict[str, Any]
    catalog_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


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


# Import/Export models
class ImportRequest(BaseModel):
    """Request schema for importing data."""

    data: Dict[str, Any]
    format: str = Field(default="yaml", pattern="^(yaml|json)$")


class BulkImportRequest(BaseModel):
    """Request schema for bulk import."""

    schemas: Optional[List[Dict[str, Any]]] = None
    rulesets: Optional[List[Dict[str, Any]]] = None
    catalogs: Optional[List[Dict[str, Any]]] = None


# Generic response models
class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: Optional[str] = None
