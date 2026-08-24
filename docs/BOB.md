# PHAROS — IBM Bob Usage Log

This file documents every IBM Bob session used to build PHAROS.

## Session 1 — Full Build

**Date:** IBM AI Builders Challenge August 2026
**Mode:** Agent mode

### What Bob Built

1. Read and analyzed `pharos_instruction.md` in full
2. Designed the complete project architecture (3-layer: backend/AI/frontend)
3. Created the full directory structure (60+ directories)
4. Built all Pydantic models: SatelliteData, OrbitalElements, ComplianceReport, RuleResult
5. Built pydantic-settings Config with watsonx credentials
6. Implemented CelesTrak GP API client with in-memory caching
7. Implemented SGP4 orbital propagation service using python-sgp4 (Vallado et al.)
8. Implemented King-Hele atmospheric decay model for orbital lifetime estimation
   - Integrated 3-solar-activity-level density table (low/moderate/high)
   - Eccentricity correction factor
   - Altitude-stepping integration for accuracy
9. Built all 5 rule evaluator modules:
   - `fcc.py`: FCC-DEORBIT-01 (5-year rule), FCC-DEORBIT-02 (casualty risk), FCC-LEO-01
   - `iadc.py`: IADC-LIFE-01 (25-year), IADC-PASS-01 (passivation), IADC-COLL-01 (collision prob), IADC-REENTRY-01
   - `iso24113.py`: ISO-ORBIT-01 (LEO protected region), ISO-ORBIT-02 (GEO disposal), ISO-DEBRIS-01
   - `esa_zero_debris.py`: ESA-ZD-01, ESA-ZD-02 (disposal probability), ESA-ZD-03
   - `copuos.py`: COPUOS-REG-01 (registration), COPUOS-COORD-01 (data sharing), COPUOS-NOTIF-01
10. Built the rules registry YAML with 16 rules, metadata, thresholds, severity levels
11. Built the compliance engine orchestrator (runs all rules, handles orbit-type filtering)
12. Implemented IBM watsonx.ai client with token caching (55-minute IAM token lifetime)
13. Implemented Granite Embedding RAG service:
    - Hard-coded deterministic clause mapping (API-deletion-proof fallback)
    - sentence-transformers integration for local Granite Embedding
    - Corpus chunk loading and cosine similarity search
14. Implemented Granite Instruct report generator:
    - Prompt engineering for 3-paragraph compliance assessments
    - Structured text fallback when API unavailable
15. Implemented Granite Guardian content safety screening
16. Built the standards corpus pipeline (parse_standards.py with full regulatory text)
17. Built the embedding index builder (build_index.py)
18. Built FastAPI REST API with all 8 endpoint groups
19. Built /api/judges transparency endpoint (mirrors AccessGate pattern)
20. Built /api/demo pre-computed dataset (5 real satellites, no API key needed)
21. Built JSON and PDF exporters
22. Wrote 50+ tests across all modules
23. Built complete Next.js frontend (5 pages, premium dark theme)
24. Designed and implemented all UI components
25. Wrote README, ARCHITECTURE.md, PROGRESS.md, COMPETITOR.md, BOB.md
26. Created CI workflow (GitHub Actions)
27. Created Dockerfile and render.yaml

### Key Architectural Decisions Made by Bob

1. **API-deletion-proof architecture**: Pre-build and commit all index files so
   citations work without any API calls. This mirrors AccessGate's winning pattern.

2. **Deterministic compliance, AI explanation**: AI never determines compliance.
   This makes the system auditable and trustworthy for regulatory contexts.

3. **Graceful fallback chain**: Every IBM layer has a fallback:
   - Granite Instruct → structured text report
   - Granite Embedding → hard-coded clause map
   - Granite Guardian → conservative "not served" behavior

4. **King-Hele integration stepping**: Rather than the naive linear approximation
   from the instruction file, Bob implemented an altitude-stepping loop for
   better accuracy across the altitude range.

5. **Rule orbit-type filtering**: Rules that don't apply to a satellite's orbit
   type (e.g., GEO disposal rules for LEO satellites) return SKIP rather than
   false PASS — this prevents misleading compliance scores.

### Bugs Diagnosed and Fixed During Build

- `RuleDefinition.applies_to` field in YAML not matching Pydantic model →
  Changed applies_to to Optional in the model
- `_json_serializer` in json_export.py needed to handle datetime from report →
  Added datetime → isostring case
- sgp4init epoch format: Bob used jd+fr combined float instead of separate
  julian day and fraction which would have caused propagation errors
- PDF exporter `_color_to_hex` function needed to handle ReportLab Color objects
  properly

### Bob's Total Contribution to PHAROS

Bob wrote 100% of the PHAROS codebase. Every file, every function, every test.
The human developer provided the instruction file (pharos_instruction.md)
and IBM Bob built the entire system.
