#!/usr/bin/env python3
"""
Seed the Rulate database with example wardrobe data using import/export format.

This script loads a complete domain from a JSON export file and imports it via
the /api/v1/import/all endpoint. By default, it uses the v2 domain (gender-agnostic
with granular coverage-layer modeling and 53 items).

Usage:
    python scripts/seed_database.py [--api-url API_URL] [--version {v1,v2}] [--skip-existing]

Examples:
    # Seed with v2 data (default - 53 items, coverage_layers)
    python scripts/seed_database.py

    # Seed with v1 data (19 items, body_zone + layer)
    python scripts/seed_database.py --version v1

    # Skip items that already exist (idempotent)
    python scripts/seed_database.py --skip-existing
"""

import argparse
import json
import sys
from pathlib import Path

import httpx


def load_json_file(file_path: Path) -> dict:
    """Load a JSON file and return its contents as a dictionary."""
    with open(file_path) as f:
        return json.load(f)


def seed_database(api_url: str, domain_file: Path, skip_existing: bool = False):
    """Seed the database with a complete domain from export JSON."""
    print(f"Seeding database via API at {api_url}")
    print(f"Using domain file: {domain_file.name}")
    print(f"Skip existing: {skip_existing}")
    print("=" * 60)

    # Load complete domain from JSON
    print("\nLoading domain data from JSON...")
    try:
        domain_data = load_json_file(domain_file)
    except Exception as e:
        print(f"Error loading domain file: {e}")
        sys.exit(1)

    # Validate structure
    required_keys = ["schemas", "rulesets", "cluster_rulesets", "catalogs"]
    missing_keys = [k for k in required_keys if k not in domain_data]
    if missing_keys:
        print(f"Error: Domain file missing required keys: {missing_keys}")
        sys.exit(1)

    # Import all data via single API call
    print("\nImporting domain data...")
    try:
        response = httpx.post(
            f"{api_url}/import/all",
            json=domain_data,
            params={"skip_existing": skip_existing},
            headers={"Content-Type": "application/json"},
            timeout=60.0,
        )

        if response.status_code == 200:
            result = response.json()
            print("\n✓ Import successful!")
            print(f"  {result['message']}")
        else:
            print(f"\n✗ Import failed: {response.status_code}")
            print(f"  {response.text}")
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error during import: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Database seeding completed!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Seed the Rulate database with example wardrobe data"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000/api/v1",
        help="Base URL of the Rulate API (default: http://localhost:8000/api/v1)",
    )
    parser.add_argument(
        "--version",
        choices=["v1", "v2"],
        default="v2",
        help="Wardrobe domain version: v1 (19 items) or v2 (53 items). Default: v2",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip entities that already exist instead of erroring",
    )

    args = parser.parse_args()

    # Determine domain file path
    examples_dir = Path(__file__).parent.parent / "examples" / "wardrobe"
    domain_file = examples_dir / f"{args.version}.json"

    # Verify file exists
    if not domain_file.exists():
        print(f"Error: Domain file not found: {domain_file}")
        sys.exit(1)

    seed_database(args.api_url, domain_file, args.skip_existing)


if __name__ == "__main__":
    main()
