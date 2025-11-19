"""
Tests for schema models and validation.
"""

import pytest
from pydantic import ValidationError

from rulate.models.schema import Dimension, DimensionType, Schema


class TestDimensionType:
    """Tests for DimensionType enum."""

    def test_dimension_types_exist(self):
        """Test that all expected dimension types are defined."""
        assert DimensionType.STRING == "string"
        assert DimensionType.INTEGER == "integer"
        assert DimensionType.FLOAT == "float"
        assert DimensionType.BOOLEAN == "boolean"
        assert DimensionType.ENUM == "enum"
        assert DimensionType.LIST == "list"


class TestDimension:
    """Tests for Dimension model."""

    def test_create_string_dimension(self):
        """Test creating a simple string dimension."""
        dim = Dimension(name="description", type=DimensionType.STRING)
        assert dim.name == "description"
        assert dim.type == DimensionType.STRING
        assert dim.required is False

    def test_create_required_dimension(self):
        """Test creating a required dimension."""
        dim = Dimension(name="category", type=DimensionType.STRING, required=True)
        assert dim.required is True

    def test_create_enum_dimension(self):
        """Test creating an ENUM dimension."""
        dim = Dimension(
            name="category",
            type=DimensionType.ENUM,
            values=["shirt", "pants", "shoes"],
            required=True,
        )
        assert dim.values == ["shirt", "pants", "shoes"]

    def test_enum_dimension_requires_values(self):
        """Test that ENUM dimensions must have values."""
        with pytest.raises(ValidationError, match="ENUM dimension must have 'values'"):
            Dimension(name="category", type=DimensionType.ENUM)

    def test_enum_dimension_requires_non_empty_values(self):
        """Test that ENUM dimensions must have at least one value."""
        with pytest.raises(ValidationError, match="must have at least one value"):
            Dimension(name="category", type=DimensionType.ENUM, values=[])

    def test_create_integer_dimension_with_range(self):
        """Test creating an INTEGER dimension with min/max."""
        dim = Dimension(name="formality", type=DimensionType.INTEGER, min=1, max=5)
        assert dim.min == 1
        assert dim.max == 5

    def test_integer_dimension_min_less_than_max(self):
        """Test that min cannot be greater than max."""
        with pytest.raises(ValidationError, match="min cannot be greater than max"):
            Dimension(name="formality", type=DimensionType.INTEGER, min=5, max=1)

    def test_create_list_dimension(self):
        """Test creating a LIST dimension."""
        dim = Dimension(name="colors", type=DimensionType.LIST, item_type="string")
        assert dim.item_type == "string"

    def test_list_dimension_requires_item_type(self):
        """Test that LIST dimensions must have item_type."""
        with pytest.raises(ValidationError, match="LIST dimension must have 'item_type'"):
            Dimension(name="colors", type=DimensionType.LIST)

    def test_list_dimension_validates_item_type(self):
        """Test that LIST dimensions validate item_type."""
        with pytest.raises(ValidationError, match="item_type must be one of"):
            Dimension(name="colors", type=DimensionType.LIST, item_type="invalid")

    def test_dimension_name_validation_empty(self):
        """Test that dimension names cannot be empty."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            Dimension(name="", type=DimensionType.STRING)

    def test_dimension_name_validation_invalid_chars(self):
        """Test that dimension names must be alphanumeric."""
        with pytest.raises(ValidationError, match="must be alphanumeric"):
            Dimension(name="my-dimension!", type=DimensionType.STRING)

    def test_dimension_name_with_underscores(self):
        """Test that dimension names can have underscores."""
        dim = Dimension(name="body_zone", type=DimensionType.STRING)
        assert dim.name == "body_zone"


class TestDimensionValueValidation:
    """Tests for Dimension.validate_value() method."""

    def test_validate_string_value(self):
        """Test validating a string value."""
        dim = Dimension(name="description", type=DimensionType.STRING)
        assert dim.validate_value("A blue shirt") is True

    def test_validate_string_type_mismatch(self):
        """Test validating wrong type for string dimension."""
        dim = Dimension(name="description", type=DimensionType.STRING)
        with pytest.raises(ValueError, match="Expected string"):
            dim.validate_value(123)

    def test_validate_integer_value(self):
        """Test validating an integer value."""
        dim = Dimension(name="formality", type=DimensionType.INTEGER, min=1, max=5)
        assert dim.validate_value(3) is True

    def test_validate_integer_below_min(self):
        """Test validating integer below minimum."""
        dim = Dimension(name="formality", type=DimensionType.INTEGER, min=1, max=5)
        with pytest.raises(ValueError, match="below minimum"):
            dim.validate_value(0)

    def test_validate_integer_above_max(self):
        """Test validating integer above maximum."""
        dim = Dimension(name="formality", type=DimensionType.INTEGER, min=1, max=5)
        with pytest.raises(ValueError, match="above maximum"):
            dim.validate_value(6)

    def test_validate_integer_type_mismatch(self):
        """Test validating wrong type for integer dimension."""
        dim = Dimension(name="formality", type=DimensionType.INTEGER)
        with pytest.raises(ValueError, match="Expected integer"):
            dim.validate_value("not a number")

    def test_validate_integer_rejects_boolean(self):
        """Test that boolean is not accepted as integer."""
        dim = Dimension(name="count", type=DimensionType.INTEGER)
        with pytest.raises(ValueError, match="Expected integer"):
            dim.validate_value(True)

    def test_validate_float_value(self):
        """Test validating a float value."""
        dim = Dimension(name="price", type=DimensionType.FLOAT, min=0.0)
        assert dim.validate_value(19.99) is True
        assert dim.validate_value(20) is True  # int is acceptable for float

    def test_validate_float_below_min(self):
        """Test validating float below minimum."""
        dim = Dimension(name="price", type=DimensionType.FLOAT, min=0.0)
        with pytest.raises(ValueError, match="below minimum"):
            dim.validate_value(-1.0)

    def test_validate_boolean_value(self):
        """Test validating a boolean value."""
        dim = Dimension(name="active", type=DimensionType.BOOLEAN)
        assert dim.validate_value(True) is True
        assert dim.validate_value(False) is True

    def test_validate_boolean_type_mismatch(self):
        """Test validating wrong type for boolean dimension."""
        dim = Dimension(name="active", type=DimensionType.BOOLEAN)
        with pytest.raises(ValueError, match="Expected boolean"):
            dim.validate_value("yes")

    def test_validate_enum_value(self):
        """Test validating an enum value."""
        dim = Dimension(name="category", type=DimensionType.ENUM, values=["shirt", "pants"])
        assert dim.validate_value("shirt") is True

    def test_validate_enum_invalid_value(self):
        """Test validating invalid enum value."""
        dim = Dimension(name="category", type=DimensionType.ENUM, values=["shirt", "pants"])
        with pytest.raises(ValueError, match="not in allowed values"):
            dim.validate_value("shoes")

    def test_validate_list_value(self):
        """Test validating a list value."""
        dim = Dimension(name="colors", type=DimensionType.LIST, item_type="string")
        assert dim.validate_value(["blue", "red"]) is True

    def test_validate_list_empty(self):
        """Test validating an empty list."""
        dim = Dimension(name="colors", type=DimensionType.LIST, item_type="string")
        assert dim.validate_value([]) is True

    def test_validate_list_invalid_item_type(self):
        """Test validating list with wrong item type."""
        dim = Dimension(name="colors", type=DimensionType.LIST, item_type="string")
        with pytest.raises(ValueError, match="should be string"):
            dim.validate_value(["blue", 123])

    def test_validate_required_dimension_missing(self):
        """Test that required dimensions reject None."""
        dim = Dimension(name="category", type=DimensionType.STRING, required=True)
        with pytest.raises(ValueError, match="is required"):
            dim.validate_value(None)

    def test_validate_optional_dimension_missing(self):
        """Test that optional dimensions accept None."""
        dim = Dimension(name="description", type=DimensionType.STRING, required=False)
        assert dim.validate_value(None) is True


class TestSchema:
    """Tests for Schema model."""

    def test_create_simple_schema(self):
        """Test creating a simple schema."""
        schema = Schema(
            name="test_schema",
            version="1.0.0",
            dimensions=[
                Dimension(name="category", type=DimensionType.STRING, required=True),
                Dimension(name="formality", type=DimensionType.INTEGER, min=1, max=5),
            ],
        )
        assert schema.name == "test_schema"
        assert schema.version == "1.0.0"
        assert len(schema.dimensions) == 2

    def test_schema_name_validation(self):
        """Test that schema names cannot be empty."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            Schema(name="", version="1.0.0", dimensions=[])

    def test_schema_version_validation_format(self):
        """Test that schema versions must follow semver."""
        with pytest.raises(ValidationError, match="major.minor.patch"):
            Schema(name="test", version="1.0", dimensions=[])

    def test_schema_version_validation_non_numeric(self):
        """Test that schema versions must be numeric."""
        with pytest.raises(ValidationError, match="must be integers"):
            Schema(name="test", version="1.0.a", dimensions=[])

    def test_schema_unique_dimension_names(self):
        """Test that dimension names must be unique."""
        with pytest.raises(ValidationError, match="Duplicate dimension names"):
            Schema(
                name="test",
                version="1.0.0",
                dimensions=[
                    Dimension(name="category", type=DimensionType.STRING),
                    Dimension(name="category", type=DimensionType.INTEGER),
                ],
            )

    def test_get_dimension(self):
        """Test getting a dimension by name."""
        schema = Schema(
            name="test",
            version="1.0.0",
            dimensions=[
                Dimension(name="category", type=DimensionType.STRING),
                Dimension(name="formality", type=DimensionType.INTEGER),
            ],
        )
        dim = schema.get_dimension("category")
        assert dim is not None
        assert dim.name == "category"

    def test_get_dimension_not_found(self):
        """Test getting a non-existent dimension."""
        schema = Schema(name="test", version="1.0.0", dimensions=[])
        dim = schema.get_dimension("nonexistent")
        assert dim is None


class TestSchemaValidateAttributes:
    """Tests for Schema.validate_attributes() method."""

    def test_validate_valid_attributes(self):
        """Test validating valid attributes."""
        schema = Schema(
            name="test",
            version="1.0.0",
            dimensions=[
                Dimension(name="category", type=DimensionType.STRING, required=True),
                Dimension(name="formality", type=DimensionType.INTEGER, min=1, max=5),
            ],
        )
        attributes = {"category": "shirt", "formality": 3}
        assert schema.validate_attributes(attributes) is True

    def test_validate_missing_required_dimension(self):
        """Test validating attributes missing required dimension."""
        schema = Schema(
            name="test",
            version="1.0.0",
            dimensions=[
                Dimension(name="category", type=DimensionType.STRING, required=True),
            ],
        )
        attributes = {"formality": 3}
        with pytest.raises(ValueError, match="Required dimension 'category' is missing"):
            schema.validate_attributes(attributes)

    def test_validate_undefined_attribute(self):
        """Test validating attributes with undefined dimension."""
        schema = Schema(
            name="test",
            version="1.0.0",
            dimensions=[
                Dimension(name="category", type=DimensionType.STRING),
            ],
        )
        attributes = {"category": "shirt", "undefined": "value"}
        with pytest.raises(ValueError, match="not defined in schema"):
            schema.validate_attributes(attributes)

    def test_validate_optional_dimension_missing(self):
        """Test that optional dimensions can be omitted."""
        schema = Schema(
            name="test",
            version="1.0.0",
            dimensions=[
                Dimension(name="category", type=DimensionType.STRING, required=True),
                Dimension(name="formality", type=DimensionType.INTEGER, required=False),
            ],
        )
        attributes = {"category": "shirt"}
        assert schema.validate_attributes(attributes) is True

    def test_validate_invalid_value_type(self):
        """Test validating attributes with wrong type."""
        schema = Schema(
            name="test",
            version="1.0.0",
            dimensions=[
                Dimension(name="formality", type=DimensionType.INTEGER, min=1, max=5),
            ],
        )
        attributes = {"formality": "high"}
        with pytest.raises(ValueError, match="Expected integer"):
            schema.validate_attributes(attributes)
