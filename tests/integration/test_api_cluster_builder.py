"""
Integration tests for Cluster Builder API endpoints.

Tests cover:
- POST /evaluate/cluster/validate - Validate a specific cluster
- POST /evaluate/cluster/candidates - Evaluate candidates for adding to a cluster
"""

import pytest


class TestValidateCluster:
    """Tests for POST /evaluate/cluster/validate"""

    @pytest.fixture
    def builder_setup(self, client, setup_schema):
        """Create full setup for cluster builder tests."""
        schema_name = setup_schema["name"]

        # Create pairwise ruleset
        ruleset_response = client.post(
            "/api/v1/rulesets",
            json={
                "name": "builder_pairwise_rules",
                "version": "1.0.0",
                "schema_name": schema_name,
                "rules": [
                    {
                        "name": "same_category_incompatible",
                        "type": "exclusion",
                        "enabled": True,
                        "condition": {"equals": {"field": "category"}},
                    }
                ],
            },
        )
        assert ruleset_response.status_code == 201

        # Create cluster ruleset with min_cluster_size rule
        cluster_ruleset_response = client.post(
            "/api/v1/cluster-rulesets",
            json={
                "name": "builder_cluster_rules",
                "version": "1.0.0",
                "schema_name": schema_name,
                "pairwise_ruleset_name": "builder_pairwise_rules",
                "rules": [
                    {
                        "name": "min_size_2",
                        "type": "requirement",
                        "enabled": True,
                        "condition": {"min_cluster_size": {"value": 2}},
                    }
                ],
            },
        )
        assert cluster_ruleset_response.status_code == 201

        # Create catalog
        catalog_response = client.post(
            "/api/v1/catalogs",
            json={
                "name": "builder_catalog",
                "schema_name": schema_name,
            },
        )
        assert catalog_response.status_code == 201

        # Create items with different categories
        items = [
            {
                "item_id": "shirt_1",
                "name": "Shirt 1",
                "attributes": {"category": "shirt", "color": "blue"},
            },
            {
                "item_id": "shirt_2",
                "name": "Shirt 2",
                "attributes": {"category": "shirt", "color": "red"},
            },
            {
                "item_id": "pants_1",
                "name": "Pants 1",
                "attributes": {"category": "pants", "color": "black"},
            },
            {
                "item_id": "shoes_1",
                "name": "Shoes 1",
                "attributes": {"category": "shoes", "color": "brown"},
            },
        ]

        for item in items:
            item_response = client.post("/api/v1/catalogs/builder_catalog/items", json=item)
            assert item_response.status_code == 201

        return {
            "catalog_name": "builder_catalog",
            "pairwise_ruleset_name": "builder_pairwise_rules",
            "cluster_ruleset_name": "builder_cluster_rules",
        }

    def test_validate_cluster_valid(self, client, builder_setup):
        """Test validating a valid cluster."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "item_ids": ["shirt_1", "pants_1"],
        }

        response = client.post("/api/v1/evaluate/cluster/validate", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["item_ids"] == ["shirt_1", "pants_1"]
        assert "rule_evaluations" in data
        assert len(data["rule_evaluations"]) > 0
        assert all(r["passed"] for r in data["rule_evaluations"])

    def test_validate_cluster_invalid_too_small(self, client, builder_setup):
        """Test validating a cluster that fails min_cluster_size rule."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "item_ids": ["shirt_1"],  # Only 1 item, min_size is 2
        }

        response = client.post("/api/v1/evaluate/cluster/validate", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert len(data["rule_evaluations"]) > 0
        # At least one rule should have failed
        assert any(not r["passed"] for r in data["rule_evaluations"])

    def test_validate_cluster_empty(self, client, builder_setup):
        """Test validating an empty cluster."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "item_ids": [],
        }

        response = client.post("/api/v1/evaluate/cluster/validate", json=request)

        assert response.status_code == 200
        data = response.json()
        # Empty cluster should be invalid
        assert data["is_valid"] is False

    def test_validate_cluster_three_items(self, client, builder_setup):
        """Test validating a valid 3-item cluster."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "item_ids": ["shirt_1", "pants_1", "shoes_1"],
        }

        response = client.post("/api/v1/evaluate/cluster/validate", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert len(data["item_ids"]) == 3

    def test_validate_cluster_catalog_not_found(self, client, builder_setup):
        """Test validating cluster with nonexistent catalog."""
        request = {
            "catalog_name": "nonexistent",
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "item_ids": ["shirt_1"],
        }

        response = client.post("/api/v1/evaluate/cluster/validate", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_validate_cluster_ruleset_not_found(self, client, builder_setup):
        """Test validating cluster with nonexistent cluster ruleset."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "cluster_ruleset_name": "nonexistent",
            "item_ids": ["shirt_1"],
        }

        response = client.post("/api/v1/evaluate/cluster/validate", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_validate_cluster_item_not_found(self, client, builder_setup):
        """Test validating cluster with nonexistent item."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "item_ids": ["shirt_1", "nonexistent_item"],
        }

        response = client.post("/api/v1/evaluate/cluster/validate", json=request)

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_validate_cluster_missing_fields(self, client):
        """Test validating cluster with missing required fields."""
        # Missing catalog_name
        response = client.post(
            "/api/v1/evaluate/cluster/validate",
            json={
                "cluster_ruleset_name": "test",
                "item_ids": ["item1"],
            },
        )
        assert response.status_code == 422

        # Missing cluster_ruleset_name
        response = client.post(
            "/api/v1/evaluate/cluster/validate",
            json={
                "catalog_name": "test",
                "item_ids": ["item1"],
            },
        )
        assert response.status_code == 422


class TestEvaluateCandidates:
    """Tests for POST /evaluate/cluster/candidates"""

    @pytest.fixture
    def builder_setup(self, client, setup_schema):
        """Create full setup for cluster builder tests."""
        schema_name = setup_schema["name"]

        # Create pairwise ruleset
        ruleset_response = client.post(
            "/api/v1/rulesets",
            json={
                "name": "candidates_pairwise_rules",
                "version": "1.0.0",
                "schema_name": schema_name,
                "rules": [
                    {
                        "name": "same_category_incompatible",
                        "type": "exclusion",
                        "enabled": True,
                        "condition": {"equals": {"field": "category"}},
                    }
                ],
            },
        )
        assert ruleset_response.status_code == 201

        # Create cluster ruleset with min_cluster_size rule
        cluster_ruleset_response = client.post(
            "/api/v1/cluster-rulesets",
            json={
                "name": "candidates_cluster_rules",
                "version": "1.0.0",
                "schema_name": schema_name,
                "pairwise_ruleset_name": "candidates_pairwise_rules",
                "rules": [
                    {
                        "name": "min_size_2",
                        "type": "requirement",
                        "enabled": True,
                        "condition": {"min_cluster_size": {"value": 2}},
                    }
                ],
            },
        )
        assert cluster_ruleset_response.status_code == 201

        # Create catalog
        catalog_response = client.post(
            "/api/v1/catalogs",
            json={
                "name": "candidates_catalog",
                "schema_name": schema_name,
            },
        )
        assert catalog_response.status_code == 201

        # Create items with different categories
        items = [
            {
                "item_id": "shirt_1",
                "name": "Shirt 1",
                "attributes": {"category": "shirt", "color": "blue"},
            },
            {
                "item_id": "shirt_2",
                "name": "Shirt 2",
                "attributes": {"category": "shirt", "color": "red"},
            },
            {
                "item_id": "pants_1",
                "name": "Pants 1",
                "attributes": {"category": "pants", "color": "black"},
            },
            {
                "item_id": "shoes_1",
                "name": "Shoes 1",
                "attributes": {"category": "shoes", "color": "brown"},
            },
        ]

        for item in items:
            item_response = client.post("/api/v1/catalogs/candidates_catalog/items", json=item)
            assert item_response.status_code == 201

        return {
            "catalog_name": "candidates_catalog",
            "pairwise_ruleset_name": "candidates_pairwise_rules",
            "cluster_ruleset_name": "candidates_cluster_rules",
        }

    def test_evaluate_candidates_empty_base(self, client, builder_setup):
        """Test evaluating candidates with empty base cluster."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "pairwise_ruleset_name": builder_setup["pairwise_ruleset_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "base_item_ids": [],
        }

        response = client.post("/api/v1/evaluate/cluster/candidates", json=request)

        assert response.status_code == 200
        data = response.json()
        assert "base_validation" in data
        assert "candidates" in data
        # Empty base cluster is invalid
        assert data["base_validation"]["is_valid"] is False
        # All catalog items should be candidates
        assert len(data["candidates"]) == 4

    def test_evaluate_candidates_single_base_item(self, client, builder_setup):
        """Test evaluating candidates with single base item."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "pairwise_ruleset_name": builder_setup["pairwise_ruleset_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "base_item_ids": ["shirt_1"],
        }

        response = client.post("/api/v1/evaluate/cluster/candidates", json=request)

        assert response.status_code == 200
        data = response.json()
        # Base cluster with 1 item should be invalid (min_size is 2)
        assert data["base_validation"]["is_valid"] is False
        # Should have 3 candidates (all items except shirt_1)
        assert len(data["candidates"]) == 3

        # Check candidate structure
        for candidate in data["candidates"]:
            assert "item_id" in candidate
            assert "is_pairwise_compatible" in candidate
            assert "cluster_if_added" in candidate

    def test_evaluate_candidates_pairwise_compatibility(self, client, builder_setup):
        """Test that pairwise compatibility is correctly evaluated."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "pairwise_ruleset_name": builder_setup["pairwise_ruleset_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "base_item_ids": ["shirt_1"],
        }

        response = client.post("/api/v1/evaluate/cluster/candidates", json=request)

        assert response.status_code == 200
        data = response.json()

        # Find shirt_2 in candidates - should be pairwise INCOMPATIBLE (same category)
        shirt_2_candidate = next(c for c in data["candidates"] if c["item_id"] == "shirt_2")
        assert shirt_2_candidate["is_pairwise_compatible"] is False

        # Find pants_1 in candidates - should be pairwise COMPATIBLE (different category)
        pants_1_candidate = next(c for c in data["candidates"] if c["item_id"] == "pants_1")
        assert pants_1_candidate["is_pairwise_compatible"] is True

    def test_evaluate_candidates_cluster_validation(self, client, builder_setup):
        """Test that cluster validation is correctly evaluated for each candidate."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "pairwise_ruleset_name": builder_setup["pairwise_ruleset_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "base_item_ids": ["shirt_1"],
        }

        response = client.post("/api/v1/evaluate/cluster/candidates", json=request)

        assert response.status_code == 200
        data = response.json()

        # Adding any item to base would make cluster size = 2, which satisfies min_size rule
        pants_1_candidate = next(c for c in data["candidates"] if c["item_id"] == "pants_1")
        assert pants_1_candidate["cluster_if_added"]["is_valid"] is True
        # Item IDs should be base + candidate
        assert "shirt_1" in pants_1_candidate["cluster_if_added"]["item_ids"]
        assert "pants_1" in pants_1_candidate["cluster_if_added"]["item_ids"]

    def test_evaluate_candidates_specific_candidates(self, client, builder_setup):
        """Test evaluating specific candidate items only."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "pairwise_ruleset_name": builder_setup["pairwise_ruleset_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "base_item_ids": ["shirt_1"],
            "candidate_item_ids": ["pants_1", "shoes_1"],  # Only evaluate these
        }

        response = client.post("/api/v1/evaluate/cluster/candidates", json=request)

        assert response.status_code == 200
        data = response.json()
        # Should only have 2 candidates
        assert len(data["candidates"]) == 2
        candidate_ids = [c["item_id"] for c in data["candidates"]]
        assert "pants_1" in candidate_ids
        assert "shoes_1" in candidate_ids
        assert "shirt_2" not in candidate_ids

    def test_evaluate_candidates_two_base_items(self, client, builder_setup):
        """Test evaluating candidates with two base items."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "pairwise_ruleset_name": builder_setup["pairwise_ruleset_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "base_item_ids": ["shirt_1", "pants_1"],
        }

        response = client.post("/api/v1/evaluate/cluster/candidates", json=request)

        assert response.status_code == 200
        data = response.json()
        # Base cluster with 2 items should be valid
        assert data["base_validation"]["is_valid"] is True
        # Should have 2 candidates (shirt_2 and shoes_1)
        assert len(data["candidates"]) == 2

    def test_evaluate_candidates_catalog_not_found(self, client, builder_setup):
        """Test evaluating candidates with nonexistent catalog."""
        request = {
            "catalog_name": "nonexistent",
            "pairwise_ruleset_name": builder_setup["pairwise_ruleset_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "base_item_ids": [],
        }

        response = client.post("/api/v1/evaluate/cluster/candidates", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_candidates_pairwise_ruleset_not_found(self, client, builder_setup):
        """Test evaluating candidates with nonexistent pairwise ruleset."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "pairwise_ruleset_name": "nonexistent",
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "base_item_ids": [],
        }

        response = client.post("/api/v1/evaluate/cluster/candidates", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_candidates_cluster_ruleset_not_found(self, client, builder_setup):
        """Test evaluating candidates with nonexistent cluster ruleset."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "pairwise_ruleset_name": builder_setup["pairwise_ruleset_name"],
            "cluster_ruleset_name": "nonexistent",
            "base_item_ids": [],
        }

        response = client.post("/api/v1/evaluate/cluster/candidates", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_candidates_base_item_not_found(self, client, builder_setup):
        """Test evaluating candidates with nonexistent base item."""
        request = {
            "catalog_name": builder_setup["catalog_name"],
            "pairwise_ruleset_name": builder_setup["pairwise_ruleset_name"],
            "cluster_ruleset_name": builder_setup["cluster_ruleset_name"],
            "base_item_ids": ["nonexistent_item"],
        }

        response = client.post("/api/v1/evaluate/cluster/candidates", json=request)

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_candidates_missing_fields(self, client):
        """Test evaluating candidates with missing required fields."""
        # Missing catalog_name
        response = client.post(
            "/api/v1/evaluate/cluster/candidates",
            json={
                "pairwise_ruleset_name": "test",
                "cluster_ruleset_name": "test",
                "base_item_ids": [],
            },
        )
        assert response.status_code == 422

        # Missing pairwise_ruleset_name
        response = client.post(
            "/api/v1/evaluate/cluster/candidates",
            json={
                "catalog_name": "test",
                "cluster_ruleset_name": "test",
                "base_item_ids": [],
            },
        )
        assert response.status_code == 422

        # Missing cluster_ruleset_name
        response = client.post(
            "/api/v1/evaluate/cluster/candidates",
            json={
                "catalog_name": "test",
                "pairwise_ruleset_name": "test",
                "base_item_ids": [],
            },
        )
        assert response.status_code == 422
