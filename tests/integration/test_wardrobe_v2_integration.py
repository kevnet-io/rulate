"""
Integration tests for wardrobe v2 schema, rules, and catalog.

Tests the complete evaluation flow with the gender-agnostic wardrobe domain,
including the new part_layer_list dimension and PartLayerConflictOperator.
"""

import json
from pathlib import Path

import pytest

from rulate.engine.evaluator import evaluate_matrix, evaluate_pair
from rulate.models.catalog import Catalog
from rulate.models.cluster import ClusterRuleSet
from rulate.models.rule import RuleSet
from rulate.models.schema import Schema

# Path to the v2 wardrobe export file
EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples" / "wardrobe"
V2_JSON_PATH = EXAMPLES_DIR / "v2.json"


@pytest.fixture
def v2_data():
    """Load the v2 export JSON file."""
    with open(V2_JSON_PATH) as f:
        return json.load(f)


@pytest.fixture
def schema_v2(v2_data):
    """Load the v2 wardrobe schema from export JSON."""
    schema_dict = v2_data["schemas"][0]
    return Schema(**schema_dict)


@pytest.fixture
def rules_v2(v2_data):
    """Load the v2 wardrobe pairwise rules from export JSON."""
    ruleset_dict = v2_data["rulesets"][0]
    return RuleSet(**ruleset_dict)


@pytest.fixture
def cluster_rules_v2(v2_data, schema_v2, rules_v2):
    """Load the v2 wardrobe cluster rules from export JSON."""
    cluster_ruleset_dict = v2_data["cluster_rulesets"][0]
    ruleset = ClusterRuleSet(**cluster_ruleset_dict)
    # Set schema and pairwise ruleset references
    ruleset._schema = schema_v2
    ruleset._pairwise_ruleset = rules_v2
    return ruleset


@pytest.fixture
def catalog_v2(v2_data):
    """Load the v2 wardrobe catalog from export JSON."""
    catalog_dict = v2_data["catalogs"][0]
    return Catalog(**catalog_dict)


class TestSchemaV2Loading:
    """Test that the v2 schema loads correctly."""

    def test_schema_loads(self, schema_v2):
        """Test schema loads without errors."""
        assert schema_v2.name == "wardrobe_v2"
        assert schema_v2.version == "2.0.0"

    def test_schema_has_coverage_layers_dimension(self, schema_v2):
        """Test schema includes coverage_layers dimension."""
        coverage_dim = schema_v2.get_dimension("coverage_layers")
        assert coverage_dim is not None
        assert coverage_dim.type.value == "part_layer_list"
        assert coverage_dim.required is True

    def test_schema_has_part_vocabulary(self, schema_v2):
        """Test coverage_layers dimension has body part vocabulary."""
        coverage_dim = schema_v2.get_dimension("coverage_layers")
        assert coverage_dim.part_vocabulary is not None
        assert len(coverage_dim.part_vocabulary) > 20
        assert "chest" in coverage_dim.part_vocabulary
        assert "upper_leg" in coverage_dim.part_vocabulary
        assert "lower_leg" in coverage_dim.part_vocabulary


class TestRulesV2Loading:
    """Test that the v2 pairwise rules load correctly."""

    def test_rules_load(self, rules_v2):
        """Test pairwise rules load without errors."""
        assert rules_v2.name == "wardrobe_rules_v2"
        assert rules_v2.version == "2.0.0"

    def test_has_coverage_layer_conflict_rule(self, rules_v2):
        """Test rules include coverage_layer_conflict rule."""
        rule_names = [rule.name for rule in rules_v2.rules]
        assert "coverage_layer_conflict" in rule_names

    def test_has_same_category_exclusion_rule(self, rules_v2):
        """Test rules include same_category_exclusion rule."""
        rule_names = [rule.name for rule in rules_v2.rules]
        assert "same_category_exclusion" in rule_names

    def test_no_formality_or_season_rules(self, rules_v2):
        """Test that formality and season rules were moved to cluster rules."""
        rule_names = [rule.name for rule in rules_v2.rules]
        # These should be in cluster rules now
        assert "formality_matching" not in rule_names
        assert "season_compatibility" not in rule_names


class TestClusterRulesV2Loading:
    """Test that the v2 cluster rules load correctly."""

    def test_cluster_rules_load(self, cluster_rules_v2):
        """Test cluster rules load without errors."""
        assert cluster_rules_v2.name == "wardrobe_cluster_rules_v2"
        assert cluster_rules_v2.version == "2.0.0"

    def test_has_formality_consistency_rule(self, cluster_rules_v2):
        """Test cluster rules include formality_consistency."""
        rule_names = [rule.name for rule in cluster_rules_v2.rules]
        assert "formality_consistency" in rule_names

    def test_has_season_consistency_rule(self, cluster_rules_v2):
        """Test cluster rules include season_consistency."""
        rule_names = [rule.name for rule in cluster_rules_v2.rules]
        assert "season_consistency" in rule_names


class TestCatalogV2Loading:
    """Test that the v2 catalog loads and validates correctly."""

    def test_catalog_loads(self, catalog_v2):
        """Test catalog loads without errors."""
        assert catalog_v2.name == "gender_agnostic_wardrobe_v2"
        assert len(catalog_v2.items) >= 50

    def test_all_items_validate(self, catalog_v2, schema_v2):
        """Test all catalog items validate against schema."""
        for item in catalog_v2.items:
            # Should not raise an exception
            schema_v2.validate_attributes(item.attributes)

    def test_catalog_has_diverse_categories(self, catalog_v2):
        """Test catalog includes diverse clothing categories."""
        categories = set(item.get_attribute("category") for item in catalog_v2.items)

        # Should have items from each major category
        assert "bra" in categories  # Feminine-leaning undergarment
        assert "boxers" in categories  # Masculine-leaning undergarment
        assert "dress" in categories  # Feminine-leaning garment
        assert "shirt" in categories  # Masculine-leaning garment
        assert "tights" in categories  # Feminine-leaning hosiery
        assert "jewelry" in categories or "necklace" in categories  # Accessories

    def test_catalog_has_mixed_layer_dress(self, catalog_v2):
        """Test catalog includes dress with mixed layer values."""
        # dress_001 (Bodycon Dress) should have different layers for different parts
        bodycon = catalog_v2.get_item("dress_001")
        assert bodycon is not None

        coverage_layers = bodycon.get_attribute("coverage_layers")
        assert len(coverage_layers) >= 2  # At least two different layer tuples


class TestPairwiseEvaluation:
    """Test pairwise compatibility evaluation with v2 rules."""

    def test_compatible_bra_and_dress(self, catalog_v2, rules_v2):
        """Test that bra and dress are compatible (different layers)."""
        bra = catalog_v2.get_item("bra_001")
        dress = catalog_v2.get_item("dress_001")

        result = evaluate_pair(bra, dress, rules_v2)
        assert result.compatible is True

    def test_compatible_tights_and_dress(self, catalog_v2, rules_v2):
        """Test that tights and dress are compatible (different layers)."""
        tights = catalog_v2.get_item("tights_001")
        dress = catalog_v2.get_item("dress_001")

        result = evaluate_pair(tights, dress, rules_v2)
        assert result.compatible is True

    def test_incompatible_same_category(self, catalog_v2, rules_v2):
        """Test that two items of same category are incompatible."""
        dress1 = catalog_v2.get_item("dress_001")
        dress2 = catalog_v2.get_item("dress_002")

        result = evaluate_pair(dress1, dress2, rules_v2)
        assert result.compatible is False

        # Should fail on same_category_exclusion rule
        failed_rules = [r.rule_name for r in result.rules_evaluated if not r.passed]
        assert "same_category_exclusion" in failed_rules

    def test_incompatible_same_layer_overlap(self, catalog_v2, rules_v2):
        """Test that items with same layer on same parts are incompatible."""
        # Two pants should conflict (same category and same layer on legs)
        pants1 = catalog_v2.get_item("pants_001")
        pants2 = catalog_v2.get_item("pants_002")

        result = evaluate_pair(pants1, pants2, rules_v2)
        assert result.compatible is False

    def test_compatible_shirt_and_pants(self, catalog_v2, rules_v2):
        """Test that shirt and pants are compatible (no overlap)."""
        shirt = catalog_v2.get_item("shirt_001")
        pants = catalog_v2.get_item("pants_001")

        result = evaluate_pair(shirt, pants, rules_v2)
        assert result.compatible is True

    def test_compatible_layering_shirt_and_sweater(self, catalog_v2, rules_v2):
        """Test that shirt (layer 2.0) and sweater (layer 3.0) are compatible."""
        shirt = catalog_v2.get_item("shirt_001")
        sweater = catalog_v2.get_item("sweater_001")

        result = evaluate_pair(shirt, sweater, rules_v2)
        assert result.compatible is True

    def test_compatible_sweater_and_blazer(self, catalog_v2, rules_v2):
        """Test that sweater (layer 3.0) and blazer (layer 4.0) are compatible."""
        sweater = catalog_v2.get_item("sweater_001")
        blazer = catalog_v2.get_item("blazer_001")

        result = evaluate_pair(sweater, blazer, rules_v2)
        assert result.compatible is True

    def test_compatible_undershirt_and_shirt(self, catalog_v2, rules_v2):
        """Test that undershirt (layer 1.0) and shirt (layer 2.0) are compatible."""
        undershirt = catalog_v2.get_item("undershirt_001")
        shirt = catalog_v2.get_item("shirt_001")

        result = evaluate_pair(undershirt, shirt, rules_v2)
        assert result.compatible is True


class TestMatrixEvaluation:
    """Test compatibility matrix generation."""

    def test_matrix_evaluation_runs(self, catalog_v2, rules_v2, schema_v2):
        """Test that matrix evaluation completes without errors."""
        # evaluate_matrix expects a Catalog object
        matrix = evaluate_matrix(catalog_v2, rules_v2, schema_v2)

        assert matrix is not None
        assert len(matrix.results) > 0
        assert matrix.catalog_name == "gender_agnostic_wardrobe_v2"


class TestSpecificScenarios:
    """Test specific edge cases and important scenarios."""

    def test_accessories_compatible_with_outfits(self, catalog_v2, rules_v2):
        """Test that accessories (tie, belt, watch) are compatible with clothing."""
        shirt = catalog_v2.get_item("shirt_001")
        tie = catalog_v2.get_item("tie_001")
        belt = catalog_v2.get_item("belt_001")
        watch = catalog_v2.get_item("watch_001")

        # Tie should be compatible with shirt
        assert evaluate_pair(shirt, tie, rules_v2).compatible is True

        # Belt should be compatible with shirt
        assert evaluate_pair(shirt, belt, rules_v2).compatible is True

        # Watch should be compatible with shirt
        assert evaluate_pair(shirt, watch, rules_v2).compatible is True

    def test_footwear_compatible_with_clothing(self, catalog_v2, rules_v2):
        """Test that footwear is compatible with clothing."""
        pants = catalog_v2.get_item("pants_001")
        shoes = catalog_v2.get_item("shoes_001")
        heels = catalog_v2.get_item("heels_001")
        sneakers = catalog_v2.get_item("sneakers_001")

        # All footwear should be compatible with pants (no overlap)
        assert evaluate_pair(pants, shoes, rules_v2).compatible is True
        assert evaluate_pair(pants, heels, rules_v2).compatible is True
        assert evaluate_pair(pants, sneakers, rules_v2).compatible is True

    def test_socks_under_shoes(self, catalog_v2, rules_v2):
        """Test that socks (layer 1.0) are compatible with shoes (layer 2.0)."""
        socks = catalog_v2.get_item("socks_001")
        shoes = catalog_v2.get_item("shoes_001")

        result = evaluate_pair(socks, shoes, rules_v2)
        assert result.compatible is True

    def test_multiple_jewelry_items_compatible(self, catalog_v2, rules_v2):
        """Test that different jewelry items can be worn together."""
        necklace = catalog_v2.get_item("necklace_001")
        earrings = catalog_v2.get_item("earrings_001")
        bracelet = catalog_v2.get_item("bracelet_001")

        # Different jewelry types should be compatible (different body parts)
        assert evaluate_pair(necklace, earrings, rules_v2).compatible is True
        assert evaluate_pair(necklace, bracelet, rules_v2).compatible is True
        assert evaluate_pair(earrings, bracelet, rules_v2).compatible is True

    def test_complete_feminine_outfit(self, catalog_v2, rules_v2):
        """Test a complete feminine outfit is all compatible."""
        outfit_ids = [
            "bra_001",  # Sports Bra
            "tights_001",  # Sheer Tights
            "dress_003",  # Little Black Dress
            "heels_001",  # Black Stiletto Heels
        ]
        items = [catalog_v2.get_item(item_id) for item_id in outfit_ids]

        # Check all pairs are compatible
        for i, item1 in enumerate(items):
            for item2 in items[i + 1 :]:
                result = evaluate_pair(item1, item2, rules_v2)
                assert (
                    result.compatible is True
                ), f"{item1.name} and {item2.name} should be compatible"

    def test_complete_masculine_outfit(self, catalog_v2, rules_v2):
        """Test a complete masculine outfit is all compatible."""
        outfit_ids = [
            "boxers_001",  # Boxer Briefs
            "undershirt_001",  # Tank Undershirt
            "shirt_001",  # White Oxford Shirt
            "pants_001",  # Black Dress Pants
            "belt_001",  # Leather Belt
            "socks_001",  # Ankle Socks
            "shoes_001",  # Brown Dress Shoes
            "tie_001",  # Silk Neck Tie
        ]
        items = [catalog_v2.get_item(item_id) for item_id in outfit_ids]

        # Check all pairs are compatible
        for i, item1 in enumerate(items):
            for item2 in items[i + 1 :]:
                result = evaluate_pair(item1, item2, rules_v2)
                assert (
                    result.compatible is True
                ), f"{item1.name} and {item2.name} should be compatible"

    def test_winter_layering_outfit(self, catalog_v2, rules_v2):
        """Test a winter layering outfit with multiple layers."""
        outfit_ids = [
            "undershirt_001",  # Tank Undershirt (layer 1.0)
            "shirt_001",  # Oxford Shirt (layer 2.0)
            "sweater_001",  # Sweater (layer 3.0)
            "coat_001",  # Wool Peacoat (layer 4.5)
            "pants_001",  # Dress Pants (layer 2.0)
            "scarf_001",  # Wool Scarf (layer 4.2)
            "gloves_001",  # Leather Gloves (layer 3.5)
        ]
        items = [catalog_v2.get_item(item_id) for item_id in outfit_ids]

        # Check all pairs are compatible
        for i, item1 in enumerate(items):
            for item2 in items[i + 1 :]:
                result = evaluate_pair(item1, item2, rules_v2)
                assert (
                    result.compatible is True
                ), f"{item1.name} and {item2.name} should be compatible in winter layering"
