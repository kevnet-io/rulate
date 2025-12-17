"""
Test fixtures for API integration tests.

This module provides database setup, TestClient, and helper fixtures
for testing the FastAPI application with a test SQLite database.
"""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# Set test database path BEFORE importing any API modules
# This ensures the test database is used when modules initialize
TEST_DB_DIR = tempfile.mkdtemp()
TEST_DB_PATH = os.path.join(TEST_DB_DIR, "test_rulate.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

# Now safe to import API modules - they will use the test database
from api.database.connection import init_db  # noqa: E402
from api.main import app  # noqa: E402


def pytest_configure(config):
    """Pytest hook called before test collection."""
    # Ensure test database directory exists
    os.makedirs(TEST_DB_DIR, exist_ok=True)


def pytest_unconfigure(config):
    """Pytest hook called after all tests finish."""
    # Cleanup test database
    import shutil
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR)


@pytest.fixture(scope="function")
def client():
    """
    FastAPI TestClient using the test database.

    The test database is automatically reset before each test,
    ensuring complete test isolation.
    """
    from api.database.connection import engine

    # Dispose of any existing database connections
    engine.dispose()

    # Remove existing database file
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    # Initialize fresh database with all tables
    init_db()

    # Create and yield the test client
    with TestClient(app) as test_client:
        yield test_client

    # Cleanup after test - dispose connections first
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


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
        "schema_name": "test_schema",
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
        "schema_name": "test_schema",
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
        "schema_name": "test_schema",
        "metadata": {"season": "summer", "year": 2024},
    }


@pytest.fixture
def minimal_catalog_payload():
    """Minimal catalog payload with only required fields."""
    return {
        "name": "minimal_catalog",
        "schema_name": "test_schema",
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
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def setup_ruleset(client, setup_schema, sample_ruleset_payload):
    """Create a ruleset in the test database (requires schema)."""
    response = client.post("/api/v1/rulesets", json=sample_ruleset_payload)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def setup_catalog(client, setup_schema, sample_catalog_payload):
    """Create a catalog in the test database (requires schema)."""
    response = client.post("/api/v1/catalogs", json=sample_catalog_payload)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def setup_item(client, setup_catalog, sample_item_payload):
    """Create an item in the test database (requires catalog)."""
    catalog_name = setup_catalog["name"]
    response = client.post(
        f"/api/v1/catalogs/{catalog_name}/items",
        json=sample_item_payload,
    )
    assert response.status_code == 201
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
