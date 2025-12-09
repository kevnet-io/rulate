"""
API endpoints for evaluation.
"""


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import CatalogDB, ItemDB, RuleSetDB, SchemaDB
from api.models.schemas import EvaluateItemRequest, EvaluateMatrixRequest, EvaluatePairRequest
from rulate.engine import evaluate_item_against_catalog, evaluate_matrix, evaluate_pair
from rulate.models.catalog import Catalog, Item
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


@router.post("/evaluate/pair")
def evaluate_pair_endpoint(request: EvaluatePairRequest, db: Session = Depends(get_db)):
    """
    Evaluate compatibility between two items.

    Args:
        request: Evaluation request with item IDs, catalog, and ruleset
        db: Database session

    Returns:
        ComparisonResult with compatibility decision
    """
    # Find catalog
    db_catalog = db.query(CatalogDB).filter(CatalogDB.name == request.catalog_name).first()
    if not db_catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog '{request.catalog_name}' not found",
        )

    # Find ruleset
    db_ruleset = db.query(RuleSetDB).filter(RuleSetDB.name == request.ruleset_name).first()
    if not db_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RuleSet '{request.ruleset_name}' not found",
        )

    # Find items
    item1_db = (
        db.query(ItemDB)
        .filter(ItemDB.catalog_id == db_catalog.id, ItemDB.item_id == request.item1_id)
        .first()
    )
    item2_db = (
        db.query(ItemDB)
        .filter(ItemDB.catalog_id == db_catalog.id, ItemDB.item_id == request.item2_id)
        .first()
    )

    if not item1_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item '{request.item1_id}' not found"
        )
    if not item2_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item '{request.item2_id}' not found"
        )

    # Convert to Rulate models
    schema = db_to_rulate_schema(db_catalog.schema)
    ruleset = db_to_rulate_ruleset(db_ruleset)
    item1 = Item(
        id=item1_db.item_id,
        name=item1_db.name,
        attributes=item1_db.get_attributes(),
        metadata=item1_db.get_metadata(),
    )
    item2 = Item(
        id=item2_db.item_id,
        name=item2_db.name,
        attributes=item2_db.get_attributes(),
        metadata=item2_db.get_metadata(),
    )

    # Evaluate
    result = evaluate_pair(item1, item2, ruleset, schema)

    # Return as dict
    return result.model_dump(mode="python")


@router.post("/evaluate/matrix")
def evaluate_matrix_endpoint(request: EvaluateMatrixRequest, db: Session = Depends(get_db)):
    """
    Evaluate all pairwise combinations in a catalog.

    Args:
        request: Evaluation request with catalog and ruleset
        db: Database session

    Returns:
        EvaluationMatrix with all pairwise comparisons
    """
    # Find catalog
    db_catalog = db.query(CatalogDB).filter(CatalogDB.name == request.catalog_name).first()
    if not db_catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog '{request.catalog_name}' not found",
        )

    # Find ruleset
    db_ruleset = db.query(RuleSetDB).filter(RuleSetDB.name == request.ruleset_name).first()
    if not db_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RuleSet '{request.ruleset_name}' not found",
        )

    # Convert to Rulate models
    schema = db_to_rulate_schema(db_catalog.schema)
    ruleset = db_to_rulate_ruleset(db_ruleset)
    catalog = db_to_rulate_catalog(db_catalog)

    # Evaluate
    matrix = evaluate_matrix(catalog, ruleset, schema, include_self=request.include_self)

    # Return as dict with summary stats
    result = matrix.model_dump(mode="python")
    result["total_comparisons"] = len(matrix.results)
    result["compatible_count"] = len(matrix.get_compatible_pairs())
    result["compatibility_rate"] = (
        result["compatible_count"] / result["total_comparisons"]
        if result["total_comparisons"] > 0
        else 0.0
    )
    return result


@router.post("/evaluate/item")
def evaluate_item_endpoint(request: EvaluateItemRequest, db: Session = Depends(get_db)):
    """
    Evaluate a single item against all other items in catalog.

    Args:
        request: Evaluation request with item ID, catalog, and ruleset
        db: Database session

    Returns:
        List of ComparisonResults
    """
    # Find catalog
    db_catalog = db.query(CatalogDB).filter(CatalogDB.name == request.catalog_name).first()
    if not db_catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog '{request.catalog_name}' not found",
        )

    # Find ruleset
    db_ruleset = db.query(RuleSetDB).filter(RuleSetDB.name == request.ruleset_name).first()
    if not db_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RuleSet '{request.ruleset_name}' not found",
        )

    # Find item
    item_db = (
        db.query(ItemDB)
        .filter(ItemDB.catalog_id == db_catalog.id, ItemDB.item_id == request.item_id)
        .first()
    )
    if not item_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item '{request.item_id}' not found"
        )

    # Convert to Rulate models
    schema = db_to_rulate_schema(db_catalog.schema)
    ruleset = db_to_rulate_ruleset(db_ruleset)
    catalog = db_to_rulate_catalog(db_catalog)
    item = Item(
        id=item_db.item_id,
        name=item_db.name,
        attributes=item_db.get_attributes(),
        metadata=item_db.get_metadata(),
    )

    # Evaluate
    results = evaluate_item_against_catalog(item, catalog, ruleset, schema)

    # Return as list of dicts
    return [r.model_dump(mode="python") for r in results]
