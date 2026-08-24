# PHAROS Architecture

## System Overview

PHAROS is a satellite compliance intelligence platform with three layers:

1. **Backend Engine (Python/FastAPI)** — Deterministic compliance checking
2. **AI Layer (IBM Granite)** — Plain-language explanation and citations
3. **Frontend (Next.js)** — Professional dark-theme compliance dashboard

## Architecture Principle

**The engine DETECTS. IBM Granite EXPLAINS.**

Compliance decisions are ALWAYS deterministic — never AI-determined. The AI layer
adds: plain-language reports, semantic citation retrieval, content safety screening.

## Component Map

```
backend/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── api/
│   │   ├── routes.py            # All REST endpoints
│   │   ├── judges.py            # /api/judges transparency
│   │   └── demo.py              # Pre-computed demo data
│   ├── core/config.py           # Settings (pydantic-settings)
│   ├── models/
│   │   ├── satellite.py         # Orbital data models
│   │   ├── compliance.py        # ComplianceReport, RuleResult
│   │   └── standards.py        # Rules registry models
│   ├── services/
│   │   ├── celestrak_client.py  # CelesTrak GP API client
│   │   ├── orbital_propagator.py # SGP4 integration
│   │   ├── lifetime_estimator.py # King-Hele decay model
│   │   ├── compliance_engine.py  # Master orchestrator
│   │   ├── report_generator.py  # Granite Instruct wrapper
│   │   └── rag_service.py       # Citation retrieval
│   ├── evaluators/              # One evaluator per standards body
│   │   ├── fcc.py              # FCC 47 CFR Part 25
│   │   ├── iadc.py             # IADC-02-01 Rev 3
│   │   ├── iso24113.py         # ISO 24113:2019
│   │   ├── esa_zero_debris.py  # ESA Zero Debris Charter
│   │   └── copuos.py           # UN COPUOS LTS Guidelines
│   ├── exporters/
│   │   ├── json_export.py      # JSON report serializer
│   │   └── pdf_export.py       # PDF report generator (ReportLab)
│   └── ai/
│       ├── watsonx_client.py    # IBM watsonx.ai SDK wrapper
│       ├── watsonx_embedding.py # Granite Embedding + RAG
│       └── watsonx_guardian.py  # Granite Guardian screening
├── rules/
│   └── rules_registry.yaml     # All rules with metadata
├── standards/
│   ├── raw/                    # Original documents
│   ├── parsed/                 # Docling-parsed markdown
│   └── index/chunks.json       # Pre-built embedding index
```

## Data Flow

```
CelesTrak GP API
        ↓
  SatelliteData (Pydantic model)
        ↓
  orbital_propagator.py  →  OrbitalElements
                              ↓
  lifetime_estimator.py  →  estimated_lifetime_years
                              ↓
  compliance_engine.py   →  [evaluate all 16 rules]
                              ↓
  rule_results (pass/fail/flag with standard_clause citations)
        ↓
  rag_service.py         →  retrieved_clause_text (Granite Embedding)
        ↓
  report_generator.py    →  ai_report_text (Granite Instruct)
        ↓
  watsonx_guardian.py    →  safety screened ✓
        ↓
  ComplianceReport (API response)
        ↓
  Next.js Frontend
```

## Key Design Decisions

### 1. Deterministic compliance, AI explanation
- Rule evaluators use pure Python math — no LLM in the decision path
- Granite adds: prose summaries, semantic citations, safety screening
- API-deletion proof: delete watsonx.ai, engine still produces reports

### 2. Pre-built standards corpus
- Docling parses regulatory PDFs once, commits output to repo
- Embedding index built once, committed to repo
- No rebuild at request time → sub-second citation retrieval

### 3. Graceful fallback at every layer
- Granite Instruct unavailable → structured text report
- Granite Embedding unavailable → deterministic rule-to-clause mapping
- Granite Guardian unavailable → unscreened AI content not served (conservative)
- CelesTrak unavailable → demo data endpoint always works

### 4. Rule evaluator pattern
Each evaluator:
- Takes satellite orbital parameters as input
- Returns RuleResult(rule_id, status, message, value, threshold, unit, standard_clause)
- Cites the exact standard clause
- Never uses AI for the compliance decision

## Last Updated

Built by IBM Bob — IBM AI Builders Challenge August 2026
