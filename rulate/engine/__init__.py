"""
Rule evaluation engine.

This module provides the core evaluation functionality for comparing items
based on rules and schemas.
"""

from rulate.engine.condition_evaluator import evaluate_condition, validate_condition
from rulate.engine.evaluator import (
    evaluate_item_against_catalog,
    evaluate_matrix,
    evaluate_pair,
)

__all__ = [
    "evaluate_pair",
    "evaluate_matrix",
    "evaluate_item_against_catalog",
    "evaluate_condition",
    "validate_condition",
]
