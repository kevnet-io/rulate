"""
Integration tests for RuleSet API endpoints.

Tests all CRUD operations for the /api/v1/rulesets endpoints including:
- Creating rulesets with various rule types
- Listing rulesets with pagination
- Getting specific rulesets
- Updating rulesets
- Deleting rulesets
- Schema reference validation
- Error handling (404, 409, 422)
"""

import pytest


class TestCreateRuleSet:
    """Tests for POST /api/v1/rulesets endpoint."""

    def test_create_ruleset_success(self, client, setup_schema, sample_ruleset_payload):
        """Test creating a ruleset with valid data."""
        response = client.post("/api/v1/rulesets", json=sample_ruleset_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_ruleset_payload["name"]
        assert data["version"] == sample_ruleset_payload["version"]
        assert data["description"] == sample_ruleset_payload["description"]
        assert data["schema_name"] == sample_ruleset_payload["schema_name"]
        assert len(data["rules"]) == len(sample_ruleset_payload["rules"])
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_minimal_ruleset(self, client, setup_schema, minimal_ruleset_payload):
        """Test creating a ruleset with only required fields."""
        response = client.post("/api/v1/rulesets", json=minimal_ruleset_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == minimal_ruleset_payload["name"]
        assert data["version"] == minimal_ruleset_payload["version"]
        assert data["description"] is None
        assert data["rules"] == []

    def test_create_ruleset_with_nonexistent_schema(self, client):
        """Test creating ruleset with non-existent schema reference fails."""
        payload = {
            "name": "orphan_ruleset",
            "version": "1.0.0",
            "schema_name": "nonexistent_schema",
            "rules": [],
        }

        response = client.post("/api/v1/rulesets", json=payload)

        assert response.status_code == 404
        assert "schema" in response.json()["detail"].lower()

    def test_create_duplicate_ruleset_fails(self, client, setup_schema, sample_ruleset_payload):
        """Test creating duplicate ruleset returns 409 Conflict."""
        # Create first ruleset
        response1 = client.post("/api/v1/rulesets", json=sample_ruleset_payload)
        assert response1.status_code == 201

        # Attempt to create duplicate
        response2 = client.post("/api/v1/rulesets", json=sample_ruleset_payload)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"].lower()

    def test_create_ruleset_exclusion_rule(self, client, setup_schema):
        """Test creating ruleset with exclusion rule."""
        payload = {
            "name": "exclusion_rules",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "rules": [
                {
                    "name": "same_category",
                    "type": "exclusion",
                    "enabled": True,
                    "condition": {"equals": {"field": "category"}},
                }
            ],
        }

        response = client.post("/api/v1/rulesets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert len(data["rules"]) == 1
        assert data["rules"][0]["type"] == "exclusion"
        assert data["rules"][0]["name"] == "same_category"

    def test_create_ruleset_requirement_rule(self, client, setup_schema):
        """Test creating ruleset with requirement rule."""
        payload = {
            "name": "requirement_rules",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "rules": [
                {
                    "name": "similar_formality",
                    "type": "requirement",
                    "enabled": True,
                    "condition": {"abs_diff": {"field": "formality", "max": 2}},
                }
            ],
        }

        response = client.post("/api/v1/rulesets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert len(data["rules"]) == 1
        assert data["rules"][0]["type"] == "requirement"

    def test_create_ruleset_mixed_rule_types(self, client, setup_schema):
        """Test creating ruleset with both exclusion and requirement rules."""
        payload = {
            "name": "mixed_rules",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "rules": [
                {
                    "name": "exclusion_rule",
                    "type": "exclusion",
                    "enabled": True,
                    "condition": {"equals": {"field": "category"}},
                },
                {
                    "name": "requirement_rule",
                    "type": "requirement",
                    "enabled": True,
                    "condition": {"abs_diff": {"field": "formality", "max": 1}},
                },
            ],
        }

        response = client.post("/api/v1/rulesets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert len(data["rules"]) == 2
        rule_types = [r["type"] for r in data["rules"]]
        assert "exclusion" in rule_types
        assert "requirement" in rule_types

    def test_create_ruleset_disabled_rule(self, client, setup_schema):
        """Test creating ruleset with disabled rule."""
        payload = {
            "name": "disabled_rule",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "rules": [
                {
                    "name": "disabled",
                    "type": "exclusion",
                    "enabled": False,
                    "condition": {"equals": {"field": "category"}},
                }
            ],
        }

        response = client.post("/api/v1/rulesets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["rules"][0]["enabled"] is False

    def test_create_ruleset_complex_condition(self, client, setup_schema):
        """Test creating ruleset with nested logical operators."""
        payload = {
            "name": "complex_rules",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "rules": [
                {
                    "name": "complex_condition",
                    "type": "exclusion",
                    "enabled": True,
                    "condition": {
                        "all": [
                            {"equals": {"field": "category"}},
                            {"not": {"has_different": {"field": "color"}}},
                        ]
                    },
                }
            ],
        }

        response = client.post("/api/v1/rulesets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "all" in data["rules"][0]["condition"]

    def test_create_ruleset_missing_required_fields(self, client):
        """Test creating ruleset without required fields fails."""
        # Missing name
        payload1 = {
            "version": "1.0.0",
            "schema_name": "test_schema",
            "rules": [],
        }
        response1 = client.post("/api/v1/rulesets", json=payload1)
        assert response1.status_code == 422

        # Missing version
        payload2 = {
            "name": "test",
            "schema_name": "test_schema",
            "rules": [],
        }
        response2 = client.post("/api/v1/rulesets", json=payload2)
        assert response2.status_code == 422

        # Missing schema_name
        payload3 = {
            "name": "test",
            "version": "1.0.0",
            "rules": [],
        }
        response3 = client.post("/api/v1/rulesets", json=payload3)
        assert response3.status_code == 422


class TestListRuleSets:
    """Tests for GET /api/v1/rulesets endpoint."""

    def test_list_rulesets_empty(self, client):
        """Test listing rulesets when database is empty."""
        response = client.get("/api/v1/rulesets")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_rulesets_single(self, client, setup_ruleset):
        """Test listing rulesets with one ruleset in database."""
        response = client.get("/api/v1/rulesets")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == setup_ruleset["name"]

    def test_list_rulesets_multiple(self, client, setup_schema, sample_ruleset_payload):
        """Test listing multiple rulesets."""
        # Create 3 rulesets
        for i in range(3):
            payload = sample_ruleset_payload.copy()
            payload["name"] = f"ruleset_{i}"
            response = client.post("/api/v1/rulesets", json=payload)
            assert response.status_code == 201

        # List all rulesets
        response = client.get("/api/v1/rulesets")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = [r["name"] for r in data]
        assert "ruleset_0" in names
        assert "ruleset_1" in names
        assert "ruleset_2" in names

    def test_list_rulesets_pagination_skip(self, client, setup_schema, sample_ruleset_payload):
        """Test listing rulesets with skip parameter."""
        # Create 5 rulesets
        for i in range(5):
            payload = sample_ruleset_payload.copy()
            payload["name"] = f"ruleset_{i}"
            client.post("/api/v1/rulesets", json=payload)

        # Skip first 2
        response = client.get("/api/v1/rulesets?skip=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_rulesets_pagination_limit(self, client, setup_schema, sample_ruleset_payload):
        """Test listing rulesets with limit parameter."""
        # Create 5 rulesets
        for i in range(5):
            payload = sample_ruleset_payload.copy()
            payload["name"] = f"ruleset_{i}"
            client.post("/api/v1/rulesets", json=payload)

        # Limit to 3
        response = client.get("/api/v1/rulesets?limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_rulesets_includes_schema_name(self, client, setup_ruleset):
        """Test that listed rulesets include schema_name."""
        response = client.get("/api/v1/rulesets")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "schema_name" in data[0]
        assert data[0]["schema_name"] == setup_ruleset["schema_name"]


class TestGetRuleSet:
    """Tests for GET /api/v1/rulesets/{ruleset_name} endpoint."""

    def test_get_ruleset_success(self, client, setup_ruleset):
        """Test getting a specific ruleset by name."""
        ruleset_name = setup_ruleset["name"]
        response = client.get(f"/api/v1/rulesets/{ruleset_name}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == ruleset_name
        assert data["id"] == setup_ruleset["id"]
        assert len(data["rules"]) == len(setup_ruleset["rules"])

    def test_get_ruleset_not_found(self, client):
        """Test getting non-existent ruleset returns 404."""
        response = client.get("/api/v1/rulesets/nonexistent_ruleset")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_ruleset_preserves_rule_order(self, client, setup_schema, sample_ruleset_payload):
        """Test that rule order is preserved."""
        # Create ruleset
        create_response = client.post("/api/v1/rulesets", json=sample_ruleset_payload)
        assert create_response.status_code == 201

        # Get ruleset
        ruleset_name = sample_ruleset_payload["name"]
        get_response = client.get(f"/api/v1/rulesets/{ruleset_name}")

        assert get_response.status_code == 200
        data = get_response.json()

        # Verify rule order matches
        original_names = [r["name"] for r in sample_ruleset_payload["rules"]]
        retrieved_names = [r["name"] for r in data["rules"]]
        assert original_names == retrieved_names


class TestUpdateRuleSet:
    """Tests for PUT /api/v1/rulesets/{ruleset_name} endpoint."""

    def test_update_ruleset_full(self, client, setup_ruleset):
        """Test updating all fields of a ruleset."""
        ruleset_name = setup_ruleset["name"]
        update_payload = {
            "version": "2.0.0",
            "description": "Updated description",
            "rules": [
                {
                    "name": "new_rule",
                    "type": "exclusion",
                    "enabled": True,
                    "condition": {"equals": {"field": "color"}},
                }
            ],
        }

        response = client.put(f"/api/v1/rulesets/{ruleset_name}", json=update_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "2.0.0"
        assert data["description"] == "Updated description"
        assert len(data["rules"]) == 1
        assert data["rules"][0]["name"] == "new_rule"
        # Name should not change
        assert data["name"] == ruleset_name

    def test_update_ruleset_partial_version_only(self, client, setup_ruleset):
        """Test updating only version field."""
        ruleset_name = setup_ruleset["name"]
        update_payload = {
            "version": "1.1.0",
        }

        response = client.put(f"/api/v1/rulesets/{ruleset_name}", json=update_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "1.1.0"
        # Other fields should remain unchanged
        assert data["description"] == setup_ruleset["description"]
        assert len(data["rules"]) == len(setup_ruleset["rules"])

    def test_update_ruleset_partial_rules_only(self, client, setup_ruleset):
        """Test updating only rules."""
        ruleset_name = setup_ruleset["name"]
        update_payload = {
            "rules": [],
        }

        response = client.put(f"/api/v1/rulesets/{ruleset_name}", json=update_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["rules"] == []
        assert data["version"] == setup_ruleset["version"]

    def test_update_ruleset_add_rule(self, client, setup_schema):
        """Test adding a new rule to an existing ruleset."""
        # Create ruleset with one rule
        create_payload = {
            "name": "test_add_rule",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "rules": [
                {
                    "name": "rule1",
                    "type": "exclusion",
                    "enabled": True,
                    "condition": {"equals": {"field": "category"}},
                }
            ],
        }
        create_response = client.post("/api/v1/rulesets", json=create_payload)
        assert create_response.status_code == 201

        # Update to add another rule
        update_payload = {
            "rules": [
                {
                    "name": "rule1",
                    "type": "exclusion",
                    "enabled": True,
                    "condition": {"equals": {"field": "category"}},
                },
                {
                    "name": "rule2",
                    "type": "requirement",
                    "enabled": True,
                    "condition": {"abs_diff": {"field": "formality", "max": 1}},
                },
            ],
        }

        response = client.put("/api/v1/rulesets/test_add_rule", json=update_payload)

        assert response.status_code == 200
        data = response.json()
        assert len(data["rules"]) == 2

    def test_update_ruleset_disable_rule(self, client, setup_schema):
        """Test disabling a rule via update."""
        # Create ruleset with enabled rule
        create_payload = {
            "name": "test_disable",
            "version": "1.0.0",
            "schema_name": setup_schema["name"],
            "rules": [
                {
                    "name": "rule1",
                    "type": "exclusion",
                    "enabled": True,
                    "condition": {"equals": {"field": "category"}},
                }
            ],
        }
        client.post("/api/v1/rulesets", json=create_payload)

        # Update to disable the rule
        update_payload = {
            "rules": [
                {
                    "name": "rule1",
                    "type": "exclusion",
                    "enabled": False,
                    "condition": {"equals": {"field": "category"}},
                }
            ],
        }

        response = client.put("/api/v1/rulesets/test_disable", json=update_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["rules"][0]["enabled"] is False

    def test_update_ruleset_not_found(self, client):
        """Test updating non-existent ruleset returns 404."""
        update_payload = {
            "version": "2.0.0",
        }

        response = client.put("/api/v1/rulesets/nonexistent", json=update_payload)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestDeleteRuleSet:
    """Tests for DELETE /api/v1/rulesets/{ruleset_name} endpoint."""

    def test_delete_ruleset_success(self, client, setup_ruleset):
        """Test deleting a ruleset."""
        ruleset_name = setup_ruleset["name"]
        response = client.delete(f"/api/v1/rulesets/{ruleset_name}")

        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"].lower()

        # Verify ruleset is actually deleted
        get_response = client.get(f"/api/v1/rulesets/{ruleset_name}")
        assert get_response.status_code == 404

    def test_delete_ruleset_not_found(self, client):
        """Test deleting non-existent ruleset returns 404."""
        response = client.delete("/api/v1/rulesets/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_ruleset_does_not_delete_schema(self, client, setup_schema, setup_ruleset):
        """Test deleting ruleset does not delete the referenced schema."""
        schema_name = setup_schema["name"]
        ruleset_name = setup_ruleset["name"]

        # Delete ruleset
        delete_response = client.delete(f"/api/v1/rulesets/{ruleset_name}")
        assert delete_response.status_code == 200

        # Verify schema still exists
        schema_get = client.get(f"/api/v1/schemas/{schema_name}")
        assert schema_get.status_code == 200


class TestRuleSetTimestamps:
    """Tests for ruleset timestamp behavior."""

    def test_ruleset_has_created_at(self, client, setup_schema, sample_ruleset_payload):
        """Test that created ruleset has created_at timestamp."""
        response = client.post("/api/v1/rulesets", json=sample_ruleset_payload)
        assert response.status_code == 201
        data = response.json()
        assert "created_at" in data
        assert data["created_at"] is not None

    def test_ruleset_has_updated_at(self, client, setup_schema, sample_ruleset_payload):
        """Test that created ruleset has updated_at timestamp."""
        response = client.post("/api/v1/rulesets", json=sample_ruleset_payload)
        assert response.status_code == 201
        data = response.json()
        assert "updated_at" in data
        assert data["updated_at"] is not None
