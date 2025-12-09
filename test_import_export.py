#!/usr/bin/env python3
"""
Test script for import/export functionality.
"""

import json
import time

import requests

BASE_URL = "http://localhost:8000/api/v1"


def create_test_data():
    """Create test schema, ruleset, and catalog."""
    print("Creating test data...")

    # Create a schema
    schema_data = {
        "name": "test_schema",
        "version": "1.0.0",
        "description": "Test schema for import/export",
        "dimensions": [
            {
                "name": "category",
                "type": "enum",
                "required": True,
                "values": ["type_a", "type_b", "type_c"],
            },
            {
                "name": "priority",
                "type": "integer",
                "required": False,
                "min": 1,
                "max": 5,
            },
        ],
    }

    response = requests.post(f"{BASE_URL}/schemas", json=schema_data)
    if response.status_code == 201:
        print(f"✓ Created schema: {schema_data['name']}")
    else:
        print(f"✗ Failed to create schema: {response.text}")
        return False

    # Create a ruleset
    ruleset_data = {
        "name": "test_ruleset",
        "version": "1.0.0",
        "description": "Test ruleset for import/export",
        "schema_name": "test_schema",
        "rules": [
            {
                "name": "same_category_exclusion",
                "type": "exclusion",
                "enabled": True,
                "condition": {"equals": {"field": "category"}},
            }
        ],
    }

    response = requests.post(f"{BASE_URL}/rulesets", json=ruleset_data)
    if response.status_code == 201:
        print(f"✓ Created ruleset: {ruleset_data['name']}")
    else:
        print(f"✗ Failed to create ruleset: {response.text}")
        return False

    # Create a catalog
    catalog_data = {
        "name": "test_catalog",
        "description": "Test catalog for import/export",
        "schema_name": "test_schema",
        "metadata": {"test": "value"},
    }

    response = requests.post(f"{BASE_URL}/catalogs", json=catalog_data)
    if response.status_code == 201:
        print(f"✓ Created catalog: {catalog_data['name']}")
    else:
        print(f"✗ Failed to create catalog: {response.text}")
        return False

    # Create items in catalog
    items = [
        {
            "item_id": "item_001",
            "name": "Test Item 1",
            "attributes": {"category": "type_a", "priority": 3},
        },
        {
            "item_id": "item_002",
            "name": "Test Item 2",
            "attributes": {"category": "type_b", "priority": 5},
        },
    ]

    for item in items:
        response = requests.post(
            f"{BASE_URL}/catalogs/test_catalog/items", json=item
        )
        if response.status_code == 201:
            print(f"✓ Created item: {item['item_id']}")
        else:
            print(f"✗ Failed to create item: {response.text}")
            return False

    return True


def test_export():
    """Test export functionality."""
    print("\n=== Testing Export ===")

    # Test export all
    print("\nExporting all data...")
    response = requests.get(f"{BASE_URL}/export/all")
    if response.status_code == 200:
        data = response.json()
        print("✓ Export all successful")
        print(f"  - Schemas: {len(data.get('schemas', []))}")
        print(f"  - RuleSets: {len(data.get('rulesets', []))}")
        print(f"  - Catalogs: {len(data.get('catalogs', []))}")

        # Save to file for import testing
        with open("/tmp/export_all.json", "w") as f:
            json.dump(data, f, indent=2)
        print("  - Saved to /tmp/export_all.json")
    else:
        print(f"✗ Failed to export all: {response.text}")
        return False

    # Test export schemas
    print("\nExporting schemas...")
    response = requests.get(f"{BASE_URL}/export/schemas")
    if response.status_code == 200:
        schemas = response.json()
        print(f"✓ Export schemas successful ({len(schemas)} schemas)")
        with open("/tmp/export_schemas.json", "w") as f:
            json.dump(schemas, f, indent=2)
    else:
        print(f"✗ Failed to export schemas: {response.text}")
        return False

    # Test export specific schema
    print("\nExporting specific schema...")
    response = requests.get(f"{BASE_URL}/export/schemas/test_schema")
    if response.status_code == 200:
        schema = response.json()
        print(f"✓ Export schema successful: {schema['name']}")
    else:
        print(f"✗ Failed to export schema: {response.text}")
        return False

    # Test export catalog
    print("\nExporting catalog...")
    response = requests.get(f"{BASE_URL}/export/catalogs/test_catalog")
    if response.status_code == 200:
        catalog = response.json()
        print(f"✓ Export catalog successful: {catalog['name']}")
        print(f"  - Items: {len(catalog.get('items', []))}")
    else:
        print(f"✗ Failed to export catalog: {response.text}")
        return False

    return True


def test_import():
    """Test import functionality."""
    print("\n=== Testing Import ===")

    # Delete existing data first to test import
    print("\nCleaning up existing test data...")
    requests.delete(f"{BASE_URL}/catalogs/test_catalog")
    requests.delete(f"{BASE_URL}/rulesets/test_ruleset")
    requests.delete(f"{BASE_URL}/schemas/test_schema")
    print("✓ Cleanup complete")

    # Test import all
    print("\nImporting all data...")
    with open("/tmp/export_all.json") as f:
        data = json.load(f)

    response = requests.post(
        f"{BASE_URL}/import/all?skip_existing=false", json=data
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Import all successful: {result['message']}")
    else:
        print(f"✗ Failed to import all: {response.text}")
        return False

    # Verify imported data
    print("\nVerifying imported data...")
    response = requests.get(f"{BASE_URL}/schemas/test_schema")
    if response.status_code == 200:
        print("✓ Schema imported successfully")
    else:
        print("✗ Schema not found after import")
        return False

    response = requests.get(f"{BASE_URL}/rulesets/test_ruleset")
    if response.status_code == 200:
        print("✓ RuleSet imported successfully")
    else:
        print("✗ RuleSet not found after import")
        return False

    response = requests.get(f"{BASE_URL}/catalogs/test_catalog")
    if response.status_code == 200:
        print("✓ Catalog imported successfully")
    else:
        print("✗ Catalog not found after import")
        return False

    response = requests.get(f"{BASE_URL}/catalogs/test_catalog/items")
    if response.status_code == 200:
        items = response.json()
        print(f"✓ Items imported successfully ({len(items)} items)")
    else:
        print("✗ Items not found after import")
        return False

    # Test skip_existing flag
    print("\nTesting skip_existing flag...")
    response = requests.post(
        f"{BASE_URL}/import/all?skip_existing=true", json=data
    )
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Import with skip_existing=true successful: {result['message']}")
    else:
        print(f"✗ Failed to import with skip_existing: {response.text}")
        return False

    return True


def cleanup():
    """Clean up test data."""
    print("\n=== Cleaning Up ===")
    requests.delete(f"{BASE_URL}/catalogs/test_catalog")
    requests.delete(f"{BASE_URL}/rulesets/test_ruleset")
    requests.delete(f"{BASE_URL}/schemas/test_schema")
    print("✓ Cleanup complete")


if __name__ == "__main__":
    try:
        # Wait for server to be ready
        print("Waiting for server to be ready...")
        for i in range(10):
            try:
                response = requests.get("http://localhost:8000/health")
                if response.status_code == 200:
                    print("✓ Server is ready")
                    break
            except Exception:  # Catch connection errors during startup
                time.sleep(1)
        else:
            print("✗ Server not responding")
            exit(1)

        # Run tests
        if not create_test_data():
            print("\n✗ Failed to create test data")
            exit(1)

        if not test_export():
            print("\n✗ Export tests failed")
            cleanup()
            exit(1)

        if not test_import():
            print("\n✗ Import tests failed")
            cleanup()
            exit(1)

        cleanup()
        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
