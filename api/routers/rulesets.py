"""
API endpoints for RuleSet management.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import RuleSetDB, SchemaDB
from api.models.schemas import MessageResponse, RuleSetCreate, RuleSetResponse, RuleSetUpdate

router = APIRouter()


@router.post("/rulesets", response_model=RuleSetResponse, status_code=status.HTTP_201_CREATED)
def create_ruleset(ruleset_data: RuleSetCreate, db: Session = Depends(get_db)):
    """Create a new ruleset."""
    # Check if ruleset with this name already exists
    existing = db.query(RuleSetDB).filter(RuleSetDB.name == ruleset_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"RuleSet '{ruleset_data.name}' already exists",
        )

    # Find schema
    schema = db.query(SchemaDB).filter(SchemaDB.name == ruleset_data.schema_name).first()
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema '{ruleset_data.schema_name}' not found",
        )

    # Create database record
    db_ruleset = RuleSetDB(
        name=ruleset_data.name,
        version=ruleset_data.version,
        description=ruleset_data.description,
        schema_id=schema.id,
    )
    db_ruleset.set_rules(ruleset_data.rules)

    db.add(db_ruleset)
    db.commit()
    db.refresh(db_ruleset)

    return RuleSetResponse(
        id=db_ruleset.id,
        name=db_ruleset.name,
        version=db_ruleset.version,
        description=db_ruleset.description,
        schema_name=schema.name,
        rules=db_ruleset.get_rules(),
        created_at=db_ruleset.created_at,
        updated_at=db_ruleset.updated_at,
    )


@router.get("/rulesets", response_model=List[RuleSetResponse])
def list_rulesets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all rulesets."""
    rulesets = db.query(RuleSetDB).offset(skip).limit(limit).all()
    return [
        RuleSetResponse(
            id=r.id,
            name=r.name,
            version=r.version,
            description=r.description,
            schema_name=r.schema.name,
            rules=r.rules,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rulesets
    ]


@router.get("/rulesets/{ruleset_name}", response_model=RuleSetResponse)
def get_ruleset(ruleset_name: str, db: Session = Depends(get_db)):
    """Get a ruleset by name."""
    ruleset = db.query(RuleSetDB).filter(RuleSetDB.name == ruleset_name).first()
    if not ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"RuleSet '{ruleset_name}' not found"
        )

    return RuleSetResponse(
        id=ruleset.id,
        name=ruleset.name,
        version=ruleset.version,
        description=ruleset.description,
        schema_name=ruleset.schema.name,
        rules=ruleset.get_rules(),
        created_at=ruleset.created_at,
        updated_at=ruleset.updated_at,
    )


@router.put("/rulesets/{ruleset_name}", response_model=RuleSetResponse)
def update_ruleset(
    ruleset_name: str, ruleset_data: RuleSetUpdate, db: Session = Depends(get_db)
):
    """Update a ruleset."""
    ruleset = db.query(RuleSetDB).filter(RuleSetDB.name == ruleset_name).first()
    if not ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"RuleSet '{ruleset_name}' not found"
        )

    if ruleset_data.version is not None:
        ruleset.version = ruleset_data.version
    if ruleset_data.description is not None:
        ruleset.description = ruleset_data.description
    if ruleset_data.rules is not None:
        ruleset.set_rules(ruleset_data.rules)

    db.commit()
    db.refresh(ruleset)

    return RuleSetResponse(
        id=ruleset.id,
        name=ruleset.name,
        version=ruleset.version,
        description=ruleset.description,
        schema_name=ruleset.schema.name,
        rules=ruleset.get_rules(),
        created_at=ruleset.created_at,
        updated_at=ruleset.updated_at,
    )


@router.delete("/rulesets/{ruleset_name}", response_model=MessageResponse)
def delete_ruleset(ruleset_name: str, db: Session = Depends(get_db)):
    """Delete a ruleset."""
    ruleset = db.query(RuleSetDB).filter(RuleSetDB.name == ruleset_name).first()
    if not ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"RuleSet '{ruleset_name}' not found"
        )

    db.delete(ruleset)
    db.commit()

    return MessageResponse(message=f"RuleSet '{ruleset_name}' deleted successfully")
