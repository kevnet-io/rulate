"""
API endpoints for cluster evaluation and ClusterRuleSet management.
"""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import CatalogDB, ClusterRuleSetDB, RuleSetDB, SchemaDB
from api.models.schemas import (
    ClusterRuleSetCreate,
    ClusterRuleSetResponse,
    ClusterRuleSetUpdate,
    EvaluateClustersRequest,
    MessageResponse,
)
from rulate.engine.cluster_evaluator import find_clusters
from rulate.models.catalog import Catalog, Item
from rulate.models.cluster import ClusterRuleSet
from rulate.models.rule import RuleSet
from rulate.models.schema import Schema

router = APIRouter()


def db_to_rulate_schema(db_schema: SchemaDB) -> Schema:
    """Convert database schema to Rulate Schema model."""
    return Schema(
        name=db_schema.name,
        version=db_schema.version,
        description=db_schema.description,
        dimensions=db_schema.get_dimensions(),
    )


def db_to_rulate_ruleset(db_ruleset: RuleSetDB) -> RuleSet:
    """Convert database ruleset to Rulate RuleSet model."""
    return RuleSet(
        name=db_ruleset.name,
        version=db_ruleset.version,
        description=db_ruleset.description,
        schema_ref=db_ruleset.schema.name,
        rules=db_ruleset.get_rules(),
    )


def db_to_rulate_cluster_ruleset(db_cluster_ruleset: ClusterRuleSetDB) -> ClusterRuleSet:
    """Convert database cluster ruleset to Rulate ClusterRuleSet model."""
    return ClusterRuleSet(
        name=db_cluster_ruleset.name,
        version=db_cluster_ruleset.version,
        description=db_cluster_ruleset.description,
        schema_ref=db_cluster_ruleset.schema.name,
        pairwise_ruleset_ref=db_cluster_ruleset.pairwise_ruleset.name,
        rules=db_cluster_ruleset.get_rules(),
    )


def db_to_rulate_catalog(db_catalog: CatalogDB) -> Catalog:
    """Convert database catalog to Rulate Catalog model."""
    items = [
        Item(
            id=item.item_id,
            name=item.name,
            attributes=item.get_attributes(),
            metadata=item.get_metadata(),
        )
        for item in db_catalog.items
    ]

    return Catalog(
        name=db_catalog.name,
        schema_ref=db_catalog.schema.name,
        description=db_catalog.description,
        items=items,
        metadata=db_catalog.get_metadata(),
        created_at=db_catalog.created_at,
        updated_at=db_catalog.updated_at,
    )


@router.post("/evaluate/clusters")
def evaluate_clusters_endpoint(
    request: EvaluateClustersRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Find all compatibility clusters in a catalog.

    Args:
        request: Evaluation request with catalog, rulesets, and parameters
        db: Database session

    Returns:
        ClusterAnalysis with all clusters and relationships
    """
    # Find catalog
    db_catalog = db.query(CatalogDB).filter(CatalogDB.name == request.catalog_name).first()
    if not db_catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog '{request.catalog_name}' not found",
        )

    # Find pairwise ruleset
    db_ruleset = db.query(RuleSetDB).filter(RuleSetDB.name == request.ruleset_name).first()
    if not db_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RuleSet '{request.ruleset_name}' not found",
        )

    # Find cluster ruleset
    db_cluster_ruleset = (
        db.query(ClusterRuleSetDB)
        .filter(ClusterRuleSetDB.name == request.cluster_ruleset_name)
        .first()
    )
    if not db_cluster_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ClusterRuleSet '{request.cluster_ruleset_name}' not found",
        )

    # Convert to Rulate models
    schema = db_to_rulate_schema(db_catalog.schema)
    ruleset = db_to_rulate_ruleset(db_ruleset)
    cluster_ruleset = db_to_rulate_cluster_ruleset(db_cluster_ruleset)
    catalog = db_to_rulate_catalog(db_catalog)

    # Find clusters
    analysis = find_clusters(
        catalog,
        ruleset,
        cluster_ruleset,
        schema,
        min_cluster_size=request.min_cluster_size,
        max_clusters=request.max_clusters,
    )

    # Return as dict with additional metadata
    result = analysis.model_dump(mode="python")
    return result


# ClusterRuleSet CRUD endpoints


@router.post("/cluster-rulesets", response_model=ClusterRuleSetResponse, status_code=status.HTTP_201_CREATED)
def create_cluster_ruleset(ruleset_data: ClusterRuleSetCreate, db: Session = Depends(get_db)):
    """Create a new cluster ruleset."""
    # Check if cluster ruleset with this name already exists
    existing = db.query(ClusterRuleSetDB).filter(ClusterRuleSetDB.name == ruleset_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"ClusterRuleSet '{ruleset_data.name}' already exists",
        )

    # Find schema
    schema = db.query(SchemaDB).filter(SchemaDB.name == ruleset_data.schema_name).first()
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema '{ruleset_data.schema_name}' not found",
        )

    # Find pairwise ruleset
    pairwise_ruleset = db.query(RuleSetDB).filter(RuleSetDB.name == ruleset_data.pairwise_ruleset_name).first()
    if not pairwise_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pairwise RuleSet '{ruleset_data.pairwise_ruleset_name}' not found",
        )

    # Create database record
    db_cluster_ruleset = ClusterRuleSetDB(
        name=ruleset_data.name,
        version=ruleset_data.version,
        description=ruleset_data.description,
        schema_id=schema.id,
        pairwise_ruleset_id=pairwise_ruleset.id,
    )
    db_cluster_ruleset.set_rules(ruleset_data.rules)

    db.add(db_cluster_ruleset)
    db.commit()
    db.refresh(db_cluster_ruleset)

    return ClusterRuleSetResponse(
        id=db_cluster_ruleset.id,
        name=db_cluster_ruleset.name,
        version=db_cluster_ruleset.version,
        description=db_cluster_ruleset.description,
        schema_name=schema.name,
        pairwise_ruleset_name=pairwise_ruleset.name,
        rules=db_cluster_ruleset.get_rules(),
        created_at=db_cluster_ruleset.created_at,
        updated_at=db_cluster_ruleset.updated_at,
    )


@router.get("/cluster-rulesets", response_model=List[ClusterRuleSetResponse])
def list_cluster_rulesets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all cluster rulesets."""
    cluster_rulesets = db.query(ClusterRuleSetDB).offset(skip).limit(limit).all()
    return [
        ClusterRuleSetResponse(
            id=cr.id,
            name=cr.name,
            version=cr.version,
            description=cr.description,
            schema_name=cr.schema.name,
            pairwise_ruleset_name=cr.pairwise_ruleset.name,
            rules=cr.get_rules(),
            created_at=cr.created_at,
            updated_at=cr.updated_at,
        )
        for cr in cluster_rulesets
    ]


@router.get("/cluster-rulesets/{cluster_ruleset_name}", response_model=ClusterRuleSetResponse)
def get_cluster_ruleset(cluster_ruleset_name: str, db: Session = Depends(get_db)):
    """Get a cluster ruleset by name."""
    cluster_ruleset = db.query(ClusterRuleSetDB).filter(ClusterRuleSetDB.name == cluster_ruleset_name).first()
    if not cluster_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ClusterRuleSet '{cluster_ruleset_name}' not found"
        )

    return ClusterRuleSetResponse(
        id=cluster_ruleset.id,
        name=cluster_ruleset.name,
        version=cluster_ruleset.version,
        description=cluster_ruleset.description,
        schema_name=cluster_ruleset.schema.name,
        pairwise_ruleset_name=cluster_ruleset.pairwise_ruleset.name,
        rules=cluster_ruleset.get_rules(),
        created_at=cluster_ruleset.created_at,
        updated_at=cluster_ruleset.updated_at,
    )


@router.put("/cluster-rulesets/{cluster_ruleset_name}", response_model=ClusterRuleSetResponse)
def update_cluster_ruleset(
    cluster_ruleset_name: str,
    ruleset_data: ClusterRuleSetUpdate,
    db: Session = Depends(get_db)
):
    """Update a cluster ruleset."""
    cluster_ruleset = db.query(ClusterRuleSetDB).filter(ClusterRuleSetDB.name == cluster_ruleset_name).first()
    if not cluster_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ClusterRuleSet '{cluster_ruleset_name}' not found"
        )

    # Update fields if provided
    if ruleset_data.version is not None:
        cluster_ruleset.version = ruleset_data.version
    if ruleset_data.description is not None:
        cluster_ruleset.description = ruleset_data.description
    if ruleset_data.rules is not None:
        cluster_ruleset.set_rules(ruleset_data.rules)

    db.commit()
    db.refresh(cluster_ruleset)

    return ClusterRuleSetResponse(
        id=cluster_ruleset.id,
        name=cluster_ruleset.name,
        version=cluster_ruleset.version,
        description=cluster_ruleset.description,
        schema_name=cluster_ruleset.schema.name,
        pairwise_ruleset_name=cluster_ruleset.pairwise_ruleset.name,
        rules=cluster_ruleset.get_rules(),
        created_at=cluster_ruleset.created_at,
        updated_at=cluster_ruleset.updated_at,
    )


@router.delete("/cluster-rulesets/{cluster_ruleset_name}", response_model=MessageResponse)
def delete_cluster_ruleset(cluster_ruleset_name: str, db: Session = Depends(get_db)):
    """Delete a cluster ruleset."""
    cluster_ruleset = db.query(ClusterRuleSetDB).filter(ClusterRuleSetDB.name == cluster_ruleset_name).first()
    if not cluster_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ClusterRuleSet '{cluster_ruleset_name}' not found"
        )

    db.delete(cluster_ruleset)
    db.commit()

    return MessageResponse(
        message="ClusterRuleSet deleted successfully",
        detail=f"ClusterRuleSet '{cluster_ruleset_name}' has been deleted"
    )
