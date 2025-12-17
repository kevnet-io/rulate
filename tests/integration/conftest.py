"""
Test fixtures for API integration tests.

This module provides database setup, TestClient, and helper fixtures
for testing the FastAPI application with an in-memory SQLite database.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import api.database.connection as db_connection
from api.database.models import Base


# Create app without lifespan to avoid production DB initialization
from fastapi import FastAPI
from api.routers import catalogs, clusters, evaluation, import_export, rulesets, schemas


@pytest.fixture(scope="function")
def test_db_engine():
    """
    Create an in-memory SQLite database engine for testing.

    Each test gets a fresh database that is automatically cleaned up.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def client(test_db_engine):
    """
    FastAPI TestClient with patched database connection to use test database.

    This client makes HTTP requests to the API using an in-memory database,
    ensuring test isolation and fast execution.
    """
    # Create test sessionmaker
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine,
    )

    # Patch the SessionLocal in the connection module
    with patch.object(db_connection, 'SessionLocal', TestingSessionLocal):
        # Create a fresh app for each test
        app = FastAPI(
            title="Rulate API Test",
            description="Test version of Rulate API",
            version="0.1.0",
        )

        # Include routers
        app.include_router(schemas.router, prefix="/api/v1", tags=["schemas"])
        app.include_router(rulesets.router, prefix="/api/v1", tags=["rulesets"])
        app.include_router(catalogs.router, prefix="/api/v1", tags=["catalogs"])
        app.include_router(evaluation.router, prefix="/api/v1", tags=["evaluation"])
        app.include_router(clusters.router, prefix="/api/v1", tags=["clusters"])
        app.include_router(import_export.router, prefix="/api/v1", tags=["import_export"])

        with TestClient(app) as test_client:
            yield test_client


# ============================================================================
# Schema Fixtures
# ============================================================================


@pytest.fixture
def sample_schema_payload():
    """Sample schema payload for testing."""
    return {
        "name": "test_schema",
        "version": "1.0.0",
        "description": "Test schema for integration tests",
        "dimensions": [
            {
                "name": "category",
                "type": "enum",
                "values": ["shirt", "pants", "shoes"],
                "required": True,
            },
            {
                "name": "color",
                "type": "string",
                "required": True,
            },
            {
                "name": "size",
                "type": "string",
                "required": False,
            },
            {
                "name": "formality",
                "type": "integer",
                "min": 1,
                "max": 5,
                "required": False,
            },
            {
                "name": "price",
                "type": "float",
                "min": 0.0,
                "required": False,
            },
            {
                "name": "available",
                "type": "boolean",
                "required": False,
            },
            {
                "name": "tags",
                "type": "list",
                "item_type": "string",
                "required": False,
            },
        ],
    }


@pytest.fixture
def minimal_schema_payload():
    """Minimal schema payload with only required fields."""
    return {
        "name": "minimal_schema",
        "version": "1.0.0",
        "dimensions": [
            {
                "name": "id",
                "type": "string",
                "required": True,
            }
        ],
    }


# ============================================================================
# RuleSet Fixtures
# ============================================================================


@pytest.fixture
def sample_ruleset_payload():
    """Sample ruleset payload for testing."""
    return {
        "name": "test_rules",
        "version": "1.0.0",
        "description": "Test ruleset for integration tests",
        "schema_ref": "test_schema",
        "rules": [
            {
                "name": "different_categories",
                "type": "exclusion",
                "enabled": True,
                "condition": {"equals": {"field": "category"}},
            },
            {
                "name": "similar_formality",
                "type": "requirement",
                "enabled": True,
                "condition": {"abs_diff": {"field": "formality", "max": 2}},
            },
        ],
    }


@pytest.fixture
def minimal_ruleset_payload():
    """Minimal ruleset payload with empty rules."""
    return {
        "name": "minimal_rules",
        "version": "1.0.0",
        "schema_ref": "test_schema",
        "rules": [],
    }


# ============================================================================
# Catalog Fixtures
# ============================================================================


@pytest.fixture
def sample_catalog_payload():
    """Sample catalog payload for testing."""
    return {
        "name": "test_catalog",
        "description": "Test catalog for integration tests",
        "schema_ref": "test_schema",
        "metadata": {"season": "summer", "year": 2024},
    }


@pytest.fixture
def minimal_catalog_payload():
    """Minimal catalog payload with only required fields."""
    return {
        "name": "minimal_catalog",
        "schema_ref": "test_schema",
    }


# ============================================================================
# Item Fixtures
# ============================================================================


@pytest.fixture
def sample_item_payload():
    """Sample item payload for testing."""
    return {
        "item_id": "blue_shirt_001",
        "name": "Blue Casual Shirt",
        "attributes": {
            "category": "shirt",
            "color": "blue",
            "size": "M",
            "formality": 2,
            "price": 29.99,
            "available": True,
            "tags": ["casual", "summer"],
        },
        "metadata": {"brand": "TestBrand", "sku": "BS001"},
    }


@pytest.fixture
def minimal_item_payload():
    """Minimal item payload with only required attributes."""
    return {
        "item_id": "minimal_001",
        "name": "Minimal Item",
        "attributes": {
            "category": "shirt",
            "color": "white",
        },
    }


# ============================================================================
# Setup Fixtures (create full datasets)
# ============================================================================


@pytest.fixture
def setup_schema(client, sample_schema_payload):
    """Create a schema in the test database."""
    response = client.post("/api/v1/schemas", json=sample_schema_payload)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def setup_ruleset(client, setup_schema, sample_ruleset_payload):
    """Create a ruleset in the test database (requires schema)."""
    response = client.post("/api/v1/rulesets", json=sample_ruleset_payload)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def setup_catalog(client, setup_schema, sample_catalog_payload):
    """Create a catalog in the test database (requires schema)."""
    response = client.post("/api/v1/catalogs", json=sample_catalog_payload)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def setup_item(client, setup_catalog, sample_item_payload):
    """Create an item in the test database (requires catalog)."""
    catalog_name = setup_catalog["name"]
    response = client.post(
        f"/api/v1/catalogs/{catalog_name}/items",
        json=sample_item_payload,
    )
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def setup_full_dataset(client, setup_schema, setup_ruleset, setup_catalog, setup_item):
    """
    Setup a complete dataset with schema, ruleset, catalog, and items.

    Returns a dict with all created entities for easy access in tests.
    """
    return {
        "schema": setup_schema,
        "ruleset": setup_ruleset,
        "catalog": setup_catalog,
        "item": setup_item,
    }
