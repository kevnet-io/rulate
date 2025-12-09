"""
Catalog models for storing collections of items.

A catalog contains items with their attributes, validated against a schema.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Item(BaseModel):
    """
    An item in a catalog with its attributes.

    Items represent the objects being compared (e.g., clothing items, products).
    Each item has an ID, name, and a dictionary of attributes that correspond
    to dimensions defined in the schema.

    Example:
        Item(
            id="shirt_001",
            name="Blue Oxford Shirt",
            attributes={
                "category": "shirt",
                "body_zone": "torso",
                "formality": 4,
                "colors": ["blue", "white"]
            },
            metadata={"tags": ["work", "casual"]}
        )
    """

    id: str = Field(..., description="Unique identifier for the item")
    name: str = Field(..., description="Human-readable name of the item")
    attributes: dict[str, Any] = Field(
        default_factory=dict, description="Attribute values for this item"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional metadata (tags, notes, etc.)"
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Ensure item ID is valid."""
        if not v or not v.strip():
            raise ValueError("Item ID cannot be empty")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure item name is valid."""
        if not v or not v.strip():
            raise ValueError("Item name cannot be empty")
        return v

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Get an attribute value by key.

        Args:
            key: The attribute name
            default: Default value if attribute is not present

        Returns:
            The attribute value, or default if not found
        """
        return self.attributes.get(key, default)

    def has_attribute(self, key: str) -> bool:
        """
        Check if an attribute is present.

        Args:
            key: The attribute name

        Returns:
            True if the attribute exists
        """
        return key in self.attributes

    def set_attribute(self, key: str, value: Any) -> None:
        """
        Set an attribute value.

        Args:
            key: The attribute name
            value: The value to set
        """
        self.attributes[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get a metadata value by key.

        Args:
            key: The metadata key
            default: Default value if key is not present

        Returns:
            The metadata value, or default if not found
        """
        return self.metadata.get(key, default)


class Catalog(BaseModel):
    """
    A collection of items validated against a schema.

    Catalogs group related items together and associate them with a schema
    that defines their valid attributes.

    Example:
        Catalog(
            name="my_wardrobe",
            schema_ref="wardrobe_v1",
            items=[
                Item(id="shirt_001", name="Blue Shirt", ...),
                Item(id="pants_001", name="Dark Jeans", ...),
            ]
        )
    """

    name: str = Field(..., description="Unique name of the catalog")
    schema_ref: str = Field(..., description="Name of the schema this catalog uses")
    description: str | None = Field(None, description="Human-readable description")
    items: list[Item] = Field(default_factory=list, description="Items in this catalog")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Optional metadata")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure catalog name is valid."""
        if not v or not v.strip():
            raise ValueError("Catalog name cannot be empty")
        return v

    @field_validator("schema_ref")
    @classmethod
    def validate_schema_ref(cls, v: str) -> str:
        """Ensure schema reference is valid."""
        if not v or not v.strip():
            raise ValueError("Schema reference cannot be empty")
        return v

    def get_item(self, item_id: str) -> Item | None:
        """
        Get an item by ID.

        Args:
            item_id: The ID of the item to retrieve

        Returns:
            The Item object, or None if not found
        """
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def add_item(self, item: Item) -> None:
        """
        Add an item to the catalog.

        Args:
            item: The item to add

        Raises:
            ValueError: If an item with the same ID already exists
        """
        if self.get_item(item.id) is not None:
            raise ValueError(f"Item with ID '{item.id}' already exists in catalog")
        self.items.append(item)
        self.updated_at = datetime.now()

    def remove_item(self, item_id: str) -> bool:
        """
        Remove an item from the catalog.

        Args:
            item_id: The ID of the item to remove

        Returns:
            True if item was removed, False if not found
        """
        item = self.get_item(item_id)
        if item is None:
            return False
        self.items.remove(item)
        self.updated_at = datetime.now()
        return True

    def update_item(self, item_id: str, item: Item) -> bool:
        """
        Update an existing item.

        Args:
            item_id: The ID of the item to update
            item: The new item data

        Returns:
            True if item was updated, False if not found
        """
        old_item = self.get_item(item_id)
        if old_item is None:
            return False
        self.items.remove(old_item)
        self.items.append(item)
        self.updated_at = datetime.now()
        return True

    def get_items_by_attribute(self, attribute: str, value: Any) -> list[Item]:
        """
        Find all items with a specific attribute value.

        Args:
            attribute: The attribute name to filter by
            value: The value to match

        Returns:
            List of items matching the criteria
        """
        return [item for item in self.items if item.get_attribute(attribute) == value]

    def __len__(self) -> int:
        """Return the number of items in the catalog."""
        return len(self.items)
