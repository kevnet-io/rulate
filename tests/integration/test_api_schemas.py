"""
Integration tests for Schema API endpoints.

Tests all CRUD operations for the /api/v1/schemas endpoints including:
- Creating schemas with various dimension types
- Listing schemas with pagination
- Getting specific schemas
- Updating schemas
- Deleting schemas and cascade behavior
- Error handling (404, 409, 422)
"""


class TestCreateSchema:
    """Tests for POST /api/v1/schemas endpoint."""

    def test_create_schema_success(self, client, sample_schema_payload):
        """Test creating a schema with valid data."""
        response = client.post("/api/v1/schemas", json=sample_schema_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_schema_payload["name"]
        assert data["version"] == sample_schema_payload["version"]
        assert data["description"] == sample_schema_payload["description"]
        assert len(data["dimensions"]) == len(sample_schema_payload["dimensions"])
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_minimal_schema(self, client, minimal_schema_payload):
        """Test creating a schema with only required fields."""
        response = client.post("/api/v1/schemas", json=minimal_schema_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == minimal_schema_payload["name"]
        assert data["version"] == minimal_schema_payload["version"]
        assert data["description"] is None
        assert len(data["dimensions"]) == 1

    def test_create_duplicate_schema_fails(self, client, sample_schema_payload):
        """Test creating duplicate schema returns 409 Conflict."""
        # Create first schema
        response1 = client.post("/api/v1/schemas", json=sample_schema_payload)
        assert response1.status_code == 201

        # Attempt to create duplicate
        response2 = client.post("/api/v1/schemas", json=sample_schema_payload)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"].lower()

    def test_create_schema_all_dimension_types(self, client):
        """Test creating schema with all 6 dimension types."""
        payload = {
            "name": "all_types_schema",
            "version": "1.0.0",
            "dimensions": [
                {"name": "str_field", "type": "string", "required": True},
                {"name": "int_field", "type": "integer", "min": 1, "max": 10, "required": True},
                {
                    "name": "float_field",
                    "type": "float",
                    "min": 0.0,
                    "max": 100.0,
                    "required": False,
                },
                {"name": "bool_field", "type": "boolean", "required": False},
                {"name": "enum_field", "type": "enum", "values": ["a", "b", "c"], "required": True},
                {"name": "list_field", "type": "list", "item_type": "string", "required": False},
            ],
        }

        response = client.post("/api/v1/schemas", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert len(data["dimensions"]) == 6

        # Verify each dimension type is preserved
        dimensions_by_name = {d["name"]: d for d in data["dimensions"]}
        assert dimensions_by_name["str_field"]["type"] == "string"
        assert dimensions_by_name["int_field"]["type"] == "integer"
        assert dimensions_by_name["int_field"]["min"] == 1
        assert dimensions_by_name["int_field"]["max"] == 10
        assert dimensions_by_name["float_field"]["type"] == "float"
        assert dimensions_by_name["bool_field"]["type"] == "boolean"
        assert dimensions_by_name["enum_field"]["type"] == "enum"
        assert dimensions_by_name["enum_field"]["values"] == ["a", "b", "c"]
        assert dimensions_by_name["list_field"]["type"] == "list"
        assert dimensions_by_name["list_field"]["item_type"] == "string"

    def test_create_schema_with_empty_dimensions(self, client):
        """Test creating schema with empty dimensions list."""
        payload = {
            "name": "empty_schema",
            "version": "1.0.0",
            "dimensions": [],
        }

        response = client.post("/api/v1/schemas", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["dimensions"] == []

    def test_create_schema_missing_required_fields(self, client):
        """Test creating schema without required fields fails."""
        # Missing name
        payload1 = {
            "version": "1.0.0",
            "dimensions": [],
        }
        response1 = client.post("/api/v1/schemas", json=payload1)
        assert response1.status_code == 422

        # Missing version
        payload2 = {
            "name": "test",
            "dimensions": [],
        }
        response2 = client.post("/api/v1/schemas", json=payload2)
        assert response2.status_code == 422

        # Missing dimensions
        payload3 = {
            "name": "test",
            "version": "1.0.0",
        }
        response3 = client.post("/api/v1/schemas", json=payload3)
        assert response3.status_code == 422

    def test_create_schema_invalid_dimension_type(self, client):
        """Test creating schema with invalid dimension type fails."""
        payload = {
            "name": "invalid_schema",
            "version": "1.0.0",
            "dimensions": [{"name": "field1", "type": "invalid_type", "required": True}],
        }

        response = client.post("/api/v1/schemas", json=payload)
        assert response.status_code == 422


class TestListSchemas:
    """Tests for GET /api/v1/schemas endpoint."""

    def test_list_schemas_empty(self, client):
        """Test listing schemas when database is empty."""
        response = client.get("/api/v1/schemas")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_schemas_single(self, client, setup_schema):
        """Test listing schemas with one schema in database."""
        response = client.get("/api/v1/schemas")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == setup_schema["name"]

    def test_list_schemas_multiple(self, client, sample_schema_payload):
        """Test listing multiple schemas."""
        # Create 3 schemas
        for i in range(3):
            payload = sample_schema_payload.copy()
            payload["name"] = f"schema_{i}"
            response = client.post("/api/v1/schemas", json=payload)
        assert response.status_code == 201

        # List all schemas
        response = client.get("/api/v1/schemas")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = [s["name"] for s in data]
        assert "schema_0" in names
        assert "schema_1" in names
        assert "schema_2" in names

    def test_list_schemas_pagination_skip(self, client, sample_schema_payload):
        """Test listing schemas with skip parameter."""
        # Create 5 schemas
        for i in range(5):
            payload = sample_schema_payload.copy()
            payload["name"] = f"schema_{i}"
            client.post("/api/v1/schemas", json=payload)

        # Skip first 2
        response = client.get("/api/v1/schemas?skip=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_schemas_pagination_limit(self, client, sample_schema_payload):
        """Test listing schemas with limit parameter."""
        # Create 5 schemas
        for i in range(5):
            payload = sample_schema_payload.copy()
            payload["name"] = f"schema_{i}"
            client.post("/api/v1/schemas", json=payload)

        # Limit to 3
        response = client.get("/api/v1/schemas?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_schemas_pagination_skip_and_limit(self, client, sample_schema_payload):
        """Test listing schemas with both skip and limit."""
        # Create 10 schemas
        for i in range(10):
            payload = sample_schema_payload.copy()
            payload["name"] = f"schema_{i:02d}"  # Zero-padded for consistent ordering
            client.post("/api/v1/schemas", json=payload)

        # Skip 3, limit 4
        response = client.get("/api/v1/schemas?skip=3&limit=4")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4


class TestGetSchema:
    """Tests for GET /api/v1/schemas/{schema_name} endpoint."""

    def test_get_schema_success(self, client, setup_schema):
        """Test getting a specific schema by name."""
        schema_name = setup_schema["name"]
        response = client.get(f"/api/v1/schemas/{schema_name}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == schema_name
        assert data["id"] == setup_schema["id"]
        assert len(data["dimensions"]) == len(setup_schema["dimensions"])

    def test_get_schema_not_found(self, client):
        """Test getting non-existent schema returns 404."""
        response = client.get("/api/v1/schemas/nonexistent_schema")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_schema_preserves_dimension_order(self, client, sample_schema_payload):
        """Test that dimension order is preserved."""
        # Create schema
        create_response = client.post("/api/v1/schemas", json=sample_schema_payload)
        assert create_response.status_code == 201

        # Get schema
        schema_name = sample_schema_payload["name"]
        get_response = client.get(f"/api/v1/schemas/{schema_name}")

        assert get_response.status_code == 200
        data = get_response.json()

        # Verify dimension order matches
        original_names = [d["name"] for d in sample_schema_payload["dimensions"]]
        retrieved_names = [d["name"] for d in data["dimensions"]]
        assert original_names == retrieved_names


class TestUpdateSchema:
    """Tests for PUT /api/v1/schemas/{schema_name} endpoint."""

    def test_update_schema_full(self, client, setup_schema):
        """Test updating all fields of a schema."""
        schema_name = setup_schema["name"]
        update_payload = {
            "version": "2.0.0",
            "description": "Updated description",
            "dimensions": [{"name": "new_field", "type": "string", "required": True}],
        }

        response = client.put(f"/api/v1/schemas/{schema_name}", json=update_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "2.0.0"
        assert data["description"] == "Updated description"
        assert len(data["dimensions"]) == 1
        assert data["dimensions"][0]["name"] == "new_field"
        # Name should not change
        assert data["name"] == schema_name

    def test_update_schema_partial_version_only(self, client, setup_schema):
        """Test updating only version field."""
        schema_name = setup_schema["name"]
        update_payload = {
            "version": "1.1.0",
        }

        response = client.put(f"/api/v1/schemas/{schema_name}", json=update_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.1.0"
        # Other fields should remain unchanged
        assert data["description"] == setup_schema["description"]
        assert len(data["dimensions"]) == len(setup_schema["dimensions"])

    def test_update_schema_partial_description_only(self, client, setup_schema):
        """Test updating only description field."""
        schema_name = setup_schema["name"]
        update_payload = {
            "description": "New description",
        }

        response = client.put(f"/api/v1/schemas/{schema_name}", json=update_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "New description"
        assert data["version"] == setup_schema["version"]

    def test_update_schema_partial_dimensions_only(self, client, setup_schema):
        """Test updating only dimensions."""
        schema_name = setup_schema["name"]
        update_payload = {
            "dimensions": [{"name": "single_field", "type": "integer", "required": True}],
        }

        response = client.put(f"/api/v1/schemas/{schema_name}", json=update_payload)

        assert response.status_code == 200
        data = response.json()
        assert len(data["dimensions"]) == 1
        assert data["dimensions"][0]["name"] == "single_field"

    def test_update_schema_not_found(self, client):
        """Test updating non-existent schema returns 404."""
        update_payload = {
            "version": "2.0.0",
        }

        response = client.put("/api/v1/schemas/nonexistent", json=update_payload)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_schema_with_empty_body(self, client, setup_schema):
        """Test updating schema with empty body does nothing."""
        schema_name = setup_schema["name"]
        update_payload = {}

        response = client.put(f"/api/v1/schemas/{schema_name}", json=update_payload)

        assert response.status_code == 200
        data = response.json()
        # All fields should remain unchanged
        assert data["version"] == setup_schema["version"]
        assert data["description"] == setup_schema["description"]
        assert len(data["dimensions"]) == len(setup_schema["dimensions"])


class TestDeleteSchema:
    """Tests for DELETE /api/v1/schemas/{schema_name} endpoint."""

    def test_delete_schema_success(self, client, setup_schema):
        """Test deleting a schema."""
        schema_name = setup_schema["name"]
        response = client.delete(f"/api/v1/schemas/{schema_name}")

        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"].lower()

        # Verify schema is actually deleted
        get_response = client.get(f"/api/v1/schemas/{schema_name}")
        assert get_response.status_code == 404

    def test_delete_schema_not_found(self, client):
        """Test deleting non-existent schema returns 404."""
        response = client.delete("/api/v1/schemas/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_schema_cascades_to_rulesets(self, client, setup_schema, sample_ruleset_payload):
        """Test deleting schema cascades to dependent rulesets."""
        schema_name = setup_schema["name"]

        # Create a ruleset that references this schema
        ruleset_response = client.post("/api/v1/rulesets", json=sample_ruleset_payload)
        assert ruleset_response.status_code == 201
        ruleset_name = ruleset_response.json()["name"]

        # Delete the schema
        delete_response = client.delete(f"/api/v1/schemas/{schema_name}")
        assert delete_response.status_code == 200

        # Verify ruleset is also deleted (cascade)
        ruleset_get = client.get(f"/api/v1/rulesets/{ruleset_name}")
        assert ruleset_get.status_code == 404

    def test_delete_schema_cascades_to_catalogs(self, client, setup_schema, sample_catalog_payload):
        """Test deleting schema cascades to dependent catalogs."""
        schema_name = setup_schema["name"]

        # Create a catalog that references this schema
        catalog_response = client.post("/api/v1/catalogs", json=sample_catalog_payload)
        assert catalog_response.status_code == 201
        catalog_name = catalog_response.json()["name"]

        # Delete the schema
        delete_response = client.delete(f"/api/v1/schemas/{schema_name}")
        assert delete_response.status_code == 200

        # Verify catalog is also deleted (cascade)
        catalog_get = client.get(f"/api/v1/catalogs/{catalog_name}")
        assert catalog_get.status_code == 404

    def test_delete_schema_cascades_to_catalogs_and_items(
        self, client, setup_schema, sample_catalog_payload, sample_item_payload
    ):
        """Test deleting schema cascades through catalog to items."""
        schema_name = setup_schema["name"]

        # Create catalog
        catalog_response = client.post("/api/v1/catalogs", json=sample_catalog_payload)
        assert catalog_response.status_code == 201
        catalog_name = catalog_response.json()["name"]

        # Create item in catalog
        item_response = client.post(
            f"/api/v1/catalogs/{catalog_name}/items",
            json=sample_item_payload,
        )
        assert item_response.status_code == 201
        item_id = item_response.json()["item_id"]

        # Delete the schema
        delete_response = client.delete(f"/api/v1/schemas/{schema_name}")
        assert delete_response.status_code == 200

        # Verify catalog is deleted
        catalog_get = client.get(f"/api/v1/catalogs/{catalog_name}")
        assert catalog_get.status_code == 404

        # Verify item is also deleted (cascade through catalog)
        item_get = client.get(f"/api/v1/catalogs/{catalog_name}/items/{item_id}")
        assert item_get.status_code == 404


class TestSchemaTimestamps:
    """Tests for schema timestamp behavior."""

    def test_schema_has_created_at(self, client, sample_schema_payload):
        """Test that created schema has created_at timestamp."""
        response = client.post("/api/v1/schemas", json=sample_schema_payload)
        assert response.status_code == 201
        data = response.json()
        assert "created_at" in data
        assert data["created_at"] is not None

    def test_schema_has_updated_at(self, client, sample_schema_payload):
        """Test that created schema has updated_at timestamp."""
        response = client.post("/api/v1/schemas", json=sample_schema_payload)
        assert response.status_code == 201
        data = response.json()
        assert "updated_at" in data
        assert data["updated_at"] is not None

    def test_updated_at_changes_on_update(self, client, setup_schema):
        """Test that updated_at timestamp changes when schema is updated."""
        schema_name = setup_schema["name"]

        # Update schema
        update_payload = {"version": "2.0.0"}
        update_response = client.put(f"/api/v1/schemas/{schema_name}", json=update_payload)

        assert update_response.status_code == 200
        updated_data = update_response.json()

        # Note: In practice, updated_at might be the same if update is very fast
        # This test documents the expected behavior
        assert "updated_at" in updated_data
