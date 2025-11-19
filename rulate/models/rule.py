"""
Rule models for defining compatibility logic.

Rules define when two objects are compatible or incompatible based on
their attributes and relationships.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class RuleType(str, Enum):
    """Types of rules that can be defined."""

    EXCLUSION = "exclusion"  # Items are incompatible if condition is true
    REQUIREMENT = "requirement"  # Items are only compatible if condition is true
    CUSTOM = "custom"  # Custom expression-based rule


class Rule(BaseModel):
    """
    A rule defines a compatibility constraint between two items.

    Rules consist of a type (exclusion/requirement) and a condition
    (boolean logic expression) that evaluates against item pairs.

    Examples:
        # Exclusion: can't wear two items on same body zone
        Rule(
            name="same_body_zone_exclusion",
            type=RuleType.EXCLUSION,
            condition={"equals": {"field": "body_zone"}}
        )

        # Requirement: formality must match
        Rule(
            name="formality_matching",
            type=RuleType.REQUIREMENT,
            condition={"abs_diff": {"field": "formality", "max": 1}}
        )
    """

    name: str = Field(..., description="Unique name of the rule")
    type: RuleType = Field(..., description="Type of rule (exclusion/requirement/custom)")
    description: Optional[str] = Field(None, description="Human-readable description")
    condition: Dict[str, Any] = Field(
        ..., description="Condition expression (operator tree as dict)"
    )
    enabled: bool = Field(default=True, description="Whether this rule is active")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure rule name is valid."""
        if not v or not v.strip():
            raise ValueError("Rule name cannot be empty")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Rule name must be alphanumeric (underscores and hyphens allowed)")
        return v

    @field_validator("condition")
    @classmethod
    def validate_condition(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Basic validation of condition structure."""
        if not v:
            raise ValueError("Condition cannot be empty")
        if not isinstance(v, dict):
            raise ValueError("Condition must be a dictionary")
        return v


class RuleSet(BaseModel):
    """
    A collection of rules for evaluating compatibility in a domain.

    A RuleSet is associated with a specific schema and contains all the
    rules that should be applied when comparing items.

    Example:
        wardrobe_rules = RuleSet(
            name="wardrobe_rules_v1",
            version="1.0.0",
            schema_ref="wardrobe_v1",
            rules=[
                Rule(name="same_zone", type=RuleType.EXCLUSION, ...),
                Rule(name="formality", type=RuleType.REQUIREMENT, ...),
            ]
        )
    """

    name: str = Field(..., description="Unique name of the ruleset")
    version: str = Field(..., description="Semantic version of the ruleset")
    description: Optional[str] = Field(None, description="Human-readable description")
    schema_ref: str = Field(..., description="Name of the schema this ruleset applies to")
    rules: List[Rule] = Field(default_factory=list, description="List of rules in this ruleset")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure ruleset name is valid."""
        if not v or not v.strip():
            raise ValueError("RuleSet name cannot be empty")
        return v

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Ensure version follows semantic versioning."""
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError("Version must be in format 'major.minor.patch' (e.g., '1.0.0')")
        for part in parts:
            if not part.isdigit():
                raise ValueError("Version components must be integers")
        return v

    def get_rule(self, name: str) -> Optional[Rule]:
        """
        Get a rule by name.

        Args:
            name: The name of the rule to retrieve

        Returns:
            The Rule object, or None if not found
        """
        for rule in self.rules:
            if rule.name == name:
                return rule
        return None

    def get_active_rules(self) -> List[Rule]:
        """
        Get all enabled rules.

        Returns:
            List of rules where enabled=True
        """
        return [rule for rule in self.rules if rule.enabled]

    def get_exclusion_rules(self) -> List[Rule]:
        """Get all active exclusion rules."""
        return [r for r in self.get_active_rules() if r.type == RuleType.EXCLUSION]

    def get_requirement_rules(self) -> List[Rule]:
        """Get all active requirement rules."""
        return [r for r in self.get_active_rules() if r.type == RuleType.REQUIREMENT]

    def get_custom_rules(self) -> List[Rule]:
        """Get all active custom rules."""
        return [r for r in self.get_active_rules() if r.type == RuleType.CUSTOM]
