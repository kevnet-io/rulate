"""
SQLAlchemy database models for storing rulate configurations.
"""

import json
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class SchemaDB(Base):
    """Database model for Schema storage."""

    __tablename__ = "schemas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    version = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    dimensions_json = Column(Text, nullable=False)  # JSON serialized list of dimensions
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    rulesets = relationship("RuleSetDB", back_populates="schema", cascade="all, delete-orphan")
    catalogs = relationship("CatalogDB", back_populates="schema", cascade="all, delete-orphan")

    def get_dimensions(self) -> list[dict[str, Any]]:
        """Parse dimensions from JSON."""
        return json.loads(self.dimensions_json)

    def set_dimensions(self, value: list[dict[str, Any]]) -> None:
        """Serialize dimensions to JSON."""
        self.dimensions_json = json.dumps(value)


class RuleSetDB(Base):
    """Database model for RuleSet storage."""

    __tablename__ = "rulesets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    version = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    schema_id = Column(Integer, ForeignKey("schemas.id"), nullable=False)
    rules_json = Column(Text, nullable=False)  # JSON serialized list of rules
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    schema = relationship("SchemaDB", back_populates="rulesets")

    def get_rules(self) -> list[dict[str, Any]]:
        """Parse rules from JSON."""
        return json.loads(self.rules_json)

    def set_rules(self, value: list[dict[str, Any]]) -> None:
        """Serialize rules to JSON."""
        self.rules_json = json.dumps(value)


class ClusterRuleSetDB(Base):
    """Database model for ClusterRuleSet storage."""

    __tablename__ = "cluster_rulesets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    version = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    schema_id = Column(Integer, ForeignKey("schemas.id"), nullable=False)
    pairwise_ruleset_id = Column(Integer, ForeignKey("rulesets.id"), nullable=False)
    rules_json = Column(Text, nullable=False)  # JSON serialized list of cluster rules
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    schema = relationship("SchemaDB")
    pairwise_ruleset = relationship("RuleSetDB")

    def get_rules(self) -> list[dict[str, Any]]:
        """Parse cluster rules from JSON."""
        return json.loads(self.rules_json)

    def set_rules(self, value: list[dict[str, Any]]) -> None:
        """Serialize cluster rules to JSON."""
        self.rules_json = json.dumps(value)


class CatalogDB(Base):
    """Database model for Catalog storage."""

    __tablename__ = "catalogs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    schema_id = Column(Integer, ForeignKey("schemas.id"), nullable=False)
    metadata_json = Column(Text, nullable=True)  # JSON serialized metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    schema = relationship("SchemaDB", back_populates="catalogs")
    items = relationship("ItemDB", back_populates="catalog", cascade="all, delete-orphan")

    def get_metadata(self) -> dict[str, Any]:
        """Parse metadata from JSON."""
        if self.metadata_json:
            return json.loads(self.metadata_json)
        return {}

    def set_metadata(self, value: dict[str, Any]) -> None:
        """Serialize metadata to JSON."""
        self.metadata_json = json.dumps(value) if value else None


class ItemDB(Base):
    """Database model for Item storage."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(String(255), nullable=False, index=True)  # User-facing ID
    name = Column(String(255), nullable=False)
    catalog_id = Column(Integer, ForeignKey("catalogs.id"), nullable=False)
    attributes_json = Column(Text, nullable=False)  # JSON serialized attributes
    metadata_json = Column(Text, nullable=True)  # JSON serialized metadata
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    catalog = relationship("CatalogDB", back_populates="items")

    def get_attributes(self) -> dict[str, Any]:
        """Parse attributes from JSON."""
        return json.loads(self.attributes_json)

    def set_attributes(self, value: dict[str, Any]) -> None:
        """Serialize attributes to JSON."""
        self.attributes_json = json.dumps(value)

    def get_metadata(self) -> dict[str, Any]:
        """Parse metadata from JSON."""
        if self.metadata_json:
            return json.loads(self.metadata_json)
        return {}

    def set_metadata(self, value: dict[str, Any]) -> None:
        """Serialize metadata to JSON."""
        self.metadata_json = json.dumps(value) if value else None
