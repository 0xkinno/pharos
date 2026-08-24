# AGENTS.md — Project Policy for AI Agents

## Project: PHAROS

**This file is read by every AI agent before any code changes.**

## Mandatory Before Starting

1. Read `pharos_instruction.md` — it is the law
2. Read `docs/PROGRESS.md` — current build state
3. Read `docs/ARCHITECTURE.md` — system design
4. Read `docs/Competitor.md` — competitive positioning

## Quality Standard

The standard is not "working" — the standard is "undisputed best in the competition."

Every feature is FULLY implemented. No stubs. No TODO. No coming soon.
No mock data labeled as real. No placeholder content.

## Compliance Engine Principle

**The engine DETECTS. IBM EXPLAINS.**

AI never determines compliance. The deterministic evaluators do.
IBM Granite adds: plain-language reports, semantic citations, safety screening.

## After Each Session

1. Update `docs/PROGRESS.md` with what was completed
2. Update `docs/BOB.md` with session log
3. Run the test suite to verify nothing is broken

## Files to Never Modify Without Understanding

- `backend/rules/rules_registry.yaml` — all coded rules
- `backend/app/evaluators/*.py` — never change threshold values without checking standard
- `backend/standards/parsed/*.md` — regulatory text (commit only, do not edit)
- `backend/standards/index/chunks.json` — pre-built embedding index
