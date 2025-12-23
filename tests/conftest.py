"""
Shared test fixtures for all tests.

This module provides reusable fixtures for schemas, rulesets, catalogs, and items
that can be used across all test files.
"""

import pytest

from rulate.models.catalog import Catalog, Item
from rulate.models.rule import Rule, RuleSet, RuleType
from rulate.models.schema import Schema

# ============================================================================
# Schema Fixtures
# ============================================================================


@pytest.fixture
def simple_schema():
    """Simple schema with basic dimension types."""
    return Schema(
        name="test_schema",
        version="1.0.0",
        description="Test schema for unit tests",
        dimensions=[
            {
                "name": "category",
                "type": "enum",
                "values": ["shirt", "pants", "shoes"],
                "required": True,
            },
            {"name": "color", "type": "string", "required": True},
            {"name": "size", "type": "string", "required": False},
            {"name": "formality", "type": "integer", "min": 1, "max": 5, "required": False},
            {"name": "layer", "type": "integer", "required": False},
            {"name": "body_zone", "type": "string", "required": False},
            {"name": "tags", "type": "list", "item_type": "string", "required": False},
            {"name": "price", "type": "float", "required": False},
            {"name": "available", "type": "boolean", "required": False},
        ],
    )


@pytest.fixture
def numeric_schema():
    """Schema focused on numeric dimensions for testing numeric operators."""
    return Schema(
        name="numeric_schema",
        version="1.0.0",
        dimensions=[
            {"name": "formality", "type": "integer", "min": 1, "max": 10, "required": True},
            {"name": "temperature", "type": "float", "min": -20.0, "max": 50.0, "required": False},
            {"name": "weight", "type": "float", "required": False},
        ],
    )


# ============================================================================
# Item Fixtures
# ============================================================================


@pytest.fixture
def item_blue_shirt():
    """Blue casual shirt for testing."""
    return Item(
        id="blue_shirt",
        name="Blue Casual Shirt",
        attributes={
            "category": "shirt",
            "color": "blue",
            "size": "M",
            "formality": 2,
            "layer": 1,
            "body_zone": "torso",
            "tags": ["casual", "summer"],
            "price": 29.99,
            "available": True,
        },
    )


@pytest.fixture
def item_red_shirt():
    """Red formal shirt for testing."""
    return Item(
        id="red_shirt",
        name="Red Formal Shirt",
        attributes={
            "category": "shirt",
            "color": "red",
            "size": "L",
            "formality": 4,
            "layer": 1,
            "body_zone": "torso",
            "tags": ["formal", "business"],
            "price": 59.99,
            "available": True,
        },
    )


@pytest.fixture
def item_blue_pants():
    """Blue casual pants for testing."""
    return Item(
        id="blue_pants",
        name="Blue Casual Pants",
        attributes={
            "category": "pants",
            "color": "blue",
            "size": "32",
            "formality": 2,
            "layer": 1,
            "body_zone": "legs",
            "tags": ["casual"],
            "price": 39.99,
            "available": True,
        },
    )


@pytest.fixture
def item_black_pants():
    """Black formal pants for testing."""
    return Item(
        id="black_pants",
        name="Black Formal Pants",
        attributes={
            "category": "pants",
            "color": "black",
            "size": "34",
            "formality": 5,
            "layer": 1,
            "body_zone": "legs",
            "tags": ["formal", "business"],
            "price": 79.99,
            "available": False,
        },
    )


@pytest.fixture
def item_brown_shoes():
    """Brown casual shoes for testing."""
    return Item(
        id="brown_shoes",
        name="Brown Casual Shoes",
        attributes={
            "category": "shoes",
            "color": "brown",
            "size": "10",
            "formality": 3,
            "body_zone": "feet",
            "tags": ["casual"],
            "price": 89.99,
            "available": True,
        },
    )


@pytest.fixture
def item_minimal():
    """Item with minimal attributes (only required fields)."""
    return Item(
        id="minimal",
        name="Minimal Item",
        attributes={
            "category": "shirt",
            "color": "white",
        },
    )


@pytest.fixture
def item_with_nulls():
    """Item with some null/missing attributes."""
    return Item(
        id="with_nulls",
        name="Item With Nulls",
        attributes={
            "category": "pants",
            "color": "gray",
            "formality": None,  # Explicitly None
            # missing: layer, body_zone, tags, etc.
        },
    )


@pytest.fixture
def item_dress_shirt():
    """Dress shirt covering chest, waist, upper back, lower back at layer 2.0."""
    return Item(
        id="dress_shirt",
        name="Dress Shirt",
        attributes={
            "coverage_layers": [
                {"parts": ["chest", "waist", "upper_back", "lower_back"], "layer": 2.0}
            ]
        },
    )


@pytest.fixture
def item_undershirt():
    """Undershirt covering chest, waist, upper back, lower back at layer 1.0."""
    return Item(
        id="undershirt",
        name="Undershirt",
        attributes={
            "coverage_layers": [
                {"parts": ["chest", "waist", "upper_back", "lower_back"], "layer": 1.0}
            ]
        },
    )


@pytest.fixture
def item_jeans():
    """Jeans covering hips, upper_leg, lower_leg at layer 1.5."""
    return Item(
        id="jeans",
        name="Jeans",
        attributes={
            "coverage_layers": [{"parts": ["hips", "upper_leg", "lower_leg"], "layer": 1.5}]
        },
    )


@pytest.fixture
def item_phasing_hybrid_a():
    """Problematic hybrid: chest at 2.0, legs at 1.0."""
    return Item(
        id="hybrid_a",
        name="Hybrid A",
        attributes={
            "coverage_layers": [
                {"parts": ["chest", "waist"], "layer": 2.0},
                {"parts": ["hips", "legs"], "layer": 1.0},
            ]
        },
    )


@pytest.fixture
def item_phasing_hybrid_b():
    """Problematic hybrid: chest at 1.0, legs at 2.0."""
    return Item(
        id="hybrid_b",
        name="Hybrid B",
        attributes={
            "coverage_layers": [
                {"parts": ["chest", "waist"], "layer": 1.0},
                {"parts": ["hips", "legs"], "layer": 2.0},
            ]
        },
    )


# ============================================================================
# Catalog Fixtures
# ============================================================================


@pytest.fixture
def simple_catalog(
    simple_schema,
    item_blue_shirt,
    item_red_shirt,
    item_blue_pants,
    item_black_pants,
    item_brown_shoes,
):
    """Simple catalog with 5 items for testing."""
    return Catalog(
        name="test_catalog",
        schema_ref=simple_schema.name,
        items=[
            item_blue_shirt,
            item_red_shirt,
            item_blue_pants,
            item_black_pants,
            item_brown_shoes,
        ],
    )


@pytest.fixture
def cluster_catalog():
    """Catalog with items designed for cluster testing."""
    items = [
        Item(
            id=f"item_{i}",
            name=f"Item {i}",
            attributes={
                "category": "shirt" if i % 3 == 0 else "pants" if i % 3 == 1 else "shoes",
                "color": ["red", "blue", "green", "black"][i % 4],
                "formality": (i % 5) + 1,
                "body_zone": "torso" if i % 3 == 0 else "legs" if i % 3 == 1 else "feet",
            },
        )
        for i in range(10)
    ]
    return Catalog(name="cluster_catalog", schema_ref="test_schema", items=items)


# ============================================================================
# RuleSet Fixtures
# ============================================================================


@pytest.fixture
def simple_ruleset():
    """Simple ruleset with basic exclusion and requirement rules."""
    return RuleSet(
        name="test_rules",
        version="1.0.0",
        schema_ref="test_schema",
        rules=[
            Rule(
                name="different_categories",
                type=RuleType.EXCLUSION,
                enabled=True,
                condition={"equals": {"field": "category"}},
            ),
            Rule(
                name="similar_formality",
                type=RuleType.REQUIREMENT,
                enabled=True,
                condition={"abs_diff": {"field": "formality", "max": 2}},
            ),
        ],
    )


@pytest.fixture
def complex_ruleset():
    """Complex ruleset with nested logical operators."""
    return RuleSet(
        name="complex_rules",
        version="1.0.0",
        schema_ref="test_schema",
        rules=[
            Rule(
                name="same_zone_different_layer",
                type=RuleType.EXCLUSION,
                enabled=True,
                condition={
                    "all": [
                        {"equals": {"field": "body_zone"}},
                        {"not": {"has_different": {"field": "layer"}}},
                    ]
                },
            ),
            Rule(
                name="color_or_formality_match",
                type=RuleType.REQUIREMENT,
                enabled=True,
                condition={
                    "any": [
                        {"equals": {"field": "color"}},
                        {"abs_diff": {"field": "formality", "max": 1}},
                    ]
                },
            ),
        ],
    )


# ============================================================================
# Utility Fixtures
# ============================================================================


@pytest.fixture
def sample_items_list(item_blue_shirt, item_red_shirt, item_blue_pants, item_brown_shoes):
    """List of sample items for cluster testing."""
    return [item_blue_shirt, item_red_shirt, item_blue_pants, item_brown_shoes]
