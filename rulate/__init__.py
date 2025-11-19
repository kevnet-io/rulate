"""
Rulate - A generic rule-based comparison engine.

This package provides tools for evaluating relationships between pairs of objects
based on configurable schemas and rules.
"""

__version__ = "0.1.0"

from rulate.models.catalog import Catalog, Item
from rulate.models.evaluation import ComparisonResult, RuleEvaluation
from rulate.models.rule import Rule, RuleSet, RuleType
from rulate.models.schema import Dimension, DimensionType, Schema

__all__ = [
    "Schema",
    "Dimension",
    "DimensionType",
    "Rule",
    "RuleSet",
    "RuleType",
    "Item",
    "Catalog",
    "RuleEvaluation",
    "ComparisonResult",
]
