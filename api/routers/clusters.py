"""
API endpoints for cluster evaluation and ClusterRuleSet management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import CatalogDB, ClusterRuleSetDB, RuleSetDB, SchemaDB
from api.models.schemas import (
    CandidateResult,
    ClusterRuleSetCreate,
    ClusterRuleSetResponse,
    ClusterRuleSetUpdate,
    EvaluateCandidatesRequest,
    EvaluateCandidatesResponse,
    MessageResponse,
    RuleEvaluationResponse,
    ValidateClusterRequest,
    ValidateClusterResponse,
)
from rulate.engine.cluster_evaluator import validate_cluster
from rulate.engine.evaluator import evaluate_pair
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


@router.post("/evaluate/cluster/validate", response_model=ValidateClusterResponse)
def validate_cluster_endpoint(
    request: ValidateClusterRequest, db: Session = Depends(get_db)
) -> ValidateClusterResponse:
    """
    Validate a specific set of items against pairwise and cluster rules.

    This endpoint performs comprehensive cluster validation:
    1. Checks that all pairs of items are pairwise compatible
    2. Validates the cluster against cluster-level rules

    A cluster is only valid if BOTH conditions are met.

    Args:
        request: Validation request with catalog, rulesets, and item IDs
        db: Database session

    Returns:
        ValidateClusterResponse with validation result and rule evaluations
    """
    # Find catalog
    db_catalog = db.query(CatalogDB).filter(CatalogDB.name == request.catalog_name).first()
    if not db_catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog '{request.catalog_name}' not found",
        )

    # Find pairwise ruleset
    db_pairwise_ruleset = (
        db.query(RuleSetDB).filter(RuleSetDB.name == request.pairwise_ruleset_name).first()
    )
    if not db_pairwise_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RuleSet '{request.pairwise_ruleset_name}' not found",
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
    pairwise_ruleset = db_to_rulate_ruleset(db_pairwise_ruleset)
    cluster_ruleset = db_to_rulate_cluster_ruleset(db_cluster_ruleset)
    catalog = db_to_rulate_catalog(db_catalog)

    # Get items from catalog
    items: list[Item] = []
    missing_ids: list[str] = []
    for item_id in request.item_ids:
        item = catalog.get_item(item_id)
        if item:
            items.append(item)
        else:
            missing_ids.append(item_id)

    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Items not found in catalog: {missing_ids}",
        )

    # Check pairwise compatibility for all pairs
    pairwise_incompatible_pairs: list[tuple[str, str]] = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            result = evaluate_pair(items[i], items[j], pairwise_ruleset, schema)
            if not result.compatible:
                pairwise_incompatible_pairs.append((items[i].id, items[j].id))

    # If any pairs are incompatible, cluster is invalid
    if pairwise_incompatible_pairs:
        pair_descriptions = [f"({p[0]}, {p[1]})" for p in pairwise_incompatible_pairs]
        return ValidateClusterResponse(
            item_ids=request.item_ids,
            is_valid=False,
            rule_evaluations=[
                RuleEvaluationResponse(
                    rule_name="pairwise_compatibility",
                    passed=False,
                    reason=f"Incompatible pairs found: {', '.join(pair_descriptions)}",
                )
            ],
        )

    # Validate cluster-level rules
    cluster_is_valid, cluster_rule_evals = validate_cluster(items, cluster_ruleset)

    # Add pairwise compatibility as a passing rule evaluation
    all_rule_evals = [
        RuleEvaluationResponse(
            rule_name="pairwise_compatibility",
            passed=True,
            reason="All pairs are pairwise compatible",
        )
    ] + [
        RuleEvaluationResponse(
            rule_name=r.rule_name,
            passed=r.passed,
            reason=r.reason,
        )
        for r in cluster_rule_evals
    ]

    return ValidateClusterResponse(
        item_ids=request.item_ids,
        is_valid=cluster_is_valid,
        rule_evaluations=all_rule_evals,
    )


@router.post("/evaluate/cluster/candidates", response_model=EvaluateCandidatesResponse)
def evaluate_candidates_endpoint(
    request: EvaluateCandidatesRequest, db: Session = Depends(get_db)
) -> EvaluateCandidatesResponse:
    """
    Evaluate candidate items for adding to a cluster.

    For each candidate, determines:
    1. Whether it's pairwise compatible with all items in the base cluster
    2. Whether the cluster would be valid if this candidate is added

    Args:
        request: Request with catalog, rulesets, base items, and optional candidates
        db: Database session

    Returns:
        EvaluateCandidatesResponse with base validation and candidate results
    """
    # Find catalog
    db_catalog = db.query(CatalogDB).filter(CatalogDB.name == request.catalog_name).first()
    if not db_catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog '{request.catalog_name}' not found",
        )

    # Find pairwise ruleset
    db_pairwise_ruleset = (
        db.query(RuleSetDB).filter(RuleSetDB.name == request.pairwise_ruleset_name).first()
    )
    if not db_pairwise_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RuleSet '{request.pairwise_ruleset_name}' not found",
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
    pairwise_ruleset = db_to_rulate_ruleset(db_pairwise_ruleset)
    cluster_ruleset = db_to_rulate_cluster_ruleset(db_cluster_ruleset)
    catalog = db_to_rulate_catalog(db_catalog)

    # Get base items
    base_items: list[Item] = []
    for item_id in request.base_item_ids:
        item = catalog.get_item(item_id)
        if item:
            base_items.append(item)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Base item '{item_id}' not found in catalog",
            )

    # Validate base cluster
    if base_items:
        base_is_valid, base_rule_evals = validate_cluster(base_items, cluster_ruleset)
    else:
        # Empty cluster - technically invalid for most rulesets
        base_is_valid = False
        base_rule_evals = []

    base_validation = ValidateClusterResponse(
        item_ids=request.base_item_ids,
        is_valid=base_is_valid,
        rule_evaluations=[
            RuleEvaluationResponse(
                rule_name=r.rule_name,
                passed=r.passed,
                reason=r.reason,
            )
            for r in base_rule_evals
        ],
    )

    # Determine candidates
    if request.candidate_item_ids is not None:
        candidate_ids = request.candidate_item_ids
    else:
        # All items not in base cluster
        base_id_set = set(request.base_item_ids)
        candidate_ids = [item.id for item in catalog.items if item.id not in base_id_set]

    # Evaluate each candidate
    candidates: list[CandidateResult] = []
    for candidate_id in candidate_ids:
        candidate_item = catalog.get_item(candidate_id)
        if not candidate_item:
            # Skip missing candidates (could also raise error)
            continue

        # Check pairwise compatibility with all base items
        is_pairwise_compatible = True
        for base_item in base_items:
            result = evaluate_pair(base_item, candidate_item, pairwise_ruleset, schema)
            if not result.compatible:
                is_pairwise_compatible = False
                break

        # Validate cluster with candidate added
        cluster_items = base_items + [candidate_item]
        cluster_is_valid, cluster_rule_evals = validate_cluster(cluster_items, cluster_ruleset)

        candidates.append(
            CandidateResult(
                item_id=candidate_id,
                is_pairwise_compatible=is_pairwise_compatible,
                cluster_if_added=ValidateClusterResponse(
                    item_ids=request.base_item_ids + [candidate_id],
                    is_valid=cluster_is_valid,
                    rule_evaluations=[
                        RuleEvaluationResponse(
                            rule_name=r.rule_name,
                            passed=r.passed,
                            reason=r.reason,
                        )
                        for r in cluster_rule_evals
                    ],
                ),
            )
        )

    return EvaluateCandidatesResponse(
        base_validation=base_validation,
        candidates=candidates,
    )


# ClusterRuleSet CRUD endpoints


@router.post(
    "/cluster-rulesets", response_model=ClusterRuleSetResponse, status_code=status.HTTP_201_CREATED
)
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
    pairwise_ruleset = (
        db.query(RuleSetDB).filter(RuleSetDB.name == ruleset_data.pairwise_ruleset_name).first()
    )
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


@router.get("/cluster-rulesets", response_model=list[ClusterRuleSetResponse])
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
    cluster_ruleset = (
        db.query(ClusterRuleSetDB).filter(ClusterRuleSetDB.name == cluster_ruleset_name).first()
    )
    if not cluster_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ClusterRuleSet '{cluster_ruleset_name}' not found",
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
    cluster_ruleset_name: str, ruleset_data: ClusterRuleSetUpdate, db: Session = Depends(get_db)
):
    """Update a cluster ruleset."""
    cluster_ruleset = (
        db.query(ClusterRuleSetDB).filter(ClusterRuleSetDB.name == cluster_ruleset_name).first()
    )
    if not cluster_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ClusterRuleSet '{cluster_ruleset_name}' not found",
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
    cluster_ruleset = (
        db.query(ClusterRuleSetDB).filter(ClusterRuleSetDB.name == cluster_ruleset_name).first()
    )
    if not cluster_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ClusterRuleSet '{cluster_ruleset_name}' not found",
        )

    db.delete(cluster_ruleset)
    db.commit()

    return MessageResponse(
        message="ClusterRuleSet deleted successfully",
        detail=f"ClusterRuleSet '{cluster_ruleset_name}' has been deleted",
    )
