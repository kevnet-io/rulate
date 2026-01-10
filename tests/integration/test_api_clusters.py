"""
Integration tests for Clusters API endpoints.

Tests cover:
- ClusterRuleSet CRUD operations
- Cluster evaluation endpoint
- Error handling and validation
"""


class TestCreateClusterRuleSet:
    """Tests for POST /cluster-rulesets"""

    def test_create_cluster_ruleset_success(self, client, setup_schema, setup_ruleset):
        """Test creating a cluster ruleset with valid data."""
        payload = {
            "name": "test_cluster_rules",
            "version": "1.0.0",
            "description": "Test cluster ruleset",
            "schema_name": setup_schema["name"],
            "pairwise_ruleset_name": setup_ruleset["name"],
            "rules": [
                {
                    "name": "min_size",
                    "type": "requirement",
                    "enabled": True,
                    "condition": {"has_item_with": {"field": "category", "value": "shirt"}},
                }
            ],
        }

        response = client.post("/api/v1/cluster-rulesets", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["version"] == payload["version"]
        assert data["schema_name"] == setup_schema["name"]
        assert data["pairwise_ruleset_name"] == setup_ruleset["name"]
        assert "id" in data
        assert "created_at" in data

    def test_create_cluster_ruleset_minimal(self, client, setup_schema, setup_ruleset):
        """Test creating cluster ruleset with minimal data."""
        payload = {
            "name": "minimal_cluster_rules",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "pairwise_ruleset_name": setup_ruleset["name"],
            "rules": [],
        }

        response = client.post("/api/v1/cluster-rulesets", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["rules"] == []

    def test_create_cluster_ruleset_duplicate_fails(self, client, setup_schema, setup_ruleset):
        """Test creating duplicate cluster ruleset fails with 409."""
        payload = {
            "name": "duplicate_cluster",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "pairwise_ruleset_name": setup_ruleset["name"],
            "rules": [],
        }

        # Create first one
        response1 = client.post("/api/v1/cluster-rulesets", json=payload)
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = client.post("/api/v1/cluster-rulesets", json=payload)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]

    def test_create_cluster_ruleset_missing_schema(self, client, setup_ruleset):
        """Test creating cluster ruleset with nonexistent schema fails."""
        payload = {
            "name": "orphan_cluster",
            "version": "1.0.0",
            "schema_name": "nonexistent_schema",
            "pairwise_ruleset_name": setup_ruleset["name"],
            "rules": [],
        }

        response = client.post("/api/v1/cluster-rulesets", json=payload)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_cluster_ruleset_missing_pairwise_ruleset(self, client, setup_schema):
        """Test creating cluster ruleset with nonexistent pairwise ruleset fails."""
        payload = {
            "name": "orphan_cluster",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "pairwise_ruleset_name": "nonexistent_ruleset",
            "rules": [],
        }

        response = client.post("/api/v1/cluster-rulesets", json=payload)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_cluster_ruleset_missing_required_fields(self, client):
        """Test creating cluster ruleset without required fields fails."""
        # Missing name
        response = client.post(
            "/api/v1/cluster-rulesets",
            json={
                "version": "1.0.0",
                "schema_name": "test",
                "pairwise_ruleset_name": "test",
                "rules": [],
            },
        )
        assert response.status_code == 422

        # Missing version
        response = client.post(
            "/api/v1/cluster-rulesets",
            json={
                "name": "test",
                "schema_name": "test",
                "pairwise_ruleset_name": "test",
                "rules": [],
            },
        )
        assert response.status_code == 422


class TestListClusterRuleSets:
    """Tests for GET /cluster-rulesets"""

    def test_list_cluster_rulesets_empty(self, client):
        """Test listing cluster rulesets when none exist."""
        response = client.get("/api/v1/cluster-rulesets")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_cluster_rulesets_single(self, client, setup_schema, setup_ruleset):
        """Test listing single cluster ruleset."""
        # Create cluster ruleset
        create_response = client.post(
            "/api/v1/cluster-rulesets",
            json={
                "name": "list_test",
                "version": "1.0.0",
                "schema_name": setup_schema["name"],
                "pairwise_ruleset_name": setup_ruleset["name"],
                "rules": [],
            },
        )
        assert create_response.status_code == 201

        # List
        response = client.get("/api/v1/cluster-rulesets")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "list_test"

    def test_list_cluster_rulesets_multiple(self, client, setup_schema, setup_ruleset):
        """Test listing multiple cluster rulesets."""
        # Create 3 cluster rulesets
        for i in range(3):
            response = client.post(
                "/api/v1/cluster-rulesets",
                json={
                    "name": f"cluster_{i}",
                    "version": "1.0.0",
                    "schema_name": setup_schema["name"],
                    "pairwise_ruleset_name": setup_ruleset["name"],
                    "rules": [],
                },
            )
            assert response.status_code == 201

        # List
        response = client.get("/api/v1/cluster-rulesets")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_cluster_rulesets_pagination(self, client, setup_schema, setup_ruleset):
        """Test listing with pagination."""
        # Create 5 cluster rulesets
        for i in range(5):
            client.post(
                "/api/v1/cluster-rulesets",
                json={
                    "name": f"cluster_{i}",
                    "version": "1.0.0",
                    "schema_name": setup_schema["name"],
                    "pairwise_ruleset_name": setup_ruleset["name"],
                    "rules": [],
                },
            )

        # List with limit
        response = client.get("/api/v1/cluster-rulesets?limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2

        # List with skip
        response = client.get("/api/v1/cluster-rulesets?skip=2")
        assert response.status_code == 200
        assert len(response.json()) == 3


class TestGetClusterRuleSet:
    """Tests for GET /cluster-rulesets/{name}"""

    def test_get_cluster_ruleset_success(self, client, setup_schema, setup_ruleset):
        """Test getting a cluster ruleset by name."""
        # Create
        create_response = client.post(
            "/api/v1/cluster-rulesets",
            json={
                "name": "get_test",
                "version": "1.0.0",
                "description": "Test description",
                "schema_name": setup_schema["name"],
                "pairwise_ruleset_name": setup_ruleset["name"],
                "rules": [{"name": "test_rule", "type": "requirement", "enabled": True}],
            },
        )
        assert create_response.status_code == 201

        # Get
        response = client.get("/api/v1/cluster-rulesets/get_test")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "get_test"
        assert data["description"] == "Test description"
        assert len(data["rules"]) == 1

    def test_get_cluster_ruleset_not_found(self, client):
        """Test getting nonexistent cluster ruleset returns 404."""
        response = client.get("/api/v1/cluster-rulesets/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUpdateClusterRuleSet:
    """Tests for PUT /cluster-rulesets/{name}"""

    def test_update_cluster_ruleset_version(self, client, setup_schema, setup_ruleset):
        """Test updating cluster ruleset version."""
        # Create
        client.post(
            "/api/v1/cluster-rulesets",
            json={
                "name": "update_test",
                "version": "1.0.0",
                "schema_name": setup_schema["name"],
                "pairwise_ruleset_name": setup_ruleset["name"],
                "rules": [],
            },
        )

        # Update
        response = client.put("/api/v1/cluster-rulesets/update_test", json={"version": "2.0.0"})

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "2.0.0"

    def test_update_cluster_ruleset_description(self, client, setup_schema, setup_ruleset):
        """Test updating cluster ruleset description."""
        # Create
        client.post(
            "/api/v1/cluster-rulesets",
            json={
                "name": "update_test",
                "version": "1.0.0",
                "schema_name": setup_schema["name"],
                "pairwise_ruleset_name": setup_ruleset["name"],
                "rules": [],
            },
        )

        # Update
        response = client.put(
            "/api/v1/cluster-rulesets/update_test", json={"description": "Updated description"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    def test_update_cluster_ruleset_rules(self, client, setup_schema, setup_ruleset):
        """Test updating cluster ruleset rules."""
        # Create
        client.post(
            "/api/v1/cluster-rulesets",
            json={
                "name": "update_test",
                "version": "1.0.0",
                "schema_name": setup_schema["name"],
                "pairwise_ruleset_name": setup_ruleset["name"],
                "rules": [],
            },
        )

        # Update
        new_rules = [{"name": "new_rule", "type": "requirement", "enabled": True, "condition": {}}]
        response = client.put("/api/v1/cluster-rulesets/update_test", json={"rules": new_rules})

        assert response.status_code == 200
        data = response.json()
        assert len(data["rules"]) == 1
        assert data["rules"][0]["name"] == "new_rule"

    def test_update_cluster_ruleset_not_found(self, client):
        """Test updating nonexistent cluster ruleset returns 404."""
        response = client.put("/api/v1/cluster-rulesets/nonexistent", json={"version": "2.0.0"})

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestDeleteClusterRuleSet:
    """Tests for DELETE /cluster-rulesets/{name}"""

    def test_delete_cluster_ruleset_success(self, client, setup_schema, setup_ruleset):
        """Test deleting a cluster ruleset."""
        # Create
        client.post(
            "/api/v1/cluster-rulesets",
            json={
                "name": "delete_test",
                "version": "1.0.0",
                "schema_name": setup_schema["name"],
                "pairwise_ruleset_name": setup_ruleset["name"],
                "rules": [],
            },
        )

        # Delete
        response = client.delete("/api/v1/cluster-rulesets/delete_test")

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

        # Verify deleted
        get_response = client.get("/api/v1/cluster-rulesets/delete_test")
        assert get_response.status_code == 404

    def test_delete_cluster_ruleset_not_found(self, client):
        """Test deleting nonexistent cluster ruleset returns 404."""
        response = client.delete("/api/v1/cluster-rulesets/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestClusterRuleSetTimestamps:
    """Tests for cluster ruleset timestamp fields."""

    def test_cluster_ruleset_has_created_at(self, client, setup_schema, setup_ruleset):
        """Test that cluster ruleset has created_at timestamp."""
        create_response = client.post(
            "/api/v1/cluster-rulesets",
            json={
                "name": "timestamp_test",
                "version": "1.0.0",
                "schema_name": setup_schema["name"],
                "pairwise_ruleset_name": setup_ruleset["name"],
                "rules": [],
            },
        )

        assert create_response.status_code == 201
        data = create_response.json()
        assert "created_at" in data
        assert data["created_at"] is not None

    def test_cluster_ruleset_has_updated_at(self, client, setup_schema, setup_ruleset):
        """Test that cluster ruleset has updated_at timestamp."""
        create_response = client.post(
            "/api/v1/cluster-rulesets",
            json={
                "name": "timestamp_test",
                "version": "1.0.0",
                "schema_name": setup_schema["name"],
                "pairwise_ruleset_name": setup_ruleset["name"],
                "rules": [],
            },
        )

        assert create_response.status_code == 201
        data = create_response.json()
        assert "updated_at" in data
        assert data["updated_at"] is not None
