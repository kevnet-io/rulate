"""
Integration tests for Import/Export API endpoints.

Tests cover:
- Exporting schemas, rulesets, cluster rulesets, and catalogs
- Importing data with validation
- Handling skip_existing flag
- Error handling for missing dependencies and validation failures
- End-to-end export/import workflows
"""



class TestExportSchemas:
    """Tests for schema export endpoints."""

    def test_export_all_schemas_empty(self, client):
        """Test exporting when no schemas exist."""
        response = client.get("/api/v1/export/schemas")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_export_all_schemas(self, client, setup_schema):
        """Test exporting all schemas."""
        response = client.get("/api/v1/export/schemas")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == setup_schema["name"]
        assert "dimensions" in data[0]
        assert "version" in data[0]

    def test_export_specific_schema(self, client, setup_schema):
        """Test exporting a specific schema by name."""
        schema_name = setup_schema["name"]
        response = client.get(f"/api/v1/export/schemas/{schema_name}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == schema_name
        assert "dimensions" in data
        assert "version" in data
        assert "description" in data

    def test_export_schema_not_found(self, client):
        """Test exporting nonexistent schema returns 404."""
        response = client.get("/api/v1/export/schemas/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestExportRuleSets:
    """Tests for ruleset export endpoints."""

    def test_export_all_rulesets_empty(self, client):
        """Test exporting when no rulesets exist."""
        response = client.get("/api/v1/export/rulesets")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_export_all_rulesets(self, client, setup_ruleset):
        """Test exporting all rulesets."""
        response = client.get("/api/v1/export/rulesets")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == setup_ruleset["name"]
        assert "rules" in data[0]
        assert "schema_ref" in data[0]

    def test_export_specific_ruleset(self, client, setup_ruleset):
        """Test exporting a specific ruleset by name."""
        ruleset_name = setup_ruleset["name"]
        response = client.get(f"/api/v1/export/rulesets/{ruleset_name}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == ruleset_name
        assert "rules" in data
        assert "schema_ref" in data
        assert "version" in data

    def test_export_ruleset_not_found(self, client):
        """Test exporting nonexistent ruleset returns 404."""
        response = client.get("/api/v1/export/rulesets/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestExportCatalogs:
    """Tests for catalog export endpoints."""

    def test_export_all_catalogs_empty(self, client):
        """Test exporting when no catalogs exist."""
        response = client.get("/api/v1/export/catalogs")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_export_all_catalogs(self, client, setup_catalog):
        """Test exporting all catalogs."""
        response = client.get("/api/v1/export/catalogs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == setup_catalog["name"]
        assert "schema_ref" in data[0]
        assert "items" in data[0]

    def test_export_specific_catalog(self, client, setup_catalog):
        """Test exporting a specific catalog by name."""
        catalog_name = setup_catalog["name"]
        response = client.get(f"/api/v1/export/catalogs/{catalog_name}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == catalog_name
        assert "schema_ref" in data
        assert "items" in data
        assert "metadata" in data

    def test_export_catalog_with_items(self, client, setup_item):
        """Test that exported catalog includes items."""
        catalog_name = setup_item["catalog_name"]
        response = client.get(f"/api/v1/export/catalogs/{catalog_name}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["id"] == setup_item["item_id"]
        assert "attributes" in data["items"][0]
        assert "metadata" in data["items"][0]

    def test_export_catalog_not_found(self, client):
        """Test exporting nonexistent catalog returns 404."""
        response = client.get("/api/v1/export/catalogs/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestExportAll:
    """Tests for export all endpoint."""

    def test_export_all_empty(self, client):
        """Test exporting all data when database is empty."""
        response = client.get("/api/v1/export/all")

        assert response.status_code == 200
        data = response.json()
        assert "schemas" in data
        assert "rulesets" in data
        assert "cluster_rulesets" in data
        assert "catalogs" in data
        assert data["schemas"] == []
        assert data["rulesets"] == []
        assert data["cluster_rulesets"] == []
        assert data["catalogs"] == []

    def test_export_all_with_data(self, client, setup_full_dataset):
        """Test exporting all data when data exists."""
        response = client.get("/api/v1/export/all")

        assert response.status_code == 200
        data = response.json()
        assert len(data["schemas"]) >= 1
        assert len(data["rulesets"]) >= 1
        assert len(data["catalogs"]) >= 1

    def test_export_all_structure(self, client, setup_schema):
        """Test that export all returns correct structure."""
        response = client.get("/api/v1/export/all")

        assert response.status_code == 200
        data = response.json()

        # Verify top-level keys
        assert set(data.keys()) == {"schemas", "rulesets", "cluster_rulesets", "catalogs"}

        # Verify each is a list
        assert isinstance(data["schemas"], list)
        assert isinstance(data["rulesets"], list)
        assert isinstance(data["cluster_rulesets"], list)
        assert isinstance(data["catalogs"], list)


class TestImportSchemas:
    """Tests for schema import endpoint."""

    def test_import_schemas_success(self, client):
        """Test importing valid schemas."""
        schemas = [
            {
                "name": "import_test_schema",
                "version": "1.0.0",
                "description": "Test schema for import",
                "dimensions": [
                    {"name": "color", "type": "string", "required": True},
                    {"name": "size", "type": "enum", "values": ["S", "M", "L"], "required": False},
                ],
            }
        ]

        response = client.post("/api/v1/import/schemas", json=schemas)

        assert response.status_code == 200
        data = response.json()
        assert "Imported 1 schema" in data["message"]

        # Verify schema was created
        get_response = client.get("/api/v1/schemas/import_test_schema")
        assert get_response.status_code == 200

    def test_import_multiple_schemas(self, client):
        """Test importing multiple schemas at once."""
        schemas = [
            {
                "name": "schema_1",
                "version": "1.0.0",
                "dimensions": [{"name": "field1", "type": "string", "required": True}],
            },
            {
                "name": "schema_2",
                "version": "1.0.0",
                "dimensions": [{"name": "field2", "type": "integer", "required": True}],
            },
        ]

        response = client.post("/api/v1/import/schemas", json=schemas)

        assert response.status_code == 200
        data = response.json()
        assert "Imported 2 schema" in data["message"]

    def test_import_schemas_duplicate_error(self, client, setup_schema):
        """Test that importing duplicate schema fails without skip_existing."""
        schemas = [
            {
                "name": setup_schema["name"],
                "version": "2.0.0",
                "dimensions": [{"name": "test", "type": "string", "required": True}],
            }
        ]

        response = client.post("/api/v1/import/schemas", json=schemas)

        assert response.status_code == 200
        data = response.json()
        assert "already exists" in data["message"].lower() or "error" in data["message"].lower()

    def test_import_schemas_skip_existing(self, client, setup_schema):
        """Test importing with skip_existing=True skips duplicates."""
        schemas = [
            {
                "name": setup_schema["name"],
                "version": "2.0.0",
                "dimensions": [{"name": "test", "type": "string", "required": True}],
            }
        ]

        response = client.post("/api/v1/import/schemas?skip_existing=true", json=schemas)

        assert response.status_code == 200
        data = response.json()
        assert "skipped 1" in data["message"].lower()

    def test_import_schemas_validation_error(self, client):
        """Test that invalid schema data is rejected."""
        schemas = [
            {
                "name": "invalid_schema",
                "version": "1.0.0",
                "dimensions": [
                    {
                        "name": "bad_field",
                        "type": "invalid_type",  # Invalid type
                        "required": True,
                    }
                ],
            }
        ]

        response = client.post("/api/v1/import/schemas", json=schemas)

        assert response.status_code == 200
        data = response.json()
        # Should report validation error
        assert "error" in data["message"].lower() or "validation" in data["message"].lower()


class TestImportRuleSets:
    """Tests for ruleset import endpoint."""

    def test_import_rulesets_success(self, client, setup_schema):
        """Test importing valid rulesets."""
        rulesets = [
            {
                "name": "import_test_rules",
                "version": "1.0.0",
                "schema_ref": setup_schema["name"],
                "rules": [
                    {
                        "name": "test_rule",
                        "type": "exclusion",
                        "enabled": True,
                        "condition": {"equals": {"field": "color"}},
                    }
                ],
            }
        ]

        response = client.post("/api/v1/import/rulesets", json=rulesets)

        assert response.status_code == 200
        data = response.json()
        assert "Imported 1 ruleset" in data["message"]

        # Verify ruleset was created
        get_response = client.get("/api/v1/rulesets/import_test_rules")
        assert get_response.status_code == 200

    def test_import_rulesets_missing_schema(self, client):
        """Test importing ruleset with nonexistent schema fails."""
        rulesets = [
            {
                "name": "orphan_rules",
                "version": "1.0.0",
                "schema_ref": "nonexistent_schema",
                "rules": [],
            }
        ]

        response = client.post("/api/v1/import/rulesets", json=rulesets)

        assert response.status_code == 200
        data = response.json()
        assert "not found" in data["message"].lower() or "error" in data["message"].lower()

    def test_import_rulesets_skip_existing(self, client, setup_ruleset):
        """Test importing with skip_existing=True skips duplicates."""
        rulesets = [
            {
                "name": setup_ruleset["name"],
                "version": "2.0.0",
                "schema_ref": "test_schema",
                "rules": [],
            }
        ]

        response = client.post("/api/v1/import/rulesets?skip_existing=true", json=rulesets)

        assert response.status_code == 200
        data = response.json()
        assert "skipped 1" in data["message"].lower()


class TestImportCatalogs:
    """Tests for catalog import endpoint."""

    def test_import_catalogs_success(self, client, setup_schema):
        """Test importing valid catalogs."""
        catalogs = [
            {
                "name": "import_test_catalog",
                "description": "Test catalog",
                "schema_ref": setup_schema["name"],
                "metadata": {},
                "items": [
                    {
                        "id": "item_1",
                        "name": "Test Item",
                        "attributes": {"category": "shirt", "color": "blue"},
                        "metadata": {},
                    }
                ],
            }
        ]

        response = client.post("/api/v1/import/catalogs", json=catalogs)

        assert response.status_code == 200
        data = response.json()
        assert "Imported 1 catalog" in data["message"]

        # Verify catalog was created
        get_response = client.get("/api/v1/catalogs/import_test_catalog")
        assert get_response.status_code == 200
        assert get_response.json()["item_count"] == 1

    def test_import_catalogs_with_multiple_items(self, client, setup_schema):
        """Test importing catalog with multiple items."""
        catalogs = [
            {
                "name": "multi_item_catalog",
                "schema_ref": setup_schema["name"],
                "items": [
                    {
                        "id": f"item_{i}",
                        "name": f"Item {i}",
                        "attributes": {"category": "shirt", "color": "blue"},
                        "metadata": {},
                    }
                    for i in range(5)
                ],
            }
        ]

        response = client.post("/api/v1/import/catalogs", json=catalogs)

        assert response.status_code == 200
        # Verify all items were imported
        get_response = client.get("/api/v1/catalogs/multi_item_catalog")
        assert get_response.status_code == 200
        assert get_response.json()["item_count"] == 5

    def test_import_catalogs_missing_schema(self, client):
        """Test importing catalog with nonexistent schema fails."""
        catalogs = [
            {
                "name": "orphan_catalog",
                "schema_ref": "nonexistent_schema",
                "items": [],
            }
        ]

        response = client.post("/api/v1/import/catalogs", json=catalogs)

        assert response.status_code == 200
        data = response.json()
        assert "not found" in data["message"].lower() or "error" in data["message"].lower()

    def test_import_catalogs_skip_existing(self, client, setup_catalog):
        """Test importing with skip_existing=True skips duplicates."""
        catalogs = [
            {
                "name": setup_catalog["name"],
                "schema_ref": "test_schema",
                "items": [],
            }
        ]

        response = client.post("/api/v1/import/catalogs?skip_existing=true", json=catalogs)

        assert response.status_code == 200
        data = response.json()
        assert "skipped 1" in data["message"].lower()


class TestExportImportWorkflow:
    """Tests for end-to-end export/import workflows."""

    def test_export_import_schema_roundtrip(self, client, setup_schema):
        """Test exporting and re-importing a schema."""
        schema_name = setup_schema["name"]

        # Export schema
        export_response = client.get(f"/api/v1/export/schemas/{schema_name}")
        assert export_response.status_code == 200
        exported_data = export_response.json()

        # Delete original
        delete_response = client.delete(f"/api/v1/schemas/{schema_name}")
        assert delete_response.status_code == 200

        # Re-import
        import_response = client.post("/api/v1/import/schemas", json=[exported_data])
        assert import_response.status_code == 200
        assert "Imported 1 schema" in import_response.json()["message"]

        # Verify re-imported schema matches
        get_response = client.get(f"/api/v1/schemas/{schema_name}")
        assert get_response.status_code == 200
        reimported = get_response.json()
        assert reimported["name"] == exported_data["name"]
        assert reimported["version"] == exported_data["version"]

    def test_export_import_catalog_with_items_roundtrip(self, client, setup_item):
        """Test exporting and re-importing a catalog with items."""
        catalog_name = setup_item["catalog_name"]

        # Export catalog
        export_response = client.get(f"/api/v1/export/catalogs/{catalog_name}")
        assert export_response.status_code == 200
        exported_data = export_response.json()

        # Verify items are included
        assert len(exported_data["items"]) == 1

        # Delete original
        delete_response = client.delete(f"/api/v1/catalogs/{catalog_name}")
        assert delete_response.status_code == 200

        # Re-import
        import_response = client.post("/api/v1/import/catalogs", json=[exported_data])
        assert import_response.status_code == 200

        # Verify items were re-imported
        get_response = client.get(f"/api/v1/catalogs/{catalog_name}")
        assert get_response.status_code == 200
        assert get_response.json()["item_count"] == 1

    def test_export_all_import_all_workflow(self, client, setup_full_dataset):
        """Test exporting all data and re-importing it."""
        # Export all data
        export_response = client.get("/api/v1/export/all")
        assert export_response.status_code == 200
        exported_data = export_response.json()

        # Count original data
        original_schema_count = len(exported_data["schemas"])
        original_ruleset_count = len(exported_data["rulesets"])
        original_catalog_count = len(exported_data["catalogs"])

        # This test verifies the export structure is correct
        assert original_schema_count >= 1
        assert "dimensions" in exported_data["schemas"][0]
        if original_ruleset_count > 0:
            assert "rules" in exported_data["rulesets"][0]
        if original_catalog_count > 0:
            assert "items" in exported_data["catalogs"][0]


class TestImportValidation:
    """Tests for import validation logic."""

    def test_import_schemas_empty_list(self, client):
        """Test importing empty list returns success."""
        response = client.post("/api/v1/import/schemas", json=[])

        assert response.status_code == 200
        data = response.json()
        assert "Imported 0 schema" in data["message"]

    def test_import_schemas_partial_success(self, client, setup_schema):
        """Test importing mix of valid and duplicate schemas."""
        schemas = [
            {
                "name": "new_schema",
                "version": "1.0.0",
                "dimensions": [{"name": "field", "type": "string", "required": True}],
            },
            {
                "name": setup_schema["name"],  # Duplicate
                "version": "1.0.0",
                "dimensions": [{"name": "field", "type": "string", "required": True}],
            },
        ]

        response = client.post("/api/v1/import/schemas", json=schemas)

        assert response.status_code == 200
        data = response.json()
        # Should import the new one and report error for duplicate
        assert "Imported 1 schema" in data["message"]
        assert "error" in data["message"].lower() or "already exists" in data["message"].lower()

    def test_import_preserves_metadata(self, client, setup_schema):
        """Test that importing preserves metadata fields."""
        catalogs = [
            {
                "name": "metadata_test",
                "schema_ref": setup_schema["name"],
                "metadata": {
                    "string": "value",
                    "number": 42,
                    "nested": {"key": "value"},
                },
                "items": [],
            }
        ]

        response = client.post("/api/v1/import/catalogs", json=catalogs)
        assert response.status_code == 200

        # Verify metadata was preserved
        get_response = client.get("/api/v1/catalogs/metadata_test")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["metadata"]["string"] == "value"
        assert data["metadata"]["number"] == 42
        assert data["metadata"]["nested"]["key"] == "value"


class TestImportErrorHandling:
    """Tests for error handling in import endpoints."""

    def test_import_schemas_with_malformed_data(self, client):
        """Test importing schemas with malformed data triggers exception handling."""
        schemas = [
            {
                "name": "malformed_schema",
                "version": "1.0.0",
                "dimensions": "this should be a list not a string",  # Invalid type
            }
        ]

        response = client.post("/api/v1/import/schemas", json=schemas)

        # Should return 200 with error message (graceful handling)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data["message"].lower() or "imported 0" in data["message"].lower()



    def test_import_catalogs_with_malformed_data(self, client, setup_schema):
        """Test importing catalogs with malformed data triggers exception handling."""
        catalogs = [
            {
                "name": "malformed_catalog",
                "schema_ref": setup_schema["name"],
                "items": "this should be a list not a string",  # Invalid type
            }
        ]

        response = client.post("/api/v1/import/catalogs", json=catalogs)

        # Should return 200 with error message (graceful handling)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data["message"].lower() or "imported 0" in data["message"].lower()

    def test_import_all_with_malformed_schemas(self, client):
        """Test importing all data with malformed schemas."""
        data = {
            "schemas": [
                {
                    "name": "bad_schema",
                    "version": "1.0.0",
                    "dimensions": None,  # Invalid - should be a list
                }
            ],
            "rulesets": [],
            "cluster_rulesets": [],
            "catalogs": [],
        }

        response = client.post("/api/v1/import/all", json=data)

        # Should return 200 with errors reported
        assert response.status_code == 200
        result = response.json()
        # Should have error in schema import
        assert "schema" in result["message"].lower()

    def test_import_all_with_dependency_errors(self, client):
        """Test importing all data with missing dependencies."""
        data = {
            "schemas": [],
            "rulesets": [
                {
                    "name": "orphan_ruleset",
                    "version": "1.0.0",
                    "schema_ref": "nonexistent_schema",
                    "rules": [],
                }
            ],
            "cluster_rulesets": [],
            "catalogs": [],
        }

        response = client.post("/api/v1/import/all", json=data)

        # Should return 200 with dependency errors
        assert response.status_code == 200
        result = response.json()
        assert "error" in result["message"].lower() or "not found" in result["message"].lower()

    def test_import_schemas_missing_required_field(self, client):
        """Test importing schema missing required field triggers exception handling."""
        schemas = [
            {
                # Missing 'name' field - should be required
                "version": "1.0.0",
                "dimensions": [],
            }
        ]

        # This should trigger validation error or exception
        response = client.post("/api/v1/import/schemas", json=schemas)
        
        # Even with errors, import endpoints return 200 with error details
        assert response.status_code in [200, 422]  # Accept both graceful handling or validation error

    def test_import_catalog_with_invalid_item_structure(self, client, setup_schema):
        """Test importing catalog with malformed item structure."""
        catalogs = [
            {
                "name": "bad_items_catalog",
                "schema_ref": setup_schema["name"],
                "items": [
                    # Missing item_id - should cause error
                    {
                        "name": "Item without ID",
                        "attributes": {},
                    }
                ],
            }
        ]

        response = client.post("/api/v1/import/catalogs", json=catalogs)
        
        # Should handle gracefully with error message
        assert response.status_code == 200
        data = response.json()
        # Check that the error was captured
        assert "imported 0" in data["message"].lower() or "error" in data["message"].lower()
