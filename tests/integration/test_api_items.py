"""
Integration tests for Items API endpoints.

Tests cover:
- Creating items in catalogs
- Listing items with pagination
- Getting individual items
- Updating items (full and partial)
- Deleting items
- Item metadata and attributes
- Item timestamps
- Error handling (404, 409, 422)
"""



class TestCreateItem:
    """Tests for POST /catalogs/{catalog_name}/items"""

    def test_create_item_success(self, client, setup_catalog, sample_item_payload):
        """Test creating an item with valid data."""
        catalog_name = setup_catalog["name"]
        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=sample_item_payload)

        assert response.status_code == 201
        data = response.json()
        assert data["item_id"] == sample_item_payload["item_id"]
        assert data["name"] == sample_item_payload["name"]
        assert data["attributes"] == sample_item_payload["attributes"]
        assert data["catalog_name"] == catalog_name
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_item_with_metadata(self, client, setup_catalog):
        """Test creating an item with metadata."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "test_item_meta",
            "name": "Item with Metadata",
            "attributes": {"category": "shirt", "color": "blue"},
            "metadata": {"brand": "Nike", "sku": "12345"},
        }
        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["metadata"] == payload["metadata"]

    def test_create_item_without_metadata(self, client, setup_catalog):
        """Test creating an item without metadata."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "test_item_no_meta",
            "name": "Item without Metadata",
            "attributes": {"category": "shirt", "color": "red"},
        }
        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["metadata"] == {}

    def test_create_item_with_all_attribute_types(self, client, setup_catalog):
        """Test creating an item with all dimension types."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "test_item_all_types",
            "name": "Item with All Types",
            "attributes": {
                "category": "shirt",  # enum
                "color": "blue",  # string
                "size": "M",  # string (optional)
                "formality": 3,  # integer
                "price": 29.99,  # float
                "available": True,  # boolean
                "tags": ["summer", "casual"],  # list
            },
        }
        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["attributes"] == payload["attributes"]

    def test_create_duplicate_item_fails(self, client, setup_item):
        """Test creating duplicate item fails with 409."""
        catalog_name = setup_item["catalog_name"]
        payload = {
            "item_id": setup_item["item_id"],  # Duplicate ID
            "name": "Different Name",
            "attributes": {"category": "pants", "color": "black"},
        }
        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_create_item_in_nonexistent_catalog(self, client, sample_item_payload):
        """Test creating item in nonexistent catalog fails with 404."""
        response = client.post("/api/v1/catalogs/nonexistent/items", json=sample_item_payload)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_create_item_missing_required_fields(self, client, setup_catalog):
        """Test creating item without required fields fails with 422."""
        catalog_name = setup_catalog["name"]

        # Missing item_id
        response = client.post(
            f"/api/v1/catalogs/{catalog_name}/items",
            json={"name": "Test", "attributes": {}},
        )
        assert response.status_code == 422

        # Missing name
        response = client.post(
            f"/api/v1/catalogs/{catalog_name}/items",
            json={"item_id": "test", "attributes": {}},
        )
        assert response.status_code == 422

        # Missing attributes
        response = client.post(
            f"/api/v1/catalogs/{catalog_name}/items",
            json={"item_id": "test", "name": "Test"},
        )
        assert response.status_code == 422


class TestListItems:
    """Tests for GET /catalogs/{catalog_name}/items"""

    def test_list_items_empty(self, client, setup_catalog):
        """Test listing items from empty catalog returns empty list."""
        catalog_name = setup_catalog["name"]
        response = client.get(f"/api/v1/catalogs/{catalog_name}/items")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_items_single(self, client, setup_item):
        """Test listing items with single item."""
        catalog_name = setup_item["catalog_name"]
        response = client.get(f"/api/v1/catalogs/{catalog_name}/items")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["item_id"] == setup_item["item_id"]

    def test_list_items_multiple(self, client, setup_catalog, sample_item_payload):
        """Test listing multiple items."""
        catalog_name = setup_catalog["name"]

        # Create 3 items
        for i in range(3):
            payload = sample_item_payload.copy()
            payload["item_id"] = f"item_{i}"
            payload["name"] = f"Item {i}"
            response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)
            assert response.status_code == 201

        # List all items
        response = client.get(f"/api/v1/catalogs/{catalog_name}/items")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_items_pagination_skip(self, client, setup_catalog, sample_item_payload):
        """Test listing items with skip parameter."""
        catalog_name = setup_catalog["name"]

        # Create 5 items
        for i in range(5):
            payload = sample_item_payload.copy()
            payload["item_id"] = f"item_{i}"
            client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)

        # Skip first 2
        response = client.get(f"/api/v1/catalogs/{catalog_name}/items?skip=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_items_pagination_limit(self, client, setup_catalog, sample_item_payload):
        """Test listing items with limit parameter."""
        catalog_name = setup_catalog["name"]

        # Create 5 items
        for i in range(5):
            payload = sample_item_payload.copy()
            payload["item_id"] = f"item_{i}"
            client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)

        # Limit to 2
        response = client.get(f"/api/v1/catalogs/{catalog_name}/items?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_items_from_nonexistent_catalog(self, client):
        """Test listing items from nonexistent catalog fails with 404."""
        response = client.get("/api/v1/catalogs/nonexistent/items")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_list_items_includes_all_fields(self, client, setup_item):
        """Test that listed items include all required fields."""
        catalog_name = setup_item["catalog_name"]
        response = client.get(f"/api/v1/catalogs/{catalog_name}/items")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        item = data[0]
        assert "id" in item
        assert "item_id" in item
        assert "name" in item
        assert "attributes" in item
        assert "metadata" in item
        assert "catalog_name" in item
        assert "created_at" in item
        assert "updated_at" in item


class TestGetItem:
    """Tests for GET /catalogs/{catalog_name}/items/{item_id}"""

    def test_get_item_success(self, client, setup_item):
        """Test getting an item successfully."""
        catalog_name = setup_item["catalog_name"]
        item_id = setup_item["item_id"]

        response = client.get(f"/api/v1/catalogs/{catalog_name}/items/{item_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == item_id
        assert data["name"] == setup_item["name"]
        assert data["catalog_name"] == catalog_name

    def test_get_item_not_found(self, client, setup_catalog):
        """Test getting nonexistent item fails with 404."""
        catalog_name = setup_catalog["name"]

        response = client.get(f"/api/v1/catalogs/{catalog_name}/items/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_item_catalog_not_found(self, client):
        """Test getting item from nonexistent catalog fails with 404."""
        response = client.get("/api/v1/catalogs/nonexistent/items/test_item")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_item_includes_metadata(self, client, setup_catalog):
        """Test that getting item includes metadata."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "test_meta",
            "name": "Test",
            "attributes": {"category": "shirt", "color": "blue"},
            "metadata": {"brand": "Nike"},
        }
        create_response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)
        assert create_response.status_code == 201

        response = client.get(f"/api/v1/catalogs/{catalog_name}/items/test_meta")
        assert response.status_code == 200
        assert response.json()["metadata"] == payload["metadata"]

    def test_get_item_includes_attributes(self, client, setup_item):
        """Test that getting item includes attributes."""
        catalog_name = setup_item["catalog_name"]
        item_id = setup_item["item_id"]

        response = client.get(f"/api/v1/catalogs/{catalog_name}/items/{item_id}")

        assert response.status_code == 200
        data = response.json()
        assert "attributes" in data
        assert isinstance(data["attributes"], dict)


class TestUpdateItem:
    """Tests for PUT /catalogs/{catalog_name}/items/{item_id}"""

    def test_update_item_full(self, client, setup_item):
        """Test updating all item fields."""
        catalog_name = setup_item["catalog_name"]
        item_id = setup_item["item_id"]

        update_data = {
            "name": "Updated Name",
            "attributes": {"category": "pants", "color": "black"},
            "metadata": {"updated": True},
        }
        response = client.put(
            f"/api/v1/catalogs/{catalog_name}/items/{item_id}",
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["attributes"] == update_data["attributes"]
        assert data["metadata"] == update_data["metadata"]

    def test_update_item_partial_name_only(self, client, setup_item):
        """Test updating only name."""
        catalog_name = setup_item["catalog_name"]
        item_id = setup_item["item_id"]
        original_attributes = setup_item["attributes"]

        response = client.put(
            f"/api/v1/catalogs/{catalog_name}/items/{item_id}",
            json={"name": "New Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["attributes"] == original_attributes  # Unchanged

    def test_update_item_partial_attributes_only(self, client, setup_item):
        """Test updating only attributes."""
        catalog_name = setup_item["catalog_name"]
        item_id = setup_item["item_id"]
        original_name = setup_item["name"]

        new_attributes = {"category": "shoes", "color": "white"}
        response = client.put(
            f"/api/v1/catalogs/{catalog_name}/items/{item_id}",
            json={"attributes": new_attributes},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == original_name  # Unchanged
        assert data["attributes"] == new_attributes

    def test_update_item_partial_metadata_only(self, client, setup_item):
        """Test updating only metadata."""
        catalog_name = setup_item["catalog_name"]
        item_id = setup_item["item_id"]
        original_name = setup_item["name"]

        new_metadata = {"tag": "updated"}
        response = client.put(
            f"/api/v1/catalogs/{catalog_name}/items/{item_id}",
            json={"metadata": new_metadata},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == original_name  # Unchanged
        assert data["metadata"] == new_metadata

    def test_update_item_not_found(self, client, setup_catalog):
        """Test updating nonexistent item fails with 404."""
        catalog_name = setup_catalog["name"]

        response = client.put(
            f"/api/v1/catalogs/{catalog_name}/items/nonexistent",
            json={"name": "New Name"},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_item_catalog_not_found(self, client):
        """Test updating item in nonexistent catalog fails with 404."""
        response = client.put(
            "/api/v1/catalogs/nonexistent/items/test_item",
            json={"name": "New Name"},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_update_item_with_empty_body(self, client, setup_item):
        """Test updating item with empty body doesn't change anything."""
        catalog_name = setup_item["catalog_name"]
        item_id = setup_item["item_id"]

        # Get original state
        get_response = client.get(f"/api/v1/catalogs/{catalog_name}/items/{item_id}")
        original = get_response.json()

        # Update with empty body
        response = client.put(
            f"/api/v1/catalogs/{catalog_name}/items/{item_id}",
            json={},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == original["name"]
        assert data["attributes"] == original["attributes"]


class TestDeleteItem:
    """Tests for DELETE /catalogs/{catalog_name}/items/{item_id}"""

    def test_delete_item_success(self, client, setup_item):
        """Test deleting an item successfully."""
        catalog_name = setup_item["catalog_name"]
        item_id = setup_item["item_id"]

        response = client.delete(f"/api/v1/catalogs/{catalog_name}/items/{item_id}")

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

        # Verify item is deleted
        get_response = client.get(f"/api/v1/catalogs/{catalog_name}/items/{item_id}")
        assert get_response.status_code == 404

    def test_delete_item_not_found(self, client, setup_catalog):
        """Test deleting nonexistent item fails with 404."""
        catalog_name = setup_catalog["name"]

        response = client.delete(f"/api/v1/catalogs/{catalog_name}/items/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_delete_item_catalog_not_found(self, client):
        """Test deleting item from nonexistent catalog fails with 404."""
        response = client.delete("/api/v1/catalogs/nonexistent/items/test_item")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_delete_item_does_not_delete_catalog(self, client, setup_item):
        """Test that deleting item doesn't delete catalog."""
        catalog_name = setup_item["catalog_name"]
        item_id = setup_item["item_id"]

        # Delete item
        delete_response = client.delete(f"/api/v1/catalogs/{catalog_name}/items/{item_id}")
        assert delete_response.status_code == 200

        # Verify catalog still exists
        catalog_response = client.get(f"/api/v1/catalogs/{catalog_name}")
        assert catalog_response.status_code == 200


class TestItemTimestamps:
    """Tests for item timestamp fields."""

    def test_item_has_created_at(self, client, setup_item):
        """Test that item has created_at timestamp."""
        catalog_name = setup_item["catalog_name"]
        item_id = setup_item["item_id"]

        response = client.get(f"/api/v1/catalogs/{catalog_name}/items/{item_id}")

        assert response.status_code == 200
        data = response.json()
        assert "created_at" in data
        assert data["created_at"] is not None

    def test_item_has_updated_at(self, client, setup_item):
        """Test that item has updated_at timestamp."""
        catalog_name = setup_item["catalog_name"]
        item_id = setup_item["item_id"]

        response = client.get(f"/api/v1/catalogs/{catalog_name}/items/{item_id}")

        assert response.status_code == 200
        data = response.json()
        assert "updated_at" in data
        assert data["updated_at"] is not None

    def test_updated_at_changes_on_update(self, client, setup_item):
        """Test that updated_at changes when item is updated."""
        catalog_name = setup_item["catalog_name"]
        item_id = setup_item["item_id"]

        # Get original updated_at
        get_response = client.get(f"/api/v1/catalogs/{catalog_name}/items/{item_id}")
        original_updated = get_response.json()["updated_at"]

        # Update item
        update_response = client.put(
            f"/api/v1/catalogs/{catalog_name}/items/{item_id}",
            json={"name": "Updated"},
        )

        assert update_response.status_code == 200
        new_updated = update_response.json()["updated_at"]
        assert new_updated >= original_updated


class TestItemMetadata:
    """Tests for item metadata handling."""

    def test_item_metadata_preserves_types(self, client, setup_catalog):
        """Test that metadata preserves various JSON types."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "meta_test",
            "name": "Metadata Test",
            "attributes": {"category": "shirt", "color": "blue"},
            "metadata": {
                "string": "value",
                "number": 42,
                "float": 3.14,
                "boolean": True,
                "null": None,
                "array": [1, 2, 3],
                "object": {"nested": "value"},
            },
        }

        create_response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)
        assert create_response.status_code == 201

        get_response = client.get(f"/api/v1/catalogs/{catalog_name}/items/meta_test")
        assert get_response.status_code == 200
        assert get_response.json()["metadata"] == payload["metadata"]


class TestItemAttributes:
    """Tests for item attributes with different dimension types."""

    def test_item_string_attributes(self, client, setup_catalog):
        """Test item with string attributes."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "string_test",
            "name": "String Test",
            "attributes": {"category": "shirt", "color": "blue", "size": "Large"},
        }

        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)
        assert response.status_code == 201
        assert response.json()["attributes"]["size"] == "Large"

    def test_item_integer_attributes(self, client, setup_catalog):
        """Test item with integer attributes."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "int_test",
            "name": "Integer Test",
            "attributes": {"category": "shirt", "color": "blue", "formality": 5},
        }

        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)
        assert response.status_code == 201
        assert response.json()["attributes"]["formality"] == 5

    def test_item_float_attributes(self, client, setup_catalog):
        """Test item with float attributes."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "float_test",
            "name": "Float Test",
            "attributes": {"category": "shirt", "color": "blue", "price": 49.99},
        }

        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)
        assert response.status_code == 201
        assert response.json()["attributes"]["price"] == 49.99

    def test_item_boolean_attributes(self, client, setup_catalog):
        """Test item with boolean attributes."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "bool_test",
            "name": "Boolean Test",
            "attributes": {"category": "shirt", "color": "blue", "available": False},
        }

        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)
        assert response.status_code == 201
        assert response.json()["attributes"]["available"] is False

    def test_item_enum_attributes(self, client, setup_catalog):
        """Test item with enum attributes."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "enum_test",
            "name": "Enum Test",
            "attributes": {"category": "pants", "color": "black"},  # category is enum
        }

        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)
        assert response.status_code == 201
        assert response.json()["attributes"]["category"] == "pants"

    def test_item_list_attributes(self, client, setup_catalog):
        """Test item with list attributes."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "list_test",
            "name": "List Test",
            "attributes": {
                "category": "shirt",
                "color": "blue",
                "tags": ["summer", "casual", "cotton"],
            },
        }

        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)
        assert response.status_code == 201
        assert response.json()["attributes"]["tags"] == ["summer", "casual", "cotton"]

    def test_item_with_only_required_attributes(self, client, setup_catalog):
        """Test creating item with only required attributes."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "minimal_attrs",
            "name": "Minimal",
            "attributes": {"category": "shirt", "color": "blue"},  # Only required
        }

        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "category" in data["attributes"]
        assert "color" in data["attributes"]

    def test_item_with_optional_attributes(self, client, setup_catalog):
        """Test creating item with optional attributes."""
        catalog_name = setup_catalog["name"]
        payload = {
            "item_id": "optional_attrs",
            "name": "Optional",
            "attributes": {
                "category": "shirt",
                "color": "blue",
                "size": "M",  # Optional
                "formality": 3,  # Optional
                "price": 29.99,  # Optional
                "available": True,  # Optional
                "tags": ["test"],  # Optional
            },
        }

        response = client.post(f"/api/v1/catalogs/{catalog_name}/items", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["attributes"]["size"] == "M"
        assert data["attributes"]["formality"] == 3
        assert data["attributes"]["price"] == 29.99
        assert data["attributes"]["available"] is True
        assert data["attributes"]["tags"] == ["test"]
