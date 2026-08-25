"""
Pydantic models for regulatory standards and rules.
"""
from typing import Any

from pydantic import BaseModel, Field


class RuleThreshold(BaseModel):
    """Numeric thresholds for a rule."""
    max_years: float | None = None
    min_years: float | None = None
    max_altitude_km: float | None = None
    min_altitude_km: float | None = None
    max_casualty_risk: float | None = None
    max_probability: float | None = None
    min_disposal_probability: float | None = None
    min_graveyard_km_above_geo: float | None = None


class RuleDefinition(BaseModel):
    """A single coded rule from the registry."""
    id: str = Field(..., description="e.g. FCC-DEORBIT-01")
    standard: str = Field(..., description="Full standard citation")
    body: str = Field(..., description="Regulatory body")
    title: str
    description: str
    threshold: RuleThreshold | None = None
    evaluator: str = Field(..., description="Python function path")
    severity: str = Field(..., description="critical, high, medium, low")


class StandardsRegistry(BaseModel):
    """The full rules registry loaded from YAML."""
    rules: list[RuleDefinition]


class StandardsCorpusChunk(BaseModel):
    """A single chunk from the parsed standards corpus."""
    id: str
    source_document: str
    standard_body: str
    section: str | None = None
    text: str
    embedding: list[float] | None = None  # Stored as float array


class CitationResult(BaseModel):
    """Result from RAG citation retrieval."""
    rule_id: str
    query: str
    retrieved_chunks: list[dict[str, Any]] = Field(default_factory=list)
    top_clause_text: str | None = None
    top_clause_source: str | None = None
    similarity_score: float | None = None
