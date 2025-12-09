"""
API endpoints for import/export operations.

Provides bulk import and export functionality for all data types:
- Schemas
- RuleSets
- ClusterRuleSets
- Catalogs (with items)
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import CatalogDB, ClusterRuleSetDB, ItemDB, RuleSetDB, SchemaDB
from api.models.schemas import (
    MessageResponse,
)
from rulate.models.schema import Schema as RulateSchema

router = APIRouter()


# Export Endpoints


@router.get("/export/schemas")
def export_all_schemas(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Export all schemas in JSON format.

    Returns:
        JSON array of all schemas with their dimensions
    """
    schemas = db.query(SchemaDB).all()
    export_data = [
        {
            "name": s.name,
            "version": s.version,
            "description": s.description,
            "dimensions": s.get_dimensions(),
        }
        for s in schemas
    ]
    return JSONResponse(content=export_data)


@router.get("/export/schemas/{schema_name}")
def export_schema(schema_name: str, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Export a specific schema in JSON format.

    Args:
        schema_name: Name of the schema to export
        db: Database session

    Returns:
        JSON object with schema data

    Raises:
        HTTPException: If schema not found
    """
    schema = db.query(SchemaDB).filter(SchemaDB.name == schema_name).first()
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Schema '{schema_name}' not found"
        )

    export_data = {
        "name": schema.name,
        "version": schema.version,
        "description": schema.description,
        "dimensions": schema.get_dimensions(),
    }
    return JSONResponse(content=export_data)


@router.get("/export/rulesets")
def export_all_rulesets(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Export all rulesets in JSON format.

    Returns:
        JSON array of all rulesets with their rules
    """
    rulesets = db.query(RuleSetDB).all()
    export_data = [
        {
            "name": r.name,
            "version": r.version,
            "description": r.description,
            "schema_ref": r.schema.name,
            "rules": r.get_rules(),
        }
        for r in rulesets
    ]
    return JSONResponse(content=export_data)


@router.get("/export/rulesets/{ruleset_name}")
def export_ruleset(ruleset_name: str, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Export a specific ruleset in JSON format.

    Args:
        ruleset_name: Name of the ruleset to export
        db: Database session

    Returns:
        JSON object with ruleset data

    Raises:
        HTTPException: If ruleset not found
    """
    ruleset = db.query(RuleSetDB).filter(RuleSetDB.name == ruleset_name).first()
    if not ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"RuleSet '{ruleset_name}' not found"
        )

    export_data = {
        "name": ruleset.name,
        "version": ruleset.version,
        "description": ruleset.description,
        "schema_ref": ruleset.schema.name,
        "rules": ruleset.get_rules(),
    }
    return JSONResponse(content=export_data)


@router.get("/export/cluster-rulesets")
def export_all_cluster_rulesets(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Export all cluster rulesets in JSON format.

    Returns:
        JSON array of all cluster rulesets with their rules
    """
    cluster_rulesets = db.query(ClusterRuleSetDB).all()
    export_data = [
        {
            "name": cr.name,
            "version": cr.version,
            "description": cr.description,
            "schema_ref": cr.schema.name,
            "pairwise_ruleset_ref": cr.pairwise_ruleset.name,
            "rules": cr.get_rules(),
        }
        for cr in cluster_rulesets
    ]
    return JSONResponse(content=export_data)


@router.get("/export/cluster-rulesets/{cluster_ruleset_name}")
def export_cluster_ruleset(
    cluster_ruleset_name: str, db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Export a specific cluster ruleset in JSON format.

    Args:
        cluster_ruleset_name: Name of the cluster ruleset to export
        db: Database session

    Returns:
        JSON object with cluster ruleset data

    Raises:
        HTTPException: If cluster ruleset not found
    """
    cluster_ruleset = (
        db.query(ClusterRuleSetDB).filter(ClusterRuleSetDB.name == cluster_ruleset_name).first()
    )
    if not cluster_ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ClusterRuleSet '{cluster_ruleset_name}' not found",
        )

    export_data = {
        "name": cluster_ruleset.name,
        "version": cluster_ruleset.version,
        "description": cluster_ruleset.description,
        "schema_ref": cluster_ruleset.schema.name,
        "pairwise_ruleset_ref": cluster_ruleset.pairwise_ruleset.name,
        "rules": cluster_ruleset.get_rules(),
    }
    return JSONResponse(content=export_data)


@router.get("/export/catalogs/{catalog_name}")
def export_catalog(catalog_name: str, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Export a specific catalog with all its items in JSON format.

    Args:
        catalog_name: Name of the catalog to export
        db: Database session

    Returns:
        JSON object with catalog and items data

    Raises:
        HTTPException: If catalog not found
    """
    catalog = db.query(CatalogDB).filter(CatalogDB.name == catalog_name).first()
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Catalog '{catalog_name}' not found"
        )

    export_data = {
        "name": catalog.name,
        "description": catalog.description,
        "schema_ref": catalog.schema.name,
        "metadata": catalog.get_metadata(),
        "items": [
            {
                "id": item.item_id,
                "name": item.name,
                "attributes": item.get_attributes(),
                "metadata": item.get_metadata(),
            }
            for item in catalog.items
        ],
    }
    return JSONResponse(content=export_data)


@router.get("/export/catalogs")
def export_all_catalogs(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Export all catalogs with their items in JSON format.

    Returns:
        JSON array of all catalogs with their items
    """
    catalogs = db.query(CatalogDB).all()
    export_data = [
        {
            "name": c.name,
            "description": c.description,
            "schema_ref": c.schema.name,
            "metadata": c.get_metadata(),
            "items": [
                {
                    "id": item.item_id,
                    "name": item.name,
                    "attributes": item.get_attributes(),
                    "metadata": item.get_metadata(),
                }
                for item in c.items
            ],
        }
        for c in catalogs
    ]
    return JSONResponse(content=export_data)


@router.get("/export/all")
def export_all(db: Session = Depends(get_db)) -> JSONResponse:
    """
    Export all data (schemas, rulesets, cluster rulesets, and catalogs) in JSON format.

    Returns:
        JSON object with all data organized by type
    """
    schemas = db.query(SchemaDB).all()
    rulesets = db.query(RuleSetDB).all()
    cluster_rulesets = db.query(ClusterRuleSetDB).all()
    catalogs = db.query(CatalogDB).all()

    export_data = {
        "schemas": [
            {
                "name": s.name,
                "version": s.version,
                "description": s.description,
                "dimensions": s.get_dimensions(),
            }
            for s in schemas
        ],
        "rulesets": [
            {
                "name": r.name,
                "version": r.version,
                "description": r.description,
                "schema_ref": r.schema.name,
                "rules": r.get_rules(),
            }
            for r in rulesets
        ],
        "cluster_rulesets": [
            {
                "name": cr.name,
                "version": cr.version,
                "description": cr.description,
                "schema_ref": cr.schema.name,
                "pairwise_ruleset_ref": cr.pairwise_ruleset.name,
                "rules": cr.get_rules(),
            }
            for cr in cluster_rulesets
        ],
        "catalogs": [
            {
                "name": c.name,
                "description": c.description,
                "schema_ref": c.schema.name,
                "metadata": c.get_metadata(),
                "items": [
                    {
                        "id": item.item_id,
                        "name": item.name,
                        "attributes": item.get_attributes(),
                        "metadata": item.get_metadata(),
                    }
                    for item in c.items
                ],
            }
            for c in catalogs
        ],
    }
    return JSONResponse(content=export_data)


# Import Endpoints


@router.post("/import/schemas", response_model=MessageResponse)
def import_schemas(
    schemas: list[dict[str, Any]], skip_existing: bool = False, db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Import multiple schemas.

    Args:
        schemas: List of schema objects to import
        skip_existing: If True, skip schemas that already exist instead of erroring
        db: Database session

    Returns:
        Success message with count of imported schemas

    Raises:
        HTTPException: If validation fails or schema already exists (when skip_existing=False)
    """
    imported = 0
    skipped = 0
    errors = []

    for schema_data in schemas:
        try:
            # Check if schema already exists
            existing = db.query(SchemaDB).filter(SchemaDB.name == schema_data["name"]).first()
            if existing:
                if skip_existing:
                    skipped += 1
                    continue
                else:
                    errors.append(f"Schema '{schema_data['name']}' already exists")
                    continue

            # Validate using Rulate Schema model
            try:
                _ = RulateSchema(**schema_data)  # Validation only
            except Exception as e:
                errors.append(f"Schema '{schema_data.get('name', 'unknown')}' validation failed: {str(e)}")
                continue

            # Create database record
            db_schema = SchemaDB(
                name=schema_data["name"],
                version=schema_data["version"],
                description=schema_data.get("description"),
            )
            db_schema.set_dimensions(schema_data["dimensions"])

            db.add(db_schema)
            imported += 1

        except Exception as e:
            errors.append(f"Error importing schema '{schema_data.get('name', 'unknown')}': {str(e)}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to commit schemas: {str(e)}",
        )

    message = f"Imported {imported} schema(s)"
    if skipped:
        message += f", skipped {skipped}"
    if errors:
        message += f". Errors: {'; '.join(errors)}"

    return MessageResponse(message=message, detail=None if not errors else "; ".join(errors))


@router.post("/import/rulesets", response_model=MessageResponse)
def import_rulesets(
    rulesets: list[dict[str, Any]], skip_existing: bool = False, db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Import multiple rulesets.

    Args:
        rulesets: List of ruleset objects to import
        skip_existing: If True, skip rulesets that already exist instead of erroring
        db: Database session

    Returns:
        Success message with count of imported rulesets

    Raises:
        HTTPException: If validation fails or ruleset already exists (when skip_existing=False)
    """
    imported = 0
    skipped = 0
    errors = []

    for ruleset_data in rulesets:
        try:
            # Check if ruleset already exists
            existing = db.query(RuleSetDB).filter(RuleSetDB.name == ruleset_data["name"]).first()
            if existing:
                if skip_existing:
                    skipped += 1
                    continue
                else:
                    errors.append(f"RuleSet '{ruleset_data['name']}' already exists")
                    continue

            # Find schema
            schema_ref = ruleset_data.get("schema_ref") or ruleset_data.get("schema_name")
            schema = db.query(SchemaDB).filter(SchemaDB.name == schema_ref).first()
            if not schema:
                errors.append(f"Schema '{schema_ref}' not found for ruleset '{ruleset_data['name']}'")
                continue

            # Create database record
            db_ruleset = RuleSetDB(
                name=ruleset_data["name"],
                version=ruleset_data["version"],
                description=ruleset_data.get("description"),
                schema_id=schema.id,
            )
            db_ruleset.set_rules(ruleset_data["rules"])

            db.add(db_ruleset)
            imported += 1

        except Exception as e:
            errors.append(f"Error importing ruleset '{ruleset_data.get('name', 'unknown')}': {str(e)}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to commit rulesets: {str(e)}",
        )

    message = f"Imported {imported} ruleset(s)"
    if skipped:
        message += f", skipped {skipped}"
    if errors:
        message += f". Errors: {'; '.join(errors)}"

    return MessageResponse(message=message, detail=None if not errors else "; ".join(errors))


@router.post("/import/cluster-rulesets", response_model=MessageResponse)
def import_cluster_rulesets(
    cluster_rulesets: list[dict[str, Any]],
    skip_existing: bool = False,
    db: Session = Depends(get_db),
) -> MessageResponse:
    """
    Import multiple cluster rulesets.

    Args:
        cluster_rulesets: List of cluster ruleset objects to import
        skip_existing: If True, skip cluster rulesets that already exist instead of erroring
        db: Database session

    Returns:
        Success message with count of imported cluster rulesets

    Raises:
        HTTPException: If validation fails or cluster ruleset already exists (when skip_existing=False)
    """
    imported = 0
    skipped = 0
    errors = []

    for cr_data in cluster_rulesets:
        try:
            # Check if cluster ruleset already exists
            existing = (
                db.query(ClusterRuleSetDB).filter(ClusterRuleSetDB.name == cr_data["name"]).first()
            )
            if existing:
                if skip_existing:
                    skipped += 1
                    continue
                else:
                    errors.append(f"ClusterRuleSet '{cr_data['name']}' already exists")
                    continue

            # Find schema
            schema_ref = cr_data.get("schema_ref") or cr_data.get("schema_name")
            schema = db.query(SchemaDB).filter(SchemaDB.name == schema_ref).first()
            if not schema:
                errors.append(f"Schema '{schema_ref}' not found for cluster ruleset '{cr_data['name']}'")
                continue

            # Find pairwise ruleset
            pairwise_ref = cr_data.get("pairwise_ruleset_ref") or cr_data.get(
                "pairwise_ruleset_name"
            )
            pairwise_ruleset = db.query(RuleSetDB).filter(RuleSetDB.name == pairwise_ref).first()
            if not pairwise_ruleset:
                errors.append(
                    f"Pairwise ruleset '{pairwise_ref}' not found for cluster ruleset '{cr_data['name']}'"
                )
                continue

            # Create database record
            db_cluster_ruleset = ClusterRuleSetDB(
                name=cr_data["name"],
                version=cr_data["version"],
                description=cr_data.get("description"),
                schema_id=schema.id,
                pairwise_ruleset_id=pairwise_ruleset.id,
            )
            db_cluster_ruleset.set_rules(cr_data["rules"])

            db.add(db_cluster_ruleset)
            imported += 1

        except Exception as e:
            errors.append(
                f"Error importing cluster ruleset '{cr_data.get('name', 'unknown')}': {str(e)}"
            )

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to commit cluster rulesets: {str(e)}",
        )

    message = f"Imported {imported} cluster ruleset(s)"
    if skipped:
        message += f", skipped {skipped}"
    if errors:
        message += f". Errors: {'; '.join(errors)}"

    return MessageResponse(message=message, detail=None if not errors else "; ".join(errors))


@router.post("/import/catalogs", response_model=MessageResponse)
def import_catalogs(
    catalogs: list[dict[str, Any]], skip_existing: bool = False, db: Session = Depends(get_db)
) -> MessageResponse:
    """
    Import multiple catalogs with their items.

    Args:
        catalogs: List of catalog objects to import (including items)
        skip_existing: If True, skip catalogs that already exist instead of erroring
        db: Database session

    Returns:
        Success message with count of imported catalogs and items

    Raises:
        HTTPException: If validation fails or catalog already exists (when skip_existing=False)
    """
    imported_catalogs = 0
    imported_items = 0
    skipped = 0
    errors = []

    for catalog_data in catalogs:
        try:
            # Check if catalog already exists
            existing = db.query(CatalogDB).filter(CatalogDB.name == catalog_data["name"]).first()
            if existing:
                if skip_existing:
                    skipped += 1
                    continue
                else:
                    errors.append(f"Catalog '{catalog_data['name']}' already exists")
                    continue

            # Find schema
            schema_ref = catalog_data.get("schema_ref") or catalog_data.get("schema_name")
            schema = db.query(SchemaDB).filter(SchemaDB.name == schema_ref).first()
            if not schema:
                errors.append(f"Schema '{schema_ref}' not found for catalog '{catalog_data['name']}'")
                continue

            # Create catalog
            db_catalog = CatalogDB(
                name=catalog_data["name"],
                description=catalog_data.get("description"),
                schema_id=schema.id,
            )
            if catalog_data.get("metadata"):
                db_catalog.set_metadata(catalog_data["metadata"])

            db.add(db_catalog)
            db.flush()  # Flush to get catalog ID

            # Import items
            items_data = catalog_data.get("items", [])
            for item_data in items_data:
                try:
                    db_item = ItemDB(
                        item_id=item_data["id"],
                        name=item_data["name"],
                        catalog_id=db_catalog.id,
                    )
                    db_item.set_attributes(item_data["attributes"])
                    if item_data.get("metadata"):
                        db_item.set_metadata(item_data["metadata"])

                    db.add(db_item)
                    imported_items += 1

                except Exception as e:
                    errors.append(
                        f"Error importing item '{item_data.get('id', 'unknown')}' in catalog '{catalog_data['name']}': {str(e)}"
                    )

            imported_catalogs += 1

        except Exception as e:
            errors.append(f"Error importing catalog '{catalog_data.get('name', 'unknown')}': {str(e)}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to commit catalogs: {str(e)}",
        )

    message = f"Imported {imported_catalogs} catalog(s) with {imported_items} item(s)"
    if skipped:
        message += f", skipped {skipped}"
    if errors:
        message += f". Errors: {'; '.join(errors)}"

    return MessageResponse(message=message, detail=None if not errors else "; ".join(errors))


@router.post("/import/all", response_model=MessageResponse)
def import_all(data: dict[str, Any], skip_existing: bool = False, db: Session = Depends(get_db)) -> MessageResponse:
    """
    Import all data types from a single JSON object.

    Expected format:
    {
        "schemas": [...],
        "rulesets": [...],
        "cluster_rulesets": [...],
        "catalogs": [...]
    }

    Args:
        data: Dictionary containing all data types
        skip_existing: If True, skip items that already exist instead of erroring
        db: Database session

    Returns:
        Success message with counts of imported items

    Raises:
        HTTPException: If validation fails
    """
    results = []

    # Import in dependency order: schemas -> rulesets -> cluster_rulesets -> catalogs
    if "schemas" in data and data["schemas"]:
        result = import_schemas(data["schemas"], skip_existing=skip_existing, db=db)
        results.append(f"Schemas: {result.message}")

    if "rulesets" in data and data["rulesets"]:
        result = import_rulesets(data["rulesets"], skip_existing=skip_existing, db=db)
        results.append(f"RuleSets: {result.message}")

    if "cluster_rulesets" in data and data["cluster_rulesets"]:
        result = import_cluster_rulesets(data["cluster_rulesets"], skip_existing=skip_existing, db=db)
        results.append(f"ClusterRuleSets: {result.message}")

    if "catalogs" in data and data["catalogs"]:
        result = import_catalogs(data["catalogs"], skip_existing=skip_existing, db=db)
        results.append(f"Catalogs: {result.message}")

    return MessageResponse(message=" | ".join(results) if results else "No data imported")
