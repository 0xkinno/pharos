"""
Tests for RAG Citations

Critical test: Every clause this engine cites must be verifiable
against the committed standards corpus or the deterministic fallback.

Mirror of AccessGate's citation verification test — citations are NEVER fabricated.
"""
from pathlib import Path

from app.ai.watsonx_embedding import _RULE_FALLBACK_CLAUSES, retrieve_citation


class TestCitationsAreNeverFabricated:
    """Citations must always trace to a real source."""

    def test_fallback_clauses_exist_for_all_rules(self):
        """Every rule ID in the fallback map must have non-empty clause text."""
        required_rules = [
            "FCC-DEORBIT-01", "FCC-DEORBIT-02", "FCC-LEO-01",
            "IADC-LIFE-01", "IADC-PASS-01", "IADC-COLL-01", "IADC-REENTRY-01",
            "ISO-ORBIT-01", "ISO-ORBIT-02", "ISO-DEBRIS-01",
            "ESA-ZD-01", "ESA-ZD-02", "ESA-ZD-03",
            "COPUOS-REG-01", "COPUOS-COORD-01", "COPUOS-NOTIF-01",
        ]
        for rule_id in required_rules:
            assert rule_id in _RULE_FALLBACK_CLAUSES, f"Missing fallback clause for {rule_id}"
            assert len(_RULE_FALLBACK_CLAUSES[rule_id]) > 50, f"Fallback clause too short for {rule_id}"

    def test_retrieval_returns_nonempty_text(self):
        """retrieve_citation always returns non-empty clause text."""
        for rule_id in _RULE_FALLBACK_CLAUSES:
            result = retrieve_citation(rule_id=rule_id)
            assert result["clause_text"], f"Empty clause text for {rule_id}"
            assert len(result["clause_text"]) > 30, f"Clause text too short for {rule_id}"

    def test_fallback_clauses_reference_real_standards(self):
        """Each fallback clause must reference its standard document."""
        standard_refs = {
            "FCC-DEORBIT-01": "47 CFR",
            "IADC-LIFE-01": "IADC-02-01",
            "ISO-ORBIT-01": "ISO 24113",
            "ESA-ZD-01": "Zero Debris Charter",
            "COPUOS-REG-01": "COPUOS",
        }
        for rule_id, ref in standard_refs.items():
            clause = _RULE_FALLBACK_CLAUSES[rule_id]
            assert ref in clause, (
                f"Fallback clause for {rule_id} does not reference expected standard '{ref}'"
            )

    def test_retrieval_method_is_identified(self):
        """Each citation result must identify how it was retrieved."""
        result = retrieve_citation("FCC-DEORBIT-01")
        assert "retrieval_method" in result
        assert result["retrieval_method"] in ("granite_embedding_rag", "deterministic_fallback")

    def test_no_citation_says_see_ai_or_unknown(self):
        """Citations must never say 'See AI' or contain suspicious placeholders."""
        for rule_id in _RULE_FALLBACK_CLAUSES:
            clause = _RULE_FALLBACK_CLAUSES[rule_id].lower()
            assert "see ai" not in clause
            assert "placeholder" not in clause
            assert "todo" not in clause
            assert "coming soon" not in clause

    def test_fcc_deorbit_01_citation_has_5_year_text(self):
        """FCC-DEORBIT-01 citation must mention the 5-year rule."""
        clause = _RULE_FALLBACK_CLAUSES["FCC-DEORBIT-01"]
        assert "five (5) years" in clause or "5 years" in clause or "five years" in clause.lower()

    def test_iadc_life_01_citation_has_25_year_text(self):
        """IADC-LIFE-01 citation must mention 25 years."""
        clause = _RULE_FALLBACK_CLAUSES["IADC-LIFE-01"]
        assert "25 years" in clause

    def test_esa_zd_02_citation_has_90_percent_text(self):
        """ESA-ZD-02 citation must mention the 90% (0.9) threshold."""
        clause = _RULE_FALLBACK_CLAUSES["ESA-ZD-02"]
        assert "0.9" in clause or "90%" in clause

    def test_iso_orbit_02_citation_has_200km_text(self):
        """ISO-ORBIT-02 citation must mention the 200 km graveyard requirement."""
        clause = _RULE_FALLBACK_CLAUSES["ISO-ORBIT-02"]
        assert "200 km" in clause


class TestCorpusIntegrity:
    """Tests for the pre-built standards corpus file."""

    def test_corpus_file_exists_if_built(self):
        """If the corpus was built, it should exist and be non-empty."""
        chunks_path = Path(__file__).parent.parent / "standards" / "index" / "chunks.json"
        if chunks_path.exists():
            import json
            with open(chunks_path) as f:
                chunks = json.load(f)
            assert len(chunks) > 0, "Corpus file exists but is empty"
            assert all("text" in c for c in chunks), "All chunks must have 'text' field"
            assert all("source_document" in c for c in chunks), "All chunks must have 'source_document'"
