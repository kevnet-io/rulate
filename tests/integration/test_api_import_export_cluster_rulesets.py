"""
Integration tests for Cluster RuleSet Import/Export API endpoints.

Tests cover cluster ruleset-specific functionality that was missing from
test_api_import_export.py to achieve 100% coverage of the import_export router.
"""


class TestExportClusterRuleSets:
    """Tests for cluster ruleset export endpoints."""

    def test_export_all_cluster_rulesets_empty(self, client):
        """Test exporting when no cluster rulesets exist."""
        response = client.get("/api/v1/export/cluster-rulesets")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_export_all_cluster_rulesets(self, client, setup_schema, setup_ruleset):
        """Test exporting all cluster rulesets."""
        # Create a cluster ruleset
        cluster_ruleset = {
            "name": "test_cluster_rules",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "pairwise_ruleset_name": setup_ruleset["name"],
            "rules": [
                {
                    "name": "min_size",
                    "enabled": True,
                    "condition": {"min_cluster_size": 2},
                }
            ],
        }
        create_response = client.post("/api/v1/cluster-rulesets", json=cluster_ruleset)
        assert create_response.status_code == 201

        # Export all
        response = client.get("/api/v1/export/cluster-rulesets")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "test_cluster_rules"
        assert "schema_ref" in data[0]
        assert "pairwise_ruleset_ref" in data[0]
        assert "rules" in data[0]

    def test_export_specific_cluster_ruleset(self, client, setup_schema, setup_ruleset):
        """Test exporting a specific cluster ruleset by name."""
        # Create a cluster ruleset
        cluster_ruleset = {
            "name": "export_test_cluster",
            "version": "1.0.0",
            "description": "Test export",
            "schema_name": setup_schema["name"],
            "pairwise_ruleset_name": setup_ruleset["name"],
            "rules": [],
        }
        create_response = client.post("/api/v1/cluster-rulesets", json=cluster_ruleset)
        assert create_response.status_code == 201

        # Export specific
        response = client.get("/api/v1/export/cluster-rulesets/export_test_cluster")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "export_test_cluster"
        assert data["description"] == "Test export"
        assert data["schema_ref"] == setup_schema["name"]
        assert data["pairwise_ruleset_ref"] == setup_ruleset["name"]
        assert isinstance(data["rules"], list)

    def test_export_cluster_ruleset_not_found(self, client):
        """Test exporting nonexistent cluster ruleset returns 404."""
        response = client.get("/api/v1/export/cluster-rulesets/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestImportClusterRuleSets:
    """Tests for cluster ruleset import endpoints."""

    def test_import_cluster_rulesets_success(self, client, setup_schema, setup_ruleset):
        """Test importing cluster rulesets with valid data."""
        cluster_rulesets = [
            {
                "name": "import_test_cluster",
                "version": "1.0.0",
                "description": "Imported cluster ruleset",
                "schema_ref": setup_schema["name"],
                "pairwise_ruleset_ref": setup_ruleset["name"],
                "rules": [
                    {
                        "name": "min_size_rule",
                        "enabled": True,
                        "condition": {"min_cluster_size": 3},
                    }
                ],
            }
        ]

        response = client.post("/api/v1/import/cluster-rulesets", json=cluster_rulesets)

        assert response.status_code == 200
        data = response.json()
        assert "Imported 1 cluster ruleset" in data["message"]

        # Verify it was created
        get_response = client.get("/api/v1/cluster-rulesets/import_test_cluster")
        assert get_response.status_code == 200

    def test_import_cluster_rulesets_with_schema_name_field(
        self, client, setup_schema, setup_ruleset
    ):
        """Test importing with schema_name instead of schema_ref."""
        cluster_rulesets = [
            {
                "name": "schema_name_test",
                "version": "1.0.0",
                "schema_name": setup_schema["name"],  # Using schema_name
                "pairwise_ruleset_name": setup_ruleset["name"],  # Using pairwise_ruleset_name
                "rules": [],
            }
        ]

        response = client.post("/api/v1/import/cluster-rulesets", json=cluster_rulesets)

        assert response.status_code == 200
        assert "Imported 1 cluster ruleset" in response.json()["message"]

    def test_import_cluster_rulesets_skip_existing(self, client, setup_schema, setup_ruleset):
        """Test skip_existing flag for cluster rulesets."""
        # Create initial cluster ruleset
        cluster_ruleset = {
            "name": "skip_test_cluster",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "pairwise_ruleset_name": setup_ruleset["name"],
            "rules": [],
        }
        create_response = client.post("/api/v1/cluster-rulesets", json=cluster_ruleset)
        assert create_response.status_code == 201

        # Import with skip_existing=True
        cluster_rulesets = [cluster_ruleset]
        response = client.post(
            "/api/v1/import/cluster-rulesets?skip_existing=true", json=cluster_rulesets
        )

        assert response.status_code == 200
        data = response.json()
        assert "skipped 1" in data["message"]

    def test_import_cluster_rulesets_duplicate_error(self, client, setup_schema, setup_ruleset):
        """Test duplicate cluster ruleset without skip_existing flag."""
        # Create initial cluster ruleset
        cluster_ruleset = {
            "name": "duplicate_cluster",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "pairwise_ruleset_name": setup_ruleset["name"],
            "rules": [],
        }
        create_response = client.post("/api/v1/cluster-rulesets", json=cluster_ruleset)
        assert create_response.status_code == 201

        # Import same cluster ruleset without skip_existing
        cluster_rulesets = [cluster_ruleset]
        response = client.post("/api/v1/import/cluster-rulesets", json=cluster_rulesets)

        assert response.status_code == 200
        data = response.json()
        assert "already exists" in data["message"].lower()

    def test_import_cluster_rulesets_missing_schema(self, client, setup_ruleset):
        """Test importing cluster ruleset with missing schema dependency."""
        cluster_rulesets = [
            {
                "name": "missing_schema_cluster",
                "version": "1.0.0",
                "schema_ref": "nonexistent_schema",
                "pairwise_ruleset_ref": setup_ruleset["name"],
                "rules": [],
            }
        ]

        response = client.post("/api/v1/import/cluster-rulesets", json=cluster_rulesets)

        assert response.status_code == 200
        data = response.json()
        assert "Imported 0 cluster ruleset" in data["message"]
        assert "not found" in data["message"].lower()

    def test_import_cluster_rulesets_missing_pairwise_ruleset(self, client, setup_schema):
        """Test importing cluster ruleset with missing pairwise ruleset dependency."""
        cluster_rulesets = [
            {
                "name": "missing_pairwise_cluster",
                "version": "1.0.0",
                "schema_ref": setup_schema["name"],
                "pairwise_ruleset_ref": "nonexistent_ruleset",
                "rules": [],
            }
        ]

        response = client.post("/api/v1/import/cluster-rulesets", json=cluster_rulesets)

        assert response.status_code == 200
        data = response.json()
        assert "Imported 0 cluster ruleset" in data["message"]
        assert "not found" in data["message"].lower()

    def test_import_cluster_rulesets_with_errors_and_successes(
        self, client, setup_schema, setup_ruleset
    ):
        """Test importing mix of valid and invalid cluster rulesets."""
        cluster_rulesets = [
            {
                "name": "valid_cluster",
                "version": "1.0.0",
                "schema_ref": setup_schema["name"],
                "pairwise_ruleset_ref": setup_ruleset["name"],
                "rules": [],
            },
            {
                "name": "invalid_cluster",
                "version": "1.0.0",
                "schema_ref": "nonexistent",
                "pairwise_ruleset_ref": setup_ruleset["name"],
                "rules": [],
            },
        ]

        response = client.post("/api/v1/import/cluster-rulesets", json=cluster_rulesets)

        assert response.status_code == 200
        data = response.json()
        assert "Imported 1 cluster ruleset" in data["message"]
        assert "error" in data["message"].lower()


class TestImportExportRoundtrip:
    """Tests for end-to-end cluster ruleset export/import workflows."""

    def test_cluster_ruleset_roundtrip(self, client, setup_schema, setup_ruleset):
        """Test exporting and re-importing cluster rulesets."""
        # Create cluster ruleset
        cluster_ruleset = {
            "name": "roundtrip_cluster",
            "version": "1.0.0",
            "description": "Roundtrip test",
            "schema_name": setup_schema["name"],
            "pairwise_ruleset_name": setup_ruleset["name"],
            "rules": [
                {"name": "size_rule", "enabled": True, "condition": {"min_cluster_size": 2}}
            ],
        }
        create_response = client.post("/api/v1/cluster-rulesets", json=cluster_ruleset)
        assert create_response.status_code == 201

        # Export
        export_response = client.get("/api/v1/export/cluster-rulesets")
        assert export_response.status_code == 200
        exported_data = export_response.json()

        # Delete original
        delete_response = client.delete("/api/v1/cluster-rulesets/roundtrip_cluster")
        assert delete_response.status_code == 200

        # Re-import
        import_response = client.post("/api/v1/import/cluster-rulesets", json=exported_data)
        assert import_response.status_code == 200
        assert "Imported 1 cluster ruleset" in import_response.json()["message"]

        # Verify re-imported data
        get_response = client.get("/api/v1/cluster-rulesets/roundtrip_cluster")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["description"] == "Roundtrip test"
        assert len(data["rules"]) == 1
