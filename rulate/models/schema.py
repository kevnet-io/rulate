"""
Schema models for defining the dimension space of a domain.

A schema defines what attributes (dimensions) objects in a catalog can have,
including their types, allowed values, and validation rules.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class DimensionType(str, Enum):
    """Valid types for dimension values."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ENUM = "enum"
    LIST = "list"


class Dimension(BaseModel):
    """
    A dimension defines a single attribute that items in a catalog can have.

    Examples:
        - name="category", type=ENUM, values=["shirt", "pants", "shoes"]
        - name="formality", type=INTEGER, min=1, max=5
        - name="colors", type=LIST, item_type="string"
    """

    name: str = Field(..., description="Unique name of the dimension")
    type: DimensionType = Field(..., description="Data type of the dimension")
    required: bool = Field(default=False, description="Whether this dimension must be present")
    description: str | None = Field(None, description="Human-readable description")

    # For ENUM type
    values: list[str] | None = Field(
        None, description="Allowed values (required for ENUM type)"
    )

    # For INTEGER/FLOAT types
    min: float | None = Field(None, description="Minimum value (for numeric types)")
    max: float | None = Field(None, description="Maximum value (for numeric types)")

    # For LIST type
    item_type: str | None = Field(None, description="Type of items in the list (for LIST type)")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure dimension name is valid."""
        if not v or not v.strip():
            raise ValueError("Dimension name cannot be empty")
        if not v.replace("_", "").isalnum():
            raise ValueError("Dimension name must be alphanumeric (underscores allowed)")
        return v

    @model_validator(mode="after")
    def validate_type_constraints(self) -> "Dimension":
        """Validate type-specific constraints."""
        if self.type == DimensionType.ENUM:
            if self.values is None:
                raise ValueError("ENUM dimension must have 'values' specified")
            if len(self.values) == 0:
                raise ValueError("ENUM dimension must have at least one value")

        if self.type in [DimensionType.INTEGER, DimensionType.FLOAT]:
            if self.min is not None and self.max is not None:
                if self.min > self.max:
                    raise ValueError("min cannot be greater than max")

        if self.type == DimensionType.LIST:
            if not self.item_type:
                raise ValueError("LIST dimension must have 'item_type' specified")
            valid_item_types = ["string", "integer", "float", "boolean"]
            if self.item_type not in valid_item_types:
                raise ValueError(f"item_type must be one of {valid_item_types}")

        return self

    def validate_value(self, value: Any) -> bool:
        """
        Validate a value against this dimension's constraints.

        Args:
            value: The value to validate

        Returns:
            True if valid, raises ValueError if not

        Raises:
            ValueError: If the value doesn't meet the dimension's constraints
        """
        if value is None:
            if self.required:
                raise ValueError(f"Dimension '{self.name}' is required but got None")
            return True

        # Type validation
        if self.type == DimensionType.STRING:
            if not isinstance(value, str):
                raise ValueError(f"Expected string for '{self.name}', got {type(value).__name__}")

        elif self.type == DimensionType.INTEGER:
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(f"Expected integer for '{self.name}', got {type(value).__name__}")
            if self.min is not None and value < self.min:
                raise ValueError(f"Value {value} is below minimum {self.min} for '{self.name}'")
            if self.max is not None and value > self.max:
                raise ValueError(f"Value {value} is above maximum {self.max} for '{self.name}'")

        elif self.type == DimensionType.FLOAT:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"Expected float for '{self.name}', got {type(value).__name__}")
            if self.min is not None and value < self.min:
                raise ValueError(f"Value {value} is below minimum {self.min} for '{self.name}'")
            if self.max is not None and value > self.max:
                raise ValueError(f"Value {value} is above maximum {self.max} for '{self.name}'")

        elif self.type == DimensionType.BOOLEAN:
            if not isinstance(value, bool):
                raise ValueError(f"Expected boolean for '{self.name}', got {type(value).__name__}")

        elif self.type == DimensionType.ENUM:
            if not isinstance(value, str):
                raise ValueError(f"Expected string for ENUM '{self.name}', got {type(value).__name__}")
            if value not in self.values:  # type: ignore
                raise ValueError(
                    f"Value '{value}' not in allowed values {self.values} for '{self.name}'"
                )

        elif self.type == DimensionType.LIST:
            if not isinstance(value, list):
                raise ValueError(f"Expected list for '{self.name}', got {type(value).__name__}")
            # Validate each item in the list
            for i, item in enumerate(value):
                if self.item_type == "string" and not isinstance(item, str):
                    raise ValueError(
                        f"Item {i} in '{self.name}' should be string, got {type(item).__name__}"
                    )
                elif self.item_type == "integer" and (
                    not isinstance(item, int) or isinstance(item, bool)
                ):
                    raise ValueError(
                        f"Item {i} in '{self.name}' should be integer, got {type(item).__name__}"
                    )
                elif self.item_type == "float" and (
                    not isinstance(item, (int, float)) or isinstance(item, bool)
                ):
                    raise ValueError(
                        f"Item {i} in '{self.name}' should be float, got {type(item).__name__}"
                    )
                elif self.item_type == "boolean" and not isinstance(item, bool):
                    raise ValueError(
                        f"Item {i} in '{self.name}' should be boolean, got {type(item).__name__}"
                    )

        return True


class Schema(BaseModel):
    """
    A schema defines the complete dimension space for a domain.

    It specifies all possible attributes that items can have and their validation rules.

    Example:
        wardrobe_schema = Schema(
            name="wardrobe_v1",
            version="1.0.0",
            dimensions=[
                Dimension(name="category", type=DimensionType.ENUM,
                         values=["shirt", "pants"], required=True),
                Dimension(name="formality", type=DimensionType.INTEGER, min=1, max=5),
            ]
        )
    """

    name: str = Field(..., description="Unique name of the schema")
    version: str = Field(..., description="Semantic version of the schema")
    description: str | None = Field(None, description="Human-readable description")
    dimensions: list[Dimension] = Field(..., description="List of dimensions in this schema")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure schema name is valid."""
        if not v or not v.strip():
            raise ValueError("Schema name cannot be empty")
        return v

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Ensure version follows semantic versioning."""
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError("Version must be in format 'major.minor.patch' (e.g., '1.0.0')")
        for part in parts:
            if not part.isdigit():
                raise ValueError("Version components must be integers")
        return v

    @model_validator(mode="after")
    def validate_unique_dimensions(self) -> "Schema":
        """Ensure all dimension names are unique."""
        dimension_names = [d.name for d in self.dimensions]
        if len(dimension_names) != len(set(dimension_names)):
            duplicates = [name for name in dimension_names if dimension_names.count(name) > 1]
            raise ValueError(f"Duplicate dimension names found: {set(duplicates)}")
        return self

    def get_dimension(self, name: str) -> Dimension | None:
        """
        Get a dimension by name.

        Args:
            name: The name of the dimension to retrieve

        Returns:
            The Dimension object, or None if not found
        """
        for dim in self.dimensions:
            if dim.name == name:
                return dim
        return None

    def validate_attributes(self, attributes: dict[str, Any]) -> bool:
        """
        Validate a dictionary of attributes against this schema.

        Args:
            attributes: Dictionary mapping dimension names to values

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        # Check for required dimensions
        for dimension in self.dimensions:
            if dimension.required and dimension.name not in attributes:
                raise ValueError(f"Required dimension '{dimension.name}' is missing")

        # Validate each provided attribute
        for attr_name, attr_value in attributes.items():
            attr_dimension = self.get_dimension(attr_name)
            if attr_dimension is None:
                raise ValueError(
                    f"Attribute '{attr_name}' is not defined in schema '{self.name}'"
                )
            attr_dimension.validate_value(attr_value)

        return True
