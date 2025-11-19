"""
API endpoints for Catalog and Item management.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database.connection import get_db
from api.database.models import CatalogDB, ItemDB, SchemaDB
from api.models.schemas import (
    CatalogCreate,
    CatalogResponse,
    CatalogUpdate,
    ItemCreate,
    ItemResponse,
    ItemUpdate,
    MessageResponse,
)

router = APIRouter()


# Catalog endpoints


@router.post("/catalogs", response_model=CatalogResponse, status_code=status.HTTP_201_CREATED)
def create_catalog(catalog_data: CatalogCreate, db: Session = Depends(get_db)):
    """Create a new catalog."""
    # Check if catalog already exists
    existing = db.query(CatalogDB).filter(CatalogDB.name == catalog_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Catalog '{catalog_data.name}' already exists",
        )

    # Find schema
    schema = db.query(SchemaDB).filter(SchemaDB.name == catalog_data.schema_name).first()
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema '{catalog_data.schema_name}' not found",
        )

    # Create database record
    db_catalog = CatalogDB(
        name=catalog_data.name,
        description=catalog_data.description,
        schema_id=schema.id,
    )
    if catalog_data.metadata:
        db_catalog.set_metadata(catalog_data.metadata)

    db.add(db_catalog)
    db.commit()
    db.refresh(db_catalog)

    return CatalogResponse(
        id=db_catalog.id,
        name=db_catalog.name,
        description=db_catalog.description,
        schema_name=schema.name,
        metadata=db_catalog.get_metadata(),
        item_count=len(db_catalog.items),
        created_at=db_catalog.created_at,
        updated_at=db_catalog.updated_at,
    )


@router.get("/catalogs", response_model=List[CatalogResponse])
def list_catalogs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all catalogs."""
    catalogs = db.query(CatalogDB).offset(skip).limit(limit).all()
    return [
        CatalogResponse(
            id=c.id,
            name=c.name,
            description=c.description,
            schema_name=c.schema.name,
            metadata=c.get_metadata(),
            item_count=len(c.items),
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in catalogs
    ]


@router.get("/catalogs/{catalog_name}", response_model=CatalogResponse)
def get_catalog(catalog_name: str, db: Session = Depends(get_db)):
    """Get a catalog by name."""
    catalog = db.query(CatalogDB).filter(CatalogDB.name == catalog_name).first()
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Catalog '{catalog_name}' not found"
        )

    return CatalogResponse(
        id=catalog.id,
        name=catalog.name,
        description=catalog.description,
        schema_name=catalog.schema.name,
        metadata=catalog.get_metadata(),
        item_count=len(catalog.items),
        created_at=catalog.created_at,
        updated_at=catalog.updated_at,
    )


@router.delete("/catalogs/{catalog_name}", response_model=MessageResponse)
def delete_catalog(catalog_name: str, db: Session = Depends(get_db)):
    """Delete a catalog."""
    catalog = db.query(CatalogDB).filter(CatalogDB.name == catalog_name).first()
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Catalog '{catalog_name}' not found"
        )

    db.delete(catalog)
    db.commit()

    return MessageResponse(message=f"Catalog '{catalog_name}' deleted successfully")


# Item endpoints


@router.post(
    "/catalogs/{catalog_name}/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_item(catalog_name: str, item_data: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item in a catalog."""
    # Find catalog
    catalog = db.query(CatalogDB).filter(CatalogDB.name == catalog_name).first()
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Catalog '{catalog_name}' not found"
        )

    # Check if item with this ID already exists in catalog
    existing = (
        db.query(ItemDB)
        .filter(ItemDB.catalog_id == catalog.id, ItemDB.item_id == item_data.item_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Item '{item_data.item_id}' already exists in catalog",
        )

    # Create database record
    db_item = ItemDB(
        item_id=item_data.item_id,
        name=item_data.name,
        catalog_id=catalog.id,
    )
    db_item.set_attributes(item_data.attributes)
    if item_data.metadata:
        db_item.set_metadata(item_data.metadata)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return ItemResponse(
        id=db_item.id,
        item_id=db_item.item_id,
        name=db_item.name,
        attributes=db_item.get_attributes(),
        metadata=db_item.get_metadata(),
        catalog_name=catalog.name,
        created_at=db_item.created_at,
        updated_at=db_item.updated_at,
    )


@router.get("/catalogs/{catalog_name}/items", response_model=List[ItemResponse])
def list_items(
    catalog_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """List all items in a catalog."""
    catalog = db.query(CatalogDB).filter(CatalogDB.name == catalog_name).first()
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Catalog '{catalog_name}' not found"
        )

    items = (
        db.query(ItemDB).filter(ItemDB.catalog_id == catalog.id).offset(skip).limit(limit).all()
    )

    return [
        ItemResponse(
            id=item.id,
            item_id=item.item_id,
            name=item.name,
            attributes=item.get_attributes(),
            metadata=item.get_metadata(),
            catalog_name=catalog.name,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in items
    ]


@router.get("/catalogs/{catalog_name}/items/{item_id}", response_model=ItemResponse)
def get_item(catalog_name: str, item_id: str, db: Session = Depends(get_db)):
    """Get an item by ID."""
    catalog = db.query(CatalogDB).filter(CatalogDB.name == catalog_name).first()
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Catalog '{catalog_name}' not found"
        )

    item = (
        db.query(ItemDB)
        .filter(ItemDB.catalog_id == catalog.id, ItemDB.item_id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item '{item_id}' not found"
        )

    return ItemResponse(
        id=item.id,
        item_id=item.item_id,
        name=item.name,
        attributes=item.get_attributes(),
        metadata=item.get_metadata(),
        catalog_name=catalog.name,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.put("/catalogs/{catalog_name}/items/{item_id}", response_model=ItemResponse)
def update_item(
    catalog_name: str, item_id: str, item_data: ItemUpdate, db: Session = Depends(get_db)
):
    """Update an item."""
    catalog = db.query(CatalogDB).filter(CatalogDB.name == catalog_name).first()
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Catalog '{catalog_name}' not found"
        )

    item = (
        db.query(ItemDB)
        .filter(ItemDB.catalog_id == catalog.id, ItemDB.item_id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item '{item_id}' not found"
        )

    if item_data.name is not None:
        item.name = item_data.name
    if item_data.attributes is not None:
        item.set_attributes(item_data.attributes)
    if item_data.metadata is not None:
        item.set_metadata(item_data.metadata)

    db.commit()
    db.refresh(item)

    return ItemResponse(
        id=item.id,
        item_id=item.item_id,
        name=item.name,
        attributes=item.get_attributes(),
        metadata=item.get_metadata(),
        catalog_name=catalog.name,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.delete("/catalogs/{catalog_name}/items/{item_id}", response_model=MessageResponse)
def delete_item(catalog_name: str, item_id: str, db: Session = Depends(get_db)):
    """Delete an item."""
    catalog = db.query(CatalogDB).filter(CatalogDB.name == catalog_name).first()
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Catalog '{catalog_name}' not found"
        )

    item = (
        db.query(ItemDB)
        .filter(ItemDB.catalog_id == catalog.id, ItemDB.item_id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item '{item_id}' not found"
        )

    db.delete(item)
    db.commit()

    return MessageResponse(message=f"Item '{item_id}' deleted successfully")
