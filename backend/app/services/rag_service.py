"""
RAG Service — Standards Corpus Citation Retrieval

Wraps the embedding service to provide citation retrieval for the
compliance engine. Every compliance flag retrieves the exact standard
clause by semantic meaning using Granite Embedding.
"""
from __future__ import annotations

import logging

from app.ai.watsonx_embedding import enrich_rule_results_with_citations, retrieve_citation
from app.models.compliance import RuleResult
from app.models.standards import CitationResult

logger = logging.getLogger(__name__)


def get_citation_for_rule(rule_id: str, context: str = None) -> CitationResult:
    """
    Get the most relevant standard clause for a rule ID.

    Parameters
    ----------
    rule_id : str
        Rule identifier (e.g., "FCC-DEORBIT-01")
    context : str, optional
        Additional context to improve retrieval relevance

    Returns
    -------
    CitationResult
    """
    query = f"{rule_id} {context or ''}".strip()
    citation = retrieve_citation(rule_id=rule_id, query=query)

    return CitationResult(
        rule_id=rule_id,
        query=query,
        retrieved_chunks=[citation],
        top_clause_text=citation.get("clause_text"),
        top_clause_source=citation.get("source"),
        similarity_score=citation.get("similarity_score"),
    )


def enrich_report_with_citations(rule_results: list[RuleResult]) -> list[RuleResult]:
    """
    Add RAG-retrieved citation text to each rule result in-place.
    """
    return enrich_rule_results_with_citations(rule_results)
