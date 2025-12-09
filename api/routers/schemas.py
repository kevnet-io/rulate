"""
API endpoints for Schema management.
"""


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import SchemaDB
from api.models.schemas import MessageResponse, SchemaCreate, SchemaResponse, SchemaUpdate
from rulate.models.schema import Schema as RulateSchema

router = APIRouter()


@router.post("/schemas", response_model=SchemaResponse, status_code=status.HTTP_201_CREATED)
def create_schema(schema_data: SchemaCreate, db: Session = Depends(get_db)):
    """
    Create a new schema.

    Args:
        schema_data: Schema data
        db: Database session

    Returns:
        Created schema

    Raises:
        HTTPException: If schema with name already exists or validation fails
    """
    # Check if schema with this name already exists
    existing = db.query(SchemaDB).filter(SchemaDB.name == schema_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Schema with name '{schema_data.name}' already exists",
        )

    # Validate using Rulate Schema model
    try:
        rulate_schema = RulateSchema(
            name=schema_data.name,
            version=schema_data.version,
            description=schema_data.description,
            dimensions=[
                {**dim} for dim in schema_data.dimensions
            ],  # Convert to dict if needed
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Schema validation failed: {str(e)}",
        )

    # Create database record
    db_schema = SchemaDB(
        name=schema_data.name,
        version=schema_data.version,
        description=schema_data.description,
        dimensions_json=rulate_schema.model_dump_json(include={"dimensions"})[
            15:-1
        ],  # Extract just the dimensions JSON
    )
    db_schema.set_dimensions(schema_data.dimensions)  # Use the setter method

    db.add(db_schema)
    db.commit()
    db.refresh(db_schema)

    return SchemaResponse(
        id=db_schema.id,
        name=db_schema.name,
        version=db_schema.version,
        description=db_schema.description,
        dimensions=db_schema.get_dimensions(),
        created_at=db_schema.created_at,
        updated_at=db_schema.updated_at,
    )


@router.get("/schemas", response_model=list[SchemaResponse])
def list_schemas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all schemas.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of schemas
    """
    schemas = db.query(SchemaDB).offset(skip).limit(limit).all()
    return [
        SchemaResponse(
            id=s.id,
            name=s.name,
            version=s.version,
            description=s.description,
            dimensions=s.get_dimensions(),
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in schemas
    ]


@router.get("/schemas/{schema_name}", response_model=SchemaResponse)
def get_schema(schema_name: str, db: Session = Depends(get_db)):
    """
    Get a schema by name.

    Args:
        schema_name: Name of the schema
        db: Database session

    Returns:
        Schema details

    Raises:
        HTTPException: If schema not found
    """
    schema = db.query(SchemaDB).filter(SchemaDB.name == schema_name).first()
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Schema '{schema_name}' not found"
        )

    return SchemaResponse(
        id=schema.id,
        name=schema.name,
        version=schema.version,
        description=schema.description,
        dimensions=schema.get_dimensions(),
        created_at=schema.created_at,
        updated_at=schema.updated_at,
    )


@router.put("/schemas/{schema_name}", response_model=SchemaResponse)
def update_schema(schema_name: str, schema_data: SchemaUpdate, db: Session = Depends(get_db)):
    """
    Update a schema.

    Args:
        schema_name: Name of the schema to update
        schema_data: Updated schema data
        db: Database session

    Returns:
        Updated schema

    Raises:
        HTTPException: If schema not found or validation fails
    """
    schema = db.query(SchemaDB).filter(SchemaDB.name == schema_name).first()
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Schema '{schema_name}' not found"
        )

    # Update fields
    if schema_data.version is not None:
        schema.version = schema_data.version
    if schema_data.description is not None:
        schema.description = schema_data.description
    if schema_data.dimensions is not None:
        # Validate dimensions
        try:
            RulateSchema(
                name=schema.name,
                version=schema.version,
                dimensions=schema_data.dimensions,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Schema validation failed: {str(e)}",
            )
        schema.set_dimensions(schema_data.dimensions)

    db.commit()
    db.refresh(schema)

    return SchemaResponse(
        id=schema.id,
        name=schema.name,
        version=schema.version,
        description=schema.description,
        dimensions=schema.get_dimensions(),
        created_at=schema.created_at,
        updated_at=schema.updated_at,
    )


@router.delete("/schemas/{schema_name}", response_model=MessageResponse)
def delete_schema(schema_name: str, db: Session = Depends(get_db)):
    """
    Delete a schema.

    Args:
        schema_name: Name of the schema to delete
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If schema not found
    """
    schema = db.query(SchemaDB).filter(SchemaDB.name == schema_name).first()
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Schema '{schema_name}' not found"
        )

    db.delete(schema)
    db.commit()

    return MessageResponse(message=f"Schema '{schema_name}' deleted successfully")
