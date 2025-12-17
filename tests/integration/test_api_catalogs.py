"""
Integration tests for Catalog API endpoints.

Tests all CRUD operations for the /api/v1/catalogs endpoints including:
- Creating catalogs with metadata
- Listing catalogs with pagination
- Getting specific catalogs
- Deleting catalogs and cascade to items
- Schema reference validation
- Error handling (404, 409, 422)
"""



class TestCreateCatalog:
    """Tests for POST /api/v1/catalogs endpoint."""

    def test_create_catalog_success(self, client, setup_schema, sample_catalog_payload):
        """Test creating a catalog with valid data."""
        response = client.post("/api/v1/catalogs", json=sample_catalog_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_catalog_payload["name"]
        assert data["description"] == sample_catalog_payload["description"]
        assert data["schema_name"] == sample_catalog_payload["schema_name"]
        assert data["metadata"] == sample_catalog_payload["metadata"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_minimal_catalog(self, client, setup_schema, minimal_catalog_payload):
        """Test creating a catalog with only required fields."""
        response = client.post("/api/v1/catalogs", json=minimal_catalog_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == minimal_catalog_payload["name"]
        assert data["description"] is None
        assert data["metadata"] == {}

    def test_create_catalog_with_nonexistent_schema(self, client):
        """Test creating catalog with non-existent schema reference fails."""
        payload = {
            "name": "orphan_catalog",
            "schema_name": "nonexistent_schema",
        }

        response = client.post("/api/v1/catalogs", json=payload)

        assert response.status_code == 404
        assert "schema" in response.json()["detail"].lower()

    def test_create_duplicate_catalog_fails(self, client, setup_schema, sample_catalog_payload):
        """Test creating duplicate catalog returns 409 Conflict."""
        # Create first catalog
        response1 = client.post("/api/v1/catalogs", json=sample_catalog_payload)
        assert response1.status_code == 201

        # Attempt to create duplicate
        response2 = client.post("/api/v1/catalogs", json=sample_catalog_payload)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"].lower()

    def test_create_catalog_with_empty_metadata(self, client, setup_schema):
        """Test creating catalog with empty metadata."""
        payload = {
            "name": "empty_metadata_catalog",
            "schema_name": setup_schema["name"],
            "metadata": {},
        }

        response = client.post("/api/v1/catalogs", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["metadata"] == {}

    def test_create_catalog_with_complex_metadata(self, client, setup_schema):
        """Test creating catalog with nested metadata."""
        payload = {
            "name": "complex_metadata_catalog",
            "schema_name": setup_schema["name"],
            "metadata": {
                "season": "summer",
                "year": 2024,
                "tags": ["casual", "formal"],
                "nested": {
                    "key1": "value1",
                    "key2": 123,
                },
            },
        }

        response = client.post("/api/v1/catalogs", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["metadata"]["season"] == "summer"
        assert data["metadata"]["year"] == 2024
        assert data["metadata"]["tags"] == ["casual", "formal"]
        assert data["metadata"]["nested"]["key1"] == "value1"

    def test_create_catalog_without_description(self, client, setup_schema):
        """Test creating catalog without description field."""
        payload = {
            "name": "no_desc_catalog",
            "schema_name": setup_schema["name"],
        }

        response = client.post("/api/v1/catalogs", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["description"] is None

    def test_create_catalog_missing_required_fields(self, client):
        """Test creating catalog without required fields fails."""
        # Missing name
        payload1 = {
            "schema_name": "test_schema",
        }
        response1 = client.post("/api/v1/catalogs", json=payload1)
        assert response1.status_code == 422

        # Missing schema_name
        payload2 = {
            "name": "test",
        }
        response2 = client.post("/api/v1/catalogs", json=payload2)
        assert response2.status_code == 422


class TestListCatalogs:
    """Tests for GET /api/v1/catalogs endpoint."""

    def test_list_catalogs_empty(self, client):
        """Test listing catalogs when database is empty."""
        response = client.get("/api/v1/catalogs")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_catalogs_single(self, client, setup_catalog):
        """Test listing catalogs with one catalog in database."""
        response = client.get("/api/v1/catalogs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == setup_catalog["name"]

    def test_list_catalogs_multiple(self, client, setup_schema, sample_catalog_payload):
        """Test listing multiple catalogs."""
        # Create 3 catalogs
        for i in range(3):
            payload = sample_catalog_payload.copy()
            payload["name"] = f"catalog_{i}"
            response = client.post("/api/v1/catalogs", json=payload)
            assert response.status_code == 201

        # List all catalogs
        response = client.get("/api/v1/catalogs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = [c["name"] for c in data]
        assert "catalog_0" in names
        assert "catalog_1" in names
        assert "catalog_2" in names

    def test_list_catalogs_pagination_skip(self, client, setup_schema, sample_catalog_payload):
        """Test listing catalogs with skip parameter."""
        # Create 5 catalogs
        for i in range(5):
            payload = sample_catalog_payload.copy()
            payload["name"] = f"catalog_{i}"
            client.post("/api/v1/catalogs", json=payload)

        # Skip first 2
        response = client.get("/api/v1/catalogs?skip=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_catalogs_pagination_limit(self, client, setup_schema, sample_catalog_payload):
        """Test listing catalogs with limit parameter."""
        # Create 5 catalogs
        for i in range(5):
            payload = sample_catalog_payload.copy()
            payload["name"] = f"catalog_{i}"
            client.post("/api/v1/catalogs", json=payload)

        # Limit to 3
        response = client.get("/api/v1/catalogs?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_catalogs_includes_schema_name(self, client, setup_catalog):
        """Test that listed catalogs include schema_name."""
        response = client.get("/api/v1/catalogs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "schema_name" in data[0]
        assert data[0]["schema_name"] == setup_catalog["schema_name"]

    def test_list_catalogs_includes_metadata(self, client, setup_catalog):
        """Test that listed catalogs include metadata."""
        response = client.get("/api/v1/catalogs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "metadata" in data[0]


class TestGetCatalog:
    """Tests for GET /api/v1/catalogs/{catalog_name} endpoint."""

    def test_get_catalog_success(self, client, setup_catalog):
        """Test getting a specific catalog by name."""
        catalog_name = setup_catalog["name"]
        response = client.get(f"/api/v1/catalogs/{catalog_name}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == catalog_name
        assert data["id"] == setup_catalog["id"]
        assert data["schema_name"] == setup_catalog["schema_name"]

    def test_get_catalog_not_found(self, client):
        """Test getting non-existent catalog returns 404."""
        response = client.get("/api/v1/catalogs/nonexistent_catalog")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_catalog_includes_metadata(self, client, setup_catalog):
        """Test that retrieved catalog includes metadata."""
        catalog_name = setup_catalog["name"]
        response = client.get(f"/api/v1/catalogs/{catalog_name}")

        assert response.status_code == 200
        data = response.json()
        assert "metadata" in data
        assert data["metadata"] == setup_catalog["metadata"]


class TestDeleteCatalog:
    """Tests for DELETE /api/v1/catalogs/{catalog_name} endpoint."""

    def test_delete_catalog_success(self, client, setup_catalog):
        """Test deleting a catalog."""
        catalog_name = setup_catalog["name"]
        response = client.delete(f"/api/v1/catalogs/{catalog_name}")

        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"].lower()

        # Verify catalog is actually deleted
        get_response = client.get(f"/api/v1/catalogs/{catalog_name}")
        assert get_response.status_code == 404

    def test_delete_catalog_not_found(self, client):
        """Test deleting non-existent catalog returns 404."""
        response = client.delete("/api/v1/catalogs/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_catalog_cascades_to_items(self, client, setup_catalog, sample_item_payload):
        """Test deleting catalog cascades to items."""
        catalog_name = setup_catalog["name"]

        # Create an item in the catalog
        item_response = client.post(
            f"/api/v1/catalogs/{catalog_name}/items",
            json=sample_item_payload,
        )
        assert item_response.status_code == 201
        item_id = item_response.json()["item_id"]

        # Delete the catalog
        delete_response = client.delete(f"/api/v1/catalogs/{catalog_name}")
        assert delete_response.status_code == 200

        # Verify item is also deleted (cascade)
        item_get = client.get(f"/api/v1/catalogs/{catalog_name}/items/{item_id}")
        assert item_get.status_code == 404

    def test_delete_catalog_with_multiple_items(self, client, setup_catalog, sample_item_payload):
        """Test deleting catalog with multiple items cascades all items."""
        catalog_name = setup_catalog["name"]

        # Create 3 items
        item_ids = []
        for i in range(3):
            payload = sample_item_payload.copy()
            payload["item_id"] = f"item_{i}"
            item_response = client.post(
                f"/api/v1/catalogs/{catalog_name}/items",
                json=payload,
            )
            assert item_response.status_code == 201
            item_ids.append(item_response.json()["item_id"])

        # Delete the catalog
        delete_response = client.delete(f"/api/v1/catalogs/{catalog_name}")
        assert delete_response.status_code == 200

        # Verify all items are deleted
        for item_id in item_ids:
            item_get = client.get(f"/api/v1/catalogs/{catalog_name}/items/{item_id}")
            assert item_get.status_code == 404

    def test_delete_catalog_does_not_delete_schema(self, client, setup_schema, setup_catalog):
        """Test deleting catalog does not delete the referenced schema."""
        schema_name = setup_schema["name"]
        catalog_name = setup_catalog["name"]

        # Delete catalog
        delete_response = client.delete(f"/api/v1/catalogs/{catalog_name}")
        assert delete_response.status_code == 200

        # Verify schema still exists
        schema_get = client.get(f"/api/v1/schemas/{schema_name}")
        assert schema_get.status_code == 200


class TestCatalogTimestamps:
    """Tests for catalog timestamp behavior."""

    def test_catalog_has_created_at(self, client, setup_schema, sample_catalog_payload):
        """Test that created catalog has created_at timestamp."""
        response = client.post("/api/v1/catalogs", json=sample_catalog_payload)
        assert response.status_code == 201
        data = response.json()
        assert "created_at" in data
        assert data["created_at"] is not None

    def test_catalog_has_updated_at(self, client, setup_schema, sample_catalog_payload):
        """Test that created catalog has updated_at timestamp."""
        response = client.post("/api/v1/catalogs", json=sample_catalog_payload)
        assert response.status_code == 201
        data = response.json()
        assert "updated_at" in data
        assert data["updated_at"] is not None


class TestCatalogMetadata:
    """Tests for catalog metadata handling."""

    def test_catalog_metadata_null_vs_empty(self, client, setup_schema):
        """Test distinction between null and empty metadata."""
        # Create catalog without metadata field (should default to empty dict)
        payload1 = {
            "name": "no_metadata",
            "schema_name": setup_schema["name"],
        }
        response1 = client.post("/api/v1/catalogs", json=payload1)
        assert response1.status_code == 201
        assert response1.json()["metadata"] == {}

        # Create catalog with explicit empty metadata
        payload2 = {
            "name": "empty_metadata",
            "schema_name": setup_schema["name"],
            "metadata": {},
        }
        response2 = client.post("/api/v1/catalogs", json=payload2)
        assert response2.status_code == 201
        assert response2.json()["metadata"] == {}

    def test_catalog_metadata_preserves_types(self, client, setup_schema):
        """Test that metadata preserves various JSON types."""
        payload = {
            "name": "typed_metadata",
            "schema_name": setup_schema["name"],
            "metadata": {
                "string": "text",
                "integer": 42,
                "float": 3.14,
                "boolean": True,
                "null": None,
                "array": [1, 2, 3],
                "object": {"nested": "value"},
            },
        }

        response = client.post("/api/v1/catalogs", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["metadata"]["string"] == "text"
        assert data["metadata"]["integer"] == 42
        assert data["metadata"]["float"] == 3.14
        assert data["metadata"]["boolean"] is True
        assert data["metadata"]["null"] is None
        assert data["metadata"]["array"] == [1, 2, 3]
        assert data["metadata"]["object"]["nested"] == "value"


class TestCatalogSchemaReference:
    """Tests for catalog schema reference validation."""

    def test_catalog_requires_existing_schema(self, client):
        """Test that catalog creation fails if schema doesn't exist."""
        payload = {
            "name": "test_catalog",
            "schema_name": "nonexistent_schema",
        }

        response = client.post("/api/v1/catalogs", json=payload)

        assert response.status_code == 404
        assert "schema" in response.json()["detail"].lower()

    def test_multiple_catalogs_same_schema(self, client, setup_schema, sample_catalog_payload):
        """Test that multiple catalogs can reference the same schema."""
        # Create first catalog
        payload1 = sample_catalog_payload.copy()
        payload1["name"] = "catalog_1"
        response1 = client.post("/api/v1/catalogs", json=payload1)
        assert response1.status_code == 201

        # Create second catalog with same schema_name
        payload2 = sample_catalog_payload.copy()
        payload2["name"] = "catalog_2"
        response2 = client.post("/api/v1/catalogs", json=payload2)
        assert response2.status_code == 201

        # Both should reference the same schema
        assert response1.json()["schema_name"] == response2.json()["schema_name"]
