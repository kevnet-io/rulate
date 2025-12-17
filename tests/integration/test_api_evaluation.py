"""
Integration tests for Evaluation API endpoints.

Tests cover:
- Evaluating pairs of items
- Evaluating compatibility matrix for a catalog
- Evaluating one item against all others
- Error handling (404 for missing resources)
"""

import pytest


@pytest.fixture
def evaluation_setup(client, setup_schema):
    """
    Create a complete evaluation scenario with catalog, ruleset, and items.

    Creates:
    - Schema with category (enum), color (string), formality (integer)
    - RuleSet with exclusion and requirement rules
    - Catalog with 4 items (2 compatible, 2 incompatible pairs)
    """
    schema_name = setup_schema["name"]

    # Create ruleset with actual compatibility rules
    ruleset_payload = {
        "name": "eval_rules",
        "version": "1.0.0",
        "schema_name": schema_name,
        "rules": [
            {
                "name": "same_category_incompatible",
                "type": "exclusion",
                "enabled": True,
                "condition": {"equals": {"field": "category"}},
            },
            {
                "name": "similar_formality_required",
                "type": "requirement",
                "enabled": True,
                "condition": {"abs_diff": {"field": "formality", "max": 2}},
            },
        ],
    }
    ruleset_response = client.post("/api/v1/rulesets", json=ruleset_payload)
    assert ruleset_response.status_code == 201
    ruleset = ruleset_response.json()

    # Create catalog
    catalog_payload = {
        "name": "eval_catalog",
        "schema_name": schema_name,
        "description": "Catalog for evaluation tests",
    }
    catalog_response = client.post("/api/v1/catalogs", json=catalog_payload)
    assert catalog_response.status_code == 201
    catalog = catalog_response.json()

    # Create items
    items_data = [
        {
            "item_id": "shirt_1",
            "name": "Blue Shirt",
            "attributes": {"category": "shirt", "color": "blue", "formality": 3},
        },
        {
            "item_id": "pants_1",
            "name": "Black Pants",
            "attributes": {"category": "pants", "color": "black", "formality": 4},
        },
        {
            "item_id": "shirt_2",
            "name": "Red Shirt",
            "attributes": {"category": "shirt", "color": "red", "formality": 2},
        },
        {
            "item_id": "shoes_1",
            "name": "Brown Shoes",
            "attributes": {"category": "shoes", "color": "brown", "formality": 5},
        },
    ]

    items = []
    for item_data in items_data:
        item_response = client.post(
            f"/api/v1/catalogs/{catalog['name']}/items",
            json=item_data,
        )
        assert item_response.status_code == 201
        items.append(item_response.json())

    return {
        "schema": setup_schema,
        "ruleset": ruleset,
        "catalog": catalog,
        "items": items,
    }


class TestEvaluatePair:
    """Tests for POST /evaluate/pair"""

    def test_evaluate_pair_compatible(self, client, evaluation_setup):
        """Test evaluating two compatible items."""
        request = {
            "item1_id": "shirt_1",
            "item2_id": "pants_1",
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/pair", json=request)

        assert response.status_code == 200
        data = response.json()
        assert "compatible" in data
        assert "item1_id" in data
        assert "item2_id" in data
        assert "rules_evaluated" in data
        assert data["item1_id"] == "shirt_1"
        assert data["item2_id"] == "pants_1"
        # Should be compatible: different categories, formality diff = 1
        assert data["compatible"] is True

    def test_evaluate_pair_incompatible_same_category(self, client, evaluation_setup):
        """Test evaluating two items with same category (exclusion rule)."""
        request = {
            "item1_id": "shirt_1",
            "item2_id": "shirt_2",
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/pair", json=request)

        assert response.status_code == 200
        data = response.json()
        # Should be incompatible: same category (exclusion rule)
        assert data["compatible"] is False

    def test_evaluate_pair_incompatible_formality_diff(self, client, evaluation_setup):
        """Test evaluating items with large formality difference."""
        request = {
            "item1_id": "shirt_2",  # formality: 2
            "item2_id": "shoes_1",  # formality: 5
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/pair", json=request)

        assert response.status_code == 200
        data = response.json()
        # Should be incompatible: formality diff = 3 > max 2
        assert data["compatible"] is False

    def test_evaluate_pair_includes_rules_evaluated(self, client, evaluation_setup):
        """Test that response includes detailed rule evaluations."""
        request = {
            "item1_id": "shirt_1",
            "item2_id": "pants_1",
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/pair", json=request)

        assert response.status_code == 200
        data = response.json()
        assert "rules_evaluated" in data
        assert len(data["rules_evaluated"]) == 2  # 2 rules in ruleset

        for rule_eval in data["rules_evaluated"]:
            assert "rule_name" in rule_eval
            assert "passed" in rule_eval
            assert "reason" in rule_eval

    def test_evaluate_pair_catalog_not_found(self, client, evaluation_setup):
        """Test pair evaluation with nonexistent catalog."""
        request = {
            "item1_id": "shirt_1",
            "item2_id": "pants_1",
            "catalog_name": "nonexistent",
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/pair", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_pair_ruleset_not_found(self, client, evaluation_setup):
        """Test pair evaluation with nonexistent ruleset."""
        request = {
            "item1_id": "shirt_1",
            "item2_id": "pants_1",
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": "nonexistent",
        }

        response = client.post("/api/v1/evaluate/pair", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_pair_item1_not_found(self, client, evaluation_setup):
        """Test pair evaluation with nonexistent first item."""
        request = {
            "item1_id": "nonexistent",
            "item2_id": "pants_1",
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/pair", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_pair_item2_not_found(self, client, evaluation_setup):
        """Test pair evaluation with nonexistent second item."""
        request = {
            "item1_id": "shirt_1",
            "item2_id": "nonexistent",
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/pair", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_pair_missing_fields(self, client, evaluation_setup):
        """Test pair evaluation with missing required fields."""
        # Missing item1_id
        response = client.post(
            "/api/v1/evaluate/pair",
            json={
                "item2_id": "pants_1",
                "catalog_name": "eval_catalog",
                "ruleset_name": "eval_rules",
            },
        )
        assert response.status_code == 422

        # Missing catalog_name
        response = client.post(
            "/api/v1/evaluate/pair",
            json={
                "item1_id": "shirt_1",
                "item2_id": "pants_1",
                "ruleset_name": "eval_rules",
            },
        )
        assert response.status_code == 422


class TestEvaluateMatrix:
    """Tests for POST /evaluate/matrix"""

    def test_evaluate_matrix_success(self, client, evaluation_setup):
        """Test evaluating full compatibility matrix."""
        request = {
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
            "include_self": False,
        }

        response = client.post("/api/v1/evaluate/matrix", json=request)

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_comparisons" in data
        assert "compatible_count" in data
        assert "compatibility_rate" in data

        # 4 items: C(4,2) = 6 pairs when include_self=False
        assert data["total_comparisons"] == 6

    def test_evaluate_matrix_include_self(self, client, evaluation_setup):
        """Test matrix evaluation including self-comparisons."""
        request = {
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
            "include_self": True,
        }

        response = client.post("/api/v1/evaluate/matrix", json=request)

        assert response.status_code == 200
        data = response.json()
        # 4 items: C(4,2) + 4 = 6 + 4 = 10 pairs when include_self=True
        assert data["total_comparisons"] == 10

    def test_evaluate_matrix_compatibility_stats(self, client, evaluation_setup):
        """Test that matrix includes compatibility statistics."""
        request = {
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
            "include_self": False,
        }

        response = client.post("/api/v1/evaluate/matrix", json=request)

        assert response.status_code == 200
        data = response.json()

        # Verify stats are calculated
        assert data["compatible_count"] >= 0
        assert 0.0 <= data["compatibility_rate"] <= 1.0

        # Verify compatibility_rate calculation
        if data["total_comparisons"] > 0:
            expected_rate = data["compatible_count"] / data["total_comparisons"]
            assert abs(data["compatibility_rate"] - expected_rate) < 0.001

    def test_evaluate_matrix_results_structure(self, client, evaluation_setup):
        """Test that matrix results have correct structure."""
        request = {
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
            "include_self": False,
        }

        response = client.post("/api/v1/evaluate/matrix", json=request)

        assert response.status_code == 200
        data = response.json()

        # Check structure of results
        for result in data["results"]:
            assert "item1_id" in result
            assert "item2_id" in result
            assert "compatible" in result
            assert "rules_evaluated" in result

    def test_evaluate_matrix_catalog_not_found(self, client, evaluation_setup):
        """Test matrix evaluation with nonexistent catalog."""
        request = {
            "catalog_name": "nonexistent",
            "ruleset_name": evaluation_setup["ruleset"]["name"],
            "include_self": False,
        }

        response = client.post("/api/v1/evaluate/matrix", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_matrix_ruleset_not_found(self, client, evaluation_setup):
        """Test matrix evaluation with nonexistent ruleset."""
        request = {
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": "nonexistent",
            "include_self": False,
        }

        response = client.post("/api/v1/evaluate/matrix", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_matrix_missing_fields(self, client):
        """Test matrix evaluation with missing required fields."""
        # Missing catalog_name
        response = client.post(
            "/api/v1/evaluate/matrix",
            json={"ruleset_name": "test_rules"},
        )
        assert response.status_code == 422

        # Missing ruleset_name
        response = client.post(
            "/api/v1/evaluate/matrix",
            json={"catalog_name": "test_catalog"},
        )
        assert response.status_code == 422


class TestEvaluateItem:
    """Tests for POST /evaluate/item"""

    def test_evaluate_item_success(self, client, evaluation_setup):
        """Test evaluating one item against all others."""
        request = {
            "item_id": "shirt_1",
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/item", json=request)

        assert response.status_code == 200
        data = response.json()

        # Should return list of comparison results
        assert isinstance(data, list)
        # shirt_1 compared against 3 other items
        assert len(data) == 3

    def test_evaluate_item_results_structure(self, client, evaluation_setup):
        """Test that item evaluation results have correct structure."""
        request = {
            "item_id": "shirt_1",
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/item", json=request)

        assert response.status_code == 200
        data = response.json()

        for result in data:
            assert "item1_id" in result
            assert "item2_id" in result
            assert "compatible" in result
            assert "rules_evaluated" in result
            # item1_id should always be the queried item
            assert result["item1_id"] == "shirt_1"

    def test_evaluate_item_compatibility_results(self, client, evaluation_setup):
        """Test item evaluation produces correct compatibility results."""
        request = {
            "item_id": "shirt_1",
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/item", json=request)

        assert response.status_code == 200
        data = response.json()

        # Check compatibility results
        # shirt_1 vs pants_1: should be compatible (different category, formality diff = 1)
        pants_result = next(r for r in data if r["item2_id"] == "pants_1")
        assert pants_result["compatible"] is True

        # shirt_1 vs shirt_2: should be incompatible (same category)
        shirt_result = next(r for r in data if r["item2_id"] == "shirt_2")
        assert shirt_result["compatible"] is False

    def test_evaluate_item_catalog_not_found(self, client, evaluation_setup):
        """Test item evaluation with nonexistent catalog."""
        request = {
            "item_id": "shirt_1",
            "catalog_name": "nonexistent",
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/item", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_item_ruleset_not_found(self, client, evaluation_setup):
        """Test item evaluation with nonexistent ruleset."""
        request = {
            "item_id": "shirt_1",
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": "nonexistent",
        }

        response = client.post("/api/v1/evaluate/item", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_item_not_found(self, client, evaluation_setup):
        """Test item evaluation with nonexistent item."""
        request = {
            "item_id": "nonexistent",
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/item", json=request)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_evaluate_item_single_item_catalog(self, client, setup_schema):
        """Test evaluating item in catalog with only one item."""
        # Create ruleset
        ruleset_response = client.post(
            "/api/v1/rulesets",
            json={
                "name": "single_test_rules",
                "version": "1.0.0",
                "schema_name": setup_schema["name"],
                "rules": [],
            },
        )
        assert ruleset_response.status_code == 201

        # Create catalog with one item
        catalog_response = client.post(
            "/api/v1/catalogs",
            json={
                "name": "single_test_catalog",
                "schema_name": setup_schema["name"],
            },
        )
        assert catalog_response.status_code == 201

        item_response = client.post(
            "/api/v1/catalogs/single_test_catalog/items",
            json={
                "item_id": "only_item",
                "name": "Only Item",
                "attributes": {"category": "shirt", "color": "blue"},
            },
        )
        assert item_response.status_code == 201

        request = {
            "item_id": "only_item",
            "catalog_name": "single_test_catalog",
            "ruleset_name": "single_test_rules",
        }

        response = client.post("/api/v1/evaluate/item", json=request)

        assert response.status_code == 200
        data = response.json()
        # Should return empty list (no other items to compare)
        assert len(data) == 0

    def test_evaluate_item_missing_fields(self, client):
        """Test item evaluation with missing required fields."""
        # Missing item_id
        response = client.post(
            "/api/v1/evaluate/item",
            json={
                "catalog_name": "test_catalog",
                "ruleset_name": "test_rules",
            },
        )
        assert response.status_code == 422

        # Missing catalog_name
        response = client.post(
            "/api/v1/evaluate/item",
            json={
                "item_id": "test_item",
                "ruleset_name": "test_rules",
            },
        )
        assert response.status_code == 422


class TestEvaluationHelperFunctions:
    """Tests for database-to-Rulate model conversion."""

    def test_pair_evaluation_converts_models_correctly(self, client, evaluation_setup):
        """Test that evaluation correctly converts DB models to Rulate models."""
        request = {
            "item1_id": "shirt_1",
            "item2_id": "pants_1",
            "catalog_name": evaluation_setup["catalog"]["name"],
            "ruleset_name": evaluation_setup["ruleset"]["name"],
        }

        response = client.post("/api/v1/evaluate/pair", json=request)

        # If this succeeds without errors, model conversion worked
        assert response.status_code == 200
        data = response.json()

        # Verify the evaluation used the correct data
        assert data["item1_id"] == "shirt_1"
        assert data["item2_id"] == "pants_1"

        # Verify rules were applied
        assert len(data["rules_evaluated"]) > 0
