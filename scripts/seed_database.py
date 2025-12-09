#!/usr/bin/env python3
"""
Seed the Rulate database with example wardrobe data.

This script loads the example wardrobe schema, rules, cluster rules, and catalog
into the database via the API.

Usage:
    python scripts/seed_database.py [--api-url API_URL]
"""

import argparse
import sys
from pathlib import Path

import requests
import yaml


def load_yaml_file(file_path: Path) -> dict:
    """Load a YAML file and return its contents as a dictionary."""
    with open(file_path) as f:
        return yaml.safe_load(f)


def seed_database(api_url: str, examples_dir: Path):
    """Seed the database with example data."""
    print(f"Seeding database via API at {api_url}")
    print("=" * 60)

    # Load example files
    schema_file = examples_dir / "schema.yaml"
    rules_file = examples_dir / "rules.yaml"
    cluster_rules_file = examples_dir / "cluster_rules.yaml"
    catalog_file = examples_dir / "catalog.yaml"

    # Check that all files exist
    for file_path in [schema_file, rules_file, cluster_rules_file, catalog_file]:
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            sys.exit(1)

    # Load data from files
    print("\nLoading data from files...")
    schema_data = load_yaml_file(schema_file)
    rules_data = load_yaml_file(rules_file)
    cluster_rules_data = load_yaml_file(cluster_rules_file)
    catalog_data = load_yaml_file(catalog_file)

    # 1. Create Schema
    print("\n1. Creating schema...")
    schema_payload = {
        "name": schema_data["name"],
        "version": schema_data["version"],
        "description": schema_data.get("description"),
        "dimensions": schema_data["dimensions"]
    }

    try:
        response = requests.post(
            f"{api_url}/schemas",
            json=schema_payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            print(f"   ✓ Created schema: {schema_data['name']}")
        elif response.status_code == 409:
            print(f"   ⚠ Schema already exists: {schema_data['name']}")
        else:
            print(f"   ✗ Failed to create schema: {response.status_code}")
            print(f"     {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ Error creating schema: {e}")
        sys.exit(1)

    # 2. Create Pairwise RuleSet
    print("\n2. Creating pairwise ruleset...")
    ruleset_payload = {
        "name": rules_data["name"],
        "version": rules_data["version"],
        "description": rules_data.get("description"),
        "schema_name": rules_data["schema_ref"],
        "rules": rules_data["rules"]
    }

    try:
        response = requests.post(
            f"{api_url}/rulesets",
            json=ruleset_payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            print(f"   ✓ Created ruleset: {rules_data['name']}")
        elif response.status_code == 409:
            print(f"   ⚠ Ruleset already exists: {rules_data['name']}")
        else:
            print(f"   ✗ Failed to create ruleset: {response.status_code}")
            print(f"     {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ Error creating ruleset: {e}")
        sys.exit(1)

    # 3. Create Cluster RuleSet
    print("\n3. Creating cluster ruleset...")
    cluster_ruleset_payload = {
        "name": cluster_rules_data["name"],
        "version": cluster_rules_data["version"],
        "description": cluster_rules_data.get("description"),
        "schema_name": cluster_rules_data["schema_ref"],
        "pairwise_ruleset_name": cluster_rules_data["pairwise_ruleset_ref"],
        "rules": cluster_rules_data["rules"]
    }

    try:
        response = requests.post(
            f"{api_url}/cluster-rulesets",
            json=cluster_ruleset_payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            print(f"   ✓ Created cluster ruleset: {cluster_rules_data['name']}")
        elif response.status_code == 409:
            print(f"   ⚠ Cluster ruleset already exists: {cluster_rules_data['name']}")
        else:
            print(f"   ✗ Failed to create cluster ruleset: {response.status_code}")
            print(f"     {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ Error creating cluster ruleset: {e}")
        sys.exit(1)

    # 4. Create Catalog
    print("\n4. Creating catalog...")
    catalog_payload = {
        "name": catalog_data["name"],
        "description": catalog_data.get("description"),
        "schema_name": catalog_data["schema_ref"],
        "metadata": catalog_data.get("metadata", {})
    }

    try:
        response = requests.post(
            f"{api_url}/catalogs",
            json=catalog_payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            print(f"   ✓ Created catalog: {catalog_data['name']}")
        elif response.status_code == 409:
            print(f"   ⚠ Catalog already exists: {catalog_data['name']}")
            # If catalog exists, skip item creation
            print("\nSkipping item creation (catalog already exists)")
            print("\n" + "=" * 60)
            print("Database seeding completed!")
            return
        else:
            print(f"   ✗ Failed to create catalog: {response.status_code}")
            print(f"     {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ Error creating catalog: {e}")
        sys.exit(1)

    # 5. Create Items
    print("\n5. Creating items...")
    items_created = 0
    items_failed = 0

    for item_data in catalog_data["items"]:
        item_payload = {
            "item_id": item_data["id"],
            "name": item_data["name"],
            "attributes": item_data["attributes"],
            "metadata": item_data.get("metadata", {})
        }

        try:
            response = requests.post(
                f"{api_url}/catalogs/{catalog_data['name']}/items",
                json=item_payload,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 201:
                items_created += 1
                print(f"   ✓ Created item: {item_data['id']} ({item_data['name']})")
            else:
                items_failed += 1
                print(f"   ✗ Failed to create item {item_data['id']}: {response.status_code}")
        except Exception as e:
            items_failed += 1
            print(f"   ✗ Error creating item {item_data['id']}: {e}")

    print(f"\n   Items created: {items_created}")
    if items_failed > 0:
        print(f"   Items failed: {items_failed}")

    print("\n" + "=" * 60)
    print("Database seeding completed!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Seed the Rulate database with example data")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000/api/v1",
        help="Base URL of the Rulate API (default: http://localhost:8000/api/v1)"
    )
    parser.add_argument(
        "--examples-dir",
        type=Path,
        default=Path(__file__).parent.parent / "examples" / "wardrobe",
        help="Path to examples directory (default: examples/wardrobe)"
    )

    args = parser.parse_args()

    # Verify examples directory exists
    if not args.examples_dir.exists():
        print(f"Error: Examples directory not found: {args.examples_dir}")
        sys.exit(1)

    seed_database(args.api_url, args.examples_dir)


if __name__ == "__main__":
    main()
