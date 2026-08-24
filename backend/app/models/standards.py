"""
Pydantic models for regulatory standards and rules.
"""
from typing import Optional, Any
from pydantic import BaseModel, Field


class RuleThreshold(BaseModel):
    """Numeric thresholds for a rule."""
    max_years: Optional[float] = None
    min_years: Optional[float] = None
    max_altitude_km: Optional[float] = None
    min_altitude_km: Optional[float] = None
    max_casualty_risk: Optional[float] = None
    max_probability: Optional[float] = None
    min_disposal_probability: Optional[float] = None
    min_graveyard_km_above_geo: Optional[float] = None


class RuleDefinition(BaseModel):
    """A single coded rule from the registry."""
    id: str = Field(..., description="e.g. FCC-DEORBIT-01")
    standard: str = Field(..., description="Full standard citation")
    body: str = Field(..., description="Regulatory body")
    title: str
    description: str
    threshold: Optional[RuleThreshold] = None
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
    section: Optional[str] = None
    text: str
    embedding: Optional[list[float]] = None  # Stored as float array


class CitationResult(BaseModel):
    """Result from RAG citation retrieval."""
    rule_id: str
    query: str
    retrieved_chunks: list[dict[str, Any]] = Field(default_factory=list)
    top_clause_text: Optional[str] = None
    top_clause_source: Optional[str] = None
    similarity_score: Optional[float] = None
