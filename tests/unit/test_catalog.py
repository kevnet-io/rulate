"""
Comprehensive tests for Catalog and Item models.

Tests cover:
- Item creation, validation, and attribute management
- Catalog creation, validation, and item management
- Edge cases and error handling
"""

from datetime import datetime

import pytest

from rulate.models.catalog import Catalog, Item


class TestItem:
    """Tests for the Item model."""

    def test_creates_item_with_required_fields(self):
        """Item can be created with just ID and name."""
        item = Item(id="test_001", name="Test Item")
        assert item.id == "test_001"
        assert item.name == "Test Item"
        assert item.attributes == {}
        assert item.metadata == {}

    def test_creates_item_with_attributes(self):
        """Item can be created with attributes."""
        item = Item(
            id="shirt_001",
            name="Blue Shirt",
            attributes={"color": "blue", "size": "M", "formality": 3},
        )
        assert item.attributes == {"color": "blue", "size": "M", "formality": 3}

    def test_creates_item_with_metadata(self):
        """Item can be created with metadata."""
        item = Item(
            id="shirt_001",
            name="Blue Shirt",
            metadata={"tags": ["casual", "work"], "notes": "Favorite shirt"},
        )
        assert item.metadata == {"tags": ["casual", "work"], "notes": "Favorite shirt"}

    def test_raises_error_for_empty_id(self):
        """Item ID cannot be empty string."""
        with pytest.raises(ValueError, match="Item ID cannot be empty"):
            Item(id="", name="Test Item")

    def test_raises_error_for_whitespace_only_id(self):
        """Item ID cannot be whitespace only."""
        with pytest.raises(ValueError, match="Item ID cannot be empty"):
            Item(id="   ", name="Test Item")

    def test_raises_error_for_empty_name(self):
        """Item name cannot be empty string."""
        with pytest.raises(ValueError, match="Item name cannot be empty"):
            Item(id="test_001", name="")

    def test_raises_error_for_whitespace_only_name(self):
        """Item name cannot be whitespace only."""
        with pytest.raises(ValueError, match="Item name cannot be empty"):
            Item(id="test_001", name="   ")

    def test_get_attribute_returns_value(self):
        """get_attribute() returns the attribute value."""
        item = Item(
            id="test_001",
            name="Test Item",
            attributes={"color": "blue", "size": "M"},
        )
        assert item.get_attribute("color") == "blue"
        assert item.get_attribute("size") == "M"

    def test_get_attribute_returns_default_when_missing(self):
        """get_attribute() returns default value when attribute doesn't exist."""
        item = Item(id="test_001", name="Test Item", attributes={"color": "blue"})
        assert item.get_attribute("size") is None
        assert item.get_attribute("size", "default") == "default"

    def test_get_attribute_returns_none_default_when_not_specified(self):
        """get_attribute() returns None when attribute missing and no default."""
        item = Item(id="test_001", name="Test Item")
        assert item.get_attribute("missing_attr") is None

    def test_has_attribute_returns_true_when_present(self):
        """has_attribute() returns True when attribute exists."""
        item = Item(id="test_001", name="Test Item", attributes={"color": "blue"})
        assert item.has_attribute("color") is True

    def test_has_attribute_returns_false_when_missing(self):
        """has_attribute() returns False when attribute doesn't exist."""
        item = Item(id="test_001", name="Test Item", attributes={"color": "blue"})
        assert item.has_attribute("size") is False

    def test_set_attribute_adds_new_attribute(self):
        """set_attribute() adds a new attribute."""
        item = Item(id="test_001", name="Test Item")
        item.set_attribute("color", "blue")
        assert item.attributes["color"] == "blue"

    def test_set_attribute_updates_existing_attribute(self):
        """set_attribute() updates an existing attribute."""
        item = Item(id="test_001", name="Test Item", attributes={"color": "blue"})
        item.set_attribute("color", "red")
        assert item.attributes["color"] == "red"

    def test_get_metadata_returns_value(self):
        """get_metadata() returns the metadata value."""
        item = Item(
            id="test_001",
            name="Test Item",
            metadata={"tags": ["casual"], "notes": "Test note"},
        )
        assert item.get_metadata("tags") == ["casual"]
        assert item.get_metadata("notes") == "Test note"

    def test_get_metadata_returns_default_when_missing(self):
        """get_metadata() returns default value when key doesn't exist."""
        item = Item(id="test_001", name="Test Item", metadata={"tags": ["casual"]})
        assert item.get_metadata("notes") is None
        assert item.get_metadata("notes", "default") == "default"


class TestCatalog:
    """Tests for the Catalog model."""

    def test_creates_catalog_with_required_fields(self):
        """Catalog can be created with just name and schema_ref."""
        catalog = Catalog(name="test_catalog", schema_ref="test_schema")
        assert catalog.name == "test_catalog"
        assert catalog.schema_ref == "test_schema"
        assert catalog.description is None
        assert catalog.items == []
        assert catalog.metadata == {}
        assert isinstance(catalog.created_at, datetime)
        assert isinstance(catalog.updated_at, datetime)

    def test_creates_catalog_with_items(self):
        """Catalog can be created with items."""
        items = [
            Item(id="item_001", name="Item 1"),
            Item(id="item_002", name="Item 2"),
        ]
        catalog = Catalog(name="test_catalog", schema_ref="test_schema", items=items)
        assert len(catalog.items) == 2
        assert catalog.items[0].id == "item_001"
        assert catalog.items[1].id == "item_002"

    def test_creates_catalog_with_description(self):
        """Catalog can be created with description."""
        catalog = Catalog(
            name="test_catalog",
            schema_ref="test_schema",
            description="Test catalog for unit tests",
        )
        assert catalog.description == "Test catalog for unit tests"

    def test_creates_catalog_with_metadata(self):
        """Catalog can be created with metadata."""
        catalog = Catalog(
            name="test_catalog",
            schema_ref="test_schema",
            metadata={"owner": "test_user", "version": "1.0"},
        )
        assert catalog.metadata == {"owner": "test_user", "version": "1.0"}

    def test_raises_error_for_empty_name(self):
        """Catalog name cannot be empty string."""
        with pytest.raises(ValueError, match="Catalog name cannot be empty"):
            Catalog(name="", schema_ref="test_schema")

    def test_raises_error_for_whitespace_only_name(self):
        """Catalog name cannot be whitespace only."""
        with pytest.raises(ValueError, match="Catalog name cannot be empty"):
            Catalog(name="   ", schema_ref="test_schema")

    def test_raises_error_for_empty_schema_ref(self):
        """Schema reference cannot be empty string."""
        with pytest.raises(ValueError, match="Schema reference cannot be empty"):
            Catalog(name="test_catalog", schema_ref="")

    def test_raises_error_for_whitespace_only_schema_ref(self):
        """Schema reference cannot be whitespace only."""
        with pytest.raises(ValueError, match="Schema reference cannot be empty"):
            Catalog(name="test_catalog", schema_ref="   ")

    def test_get_item_returns_item_by_id(self):
        """get_item() returns item when ID exists."""
        items = [
            Item(id="item_001", name="Item 1"),
            Item(id="item_002", name="Item 2"),
        ]
        catalog = Catalog(name="test_catalog", schema_ref="test_schema", items=items)

        item = catalog.get_item("item_001")
        assert item is not None
        assert item.id == "item_001"
        assert item.name == "Item 1"

    def test_get_item_returns_none_when_not_found(self):
        """get_item() returns None when item doesn't exist."""
        catalog = Catalog(name="test_catalog", schema_ref="test_schema")
        assert catalog.get_item("nonexistent") is None

    def test_add_item_appends_to_catalog(self):
        """add_item() adds item to catalog."""
        catalog = Catalog(name="test_catalog", schema_ref="test_schema")
        item = Item(id="item_001", name="Item 1")

        catalog.add_item(item)

        assert len(catalog.items) == 1
        assert catalog.items[0].id == "item_001"

    def test_add_item_updates_timestamp(self):
        """add_item() updates the updated_at timestamp."""
        catalog = Catalog(name="test_catalog", schema_ref="test_schema")
        original_time = catalog.updated_at

        item = Item(id="item_001", name="Item 1")
        catalog.add_item(item)

        assert catalog.updated_at >= original_time

    def test_add_item_raises_error_for_duplicate_id(self):
        """add_item() raises error when item with same ID exists."""
        catalog = Catalog(name="test_catalog", schema_ref="test_schema")
        item1 = Item(id="item_001", name="Item 1")
        item2 = Item(id="item_001", name="Item 2")

        catalog.add_item(item1)

        with pytest.raises(ValueError, match="Item with ID 'item_001' already exists"):
            catalog.add_item(item2)

    def test_remove_item_deletes_item(self):
        """remove_item() removes item from catalog."""
        items = [
            Item(id="item_001", name="Item 1"),
            Item(id="item_002", name="Item 2"),
        ]
        catalog = Catalog(name="test_catalog", schema_ref="test_schema", items=items)

        result = catalog.remove_item("item_001")

        assert result is True
        assert len(catalog.items) == 1
        assert catalog.get_item("item_001") is None
        assert catalog.get_item("item_002") is not None

    def test_remove_item_updates_timestamp(self):
        """remove_item() updates the updated_at timestamp."""
        items = [Item(id="item_001", name="Item 1")]
        catalog = Catalog(name="test_catalog", schema_ref="test_schema", items=items)
        original_time = catalog.updated_at

        catalog.remove_item("item_001")

        assert catalog.updated_at >= original_time

    def test_remove_item_returns_false_when_not_found(self):
        """remove_item() returns False when item doesn't exist."""
        catalog = Catalog(name="test_catalog", schema_ref="test_schema")
        result = catalog.remove_item("nonexistent")
        assert result is False

    def test_update_item_replaces_item(self):
        """update_item() replaces existing item."""
        items = [Item(id="item_001", name="Item 1", attributes={"color": "blue"})]
        catalog = Catalog(name="test_catalog", schema_ref="test_schema", items=items)

        new_item = Item(id="item_001", name="Updated Item", attributes={"color": "red"})
        result = catalog.update_item("item_001", new_item)

        assert result is True
        updated = catalog.get_item("item_001")
        assert updated.name == "Updated Item"
        assert updated.attributes["color"] == "red"

    def test_update_item_updates_timestamp(self):
        """update_item() updates the updated_at timestamp."""
        items = [Item(id="item_001", name="Item 1")]
        catalog = Catalog(name="test_catalog", schema_ref="test_schema", items=items)
        original_time = catalog.updated_at

        new_item = Item(id="item_001", name="Updated Item")
        catalog.update_item("item_001", new_item)

        assert catalog.updated_at >= original_time

    def test_update_item_returns_false_when_not_found(self):
        """update_item() returns False when item doesn't exist."""
        catalog = Catalog(name="test_catalog", schema_ref="test_schema")
        new_item = Item(id="nonexistent", name="Item")

        result = catalog.update_item("nonexistent", new_item)
        assert result is False

    def test_get_items_by_attribute_returns_matching_items(self):
        """get_items_by_attribute() returns items with matching attribute."""
        items = [
            Item(id="item_001", name="Item 1", attributes={"color": "blue"}),
            Item(id="item_002", name="Item 2", attributes={"color": "red"}),
            Item(id="item_003", name="Item 3", attributes={"color": "blue"}),
        ]
        catalog = Catalog(name="test_catalog", schema_ref="test_schema", items=items)

        blue_items = catalog.get_items_by_attribute("color", "blue")

        assert len(blue_items) == 2
        assert all(item.get_attribute("color") == "blue" for item in blue_items)

    def test_get_items_by_attribute_returns_empty_list_when_no_matches(self):
        """get_items_by_attribute() returns empty list when no items match."""
        items = [
            Item(id="item_001", name="Item 1", attributes={"color": "blue"}),
        ]
        catalog = Catalog(name="test_catalog", schema_ref="test_schema", items=items)

        result = catalog.get_items_by_attribute("color", "green")
        assert result == []

    def test_get_items_by_attribute_returns_empty_list_when_attribute_missing(self):
        """get_items_by_attribute() returns empty list when attribute doesn't exist."""
        items = [
            Item(id="item_001", name="Item 1", attributes={"color": "blue"}),
        ]
        catalog = Catalog(name="test_catalog", schema_ref="test_schema", items=items)

        result = catalog.get_items_by_attribute("size", "M")
        assert result == []

    def test_len_returns_item_count(self):
        """len() returns the number of items in catalog."""
        items = [
            Item(id="item_001", name="Item 1"),
            Item(id="item_002", name="Item 2"),
            Item(id="item_003", name="Item 3"),
        ]
        catalog = Catalog(name="test_catalog", schema_ref="test_schema", items=items)
        assert len(catalog) == 3

    def test_len_returns_zero_for_empty_catalog(self):
        """len() returns 0 for empty catalog."""
        catalog = Catalog(name="test_catalog", schema_ref="test_schema")
        assert len(catalog) == 0


class TestCatalogItemIntegration:
    """Integration tests for Catalog and Item working together."""

    def test_catalog_operations_maintain_item_identity(self):
        """Catalog operations don't corrupt item data."""
        catalog = Catalog(name="test_catalog", schema_ref="test_schema")

        # Add items
        item1 = Item(
            id="item_001",
            name="Item 1",
            attributes={"color": "blue", "size": "M"},
            metadata={"tags": ["test"]},
        )
        catalog.add_item(item1)

        # Retrieve and verify
        retrieved = catalog.get_item("item_001")
        assert retrieved.id == item1.id
        assert retrieved.name == item1.name
        assert retrieved.attributes == item1.attributes
        assert retrieved.metadata == item1.metadata

    def test_multiple_catalogs_dont_interfere(self):
        """Multiple catalogs can exist independently."""
        catalog1 = Catalog(name="catalog_1", schema_ref="schema_1")
        catalog2 = Catalog(name="catalog_2", schema_ref="schema_2")

        item1 = Item(id="item_001", name="Item 1")
        item2 = Item(id="item_002", name="Item 2")

        catalog1.add_item(item1)
        catalog2.add_item(item2)

        assert len(catalog1) == 1
        assert len(catalog2) == 1
        assert catalog1.get_item("item_001") is not None
        assert catalog1.get_item("item_002") is None
        assert catalog2.get_item("item_002") is not None
        assert catalog2.get_item("item_001") is None
