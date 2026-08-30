"""
REST API Routes for PHAROS Backend

Implements all endpoints defined in Section 6 of pharos_instruction.md:
  GET  /api/health
  GET  /api/satellites/search?query=...
  GET  /api/satellites/{norad_id}
  POST /api/compliance/check
  GET  /api/compliance/report/{norad_id}
  GET  /api/demo
  GET  /api/standards
  GET  /api/standards/{rule_id}
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel

from app.ai.watsonx_client import get_watsonx_client
from app.ai.watsonx_guardian import screen_report
from app.exporters.json_export import export_to_json
from app.exporters.pdf_export import export_to_pdf
from app.models.compliance import ComplianceReport
from app.models.satellite import SatelliteData, SatelliteSearchResult
from app.services.celestrak_client import (
    get_satellite_by_norad_id,
    search_satellites,
)
from app.services.compliance_engine import evaluate_satellite, load_rules_registry
from app.services.rag_service import enrich_report_with_citations
from app.services.report_generator import generate_compliance_report

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


# ─────────────────────────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/health")
async def health_check():
    """Liveness check."""
    from app.ai.watsonx_client import get_watsonx_client
    from app.core.config import get_settings
    client = get_watsonx_client()
    settings = get_settings()
    return {
        "status": "ok",
        "service": "PHAROS API",
        "version": "1.0.0",
        "watsonx_available": client.is_available(),
        "watsonx_configured": settings.watsonx_configured,
        "watsonx_api_key_present": bool(settings.watsonx_api_key),
        "watsonx_project_id_present": bool(settings.watsonx_project_id),
        "watsonx_url": settings.watsonx_url,
        "active_instruct_model": client.active_instruct_model,
        "active_guardian_model": client.active_guardian_model,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Satellite Search & Data
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/satellites/search", response_model=list[SatelliteSearchResult])
async def search(
    query: str = Query(..., min_length=1, description="Satellite name or NORAD ID"),
    limit: int = Query(20, ge=1, le=100),
):
    """Search satellites by name or NORAD catalog ID."""
    results = await search_satellites(query=query, limit=limit)
    return results


@router.get("/satellites/{norad_id}", response_model=SatelliteData)
async def get_satellite(norad_id: int):
    """Get full orbital data for a satellite by NORAD catalog ID."""
    sat = await get_satellite_by_norad_id(norad_id)
    if sat is None:
        raise HTTPException(status_code=404, detail=f"Satellite NORAD {norad_id} not found in CelesTrak.")
    return sat


# ─────────────────────────────────────────────────────────────────────────────
# Compliance Checking
# ─────────────────────────────────────────────────────────────────────────────

class ComplianceCheckRequest(BaseModel):
    norad_id: int
    mission_status: str = "active"
    years_since_mission_end: float = 0.0
    satellite_mass_kg: float = 100.0
    area_to_mass_ratio: float = 0.01
    has_propulsion: bool = True
    has_passivation_plan: bool = False
    pressure_vessels_vented: bool = False
    batteries_discharged: bool = False
    is_registered_with_un: bool = True
    ssa_data_shared: bool = True
    collision_avoidance_capability: bool = True
    solar_activity: str = "moderate"
    include_ai_report: bool = True
    include_citations: bool = True


@router.post("/compliance/check", response_model=ComplianceReport)
async def check_compliance(request: ComplianceCheckRequest):
    """
    Run a full compliance check on a satellite.
    Fetches orbital data from CelesTrak, evaluates all rules, optionally
    generates AI report and citations.
    """
    sat = await get_satellite_by_norad_id(request.norad_id)
    if sat is None:
        raise HTTPException(status_code=404, detail=f"Satellite NORAD {request.norad_id} not found.")

    report = evaluate_satellite(
        sat=sat,
        mission_status=request.mission_status,
        years_since_mission_end=request.years_since_mission_end,
        satellite_mass_kg=request.satellite_mass_kg,
        area_to_mass_ratio=request.area_to_mass_ratio,
        has_propulsion=request.has_propulsion,
        has_passivation_plan=request.has_passivation_plan,
        pressure_vessels_vented=request.pressure_vessels_vented,
        batteries_discharged=request.batteries_discharged,
        is_registered_with_un=request.is_registered_with_un,
        ssa_data_shared=request.ssa_data_shared,
        collision_avoidance_capability=request.collision_avoidance_capability,
        solar_activity=request.solar_activity,
    )

    # Enrich with RAG citations
    if request.include_citations:
        enrich_report_with_citations(report.rule_results)

    # Generate AI report
    if request.include_ai_report:
        ai_text = generate_compliance_report(report)
        client = get_watsonx_client()
        report.ai_available = client.is_available()

        if report.ai_available and ai_text:
            # Screen with Guardian before serving
            guardian_result = screen_report(ai_text)
            if guardian_result.screened and not guardian_result.safe:
                logger.warning("Guardian flagged AI report as unsafe for %s", sat.object_name)
                report.ai_report_text = None
                report.ai_report_safe = False
            else:
                report.ai_report_text = ai_text
                report.ai_report_safe = True
        else:
            # AI not available — use structured fallback (always safe)
            report.ai_report_text = ai_text
            report.ai_report_safe = True

    return report


@router.get("/compliance/report/{norad_id}", response_model=ComplianceReport)
async def get_compliance_report(
    norad_id: int,
    include_ai_report: bool = Query(True),
    include_citations: bool = Query(True),
):
    """Get a full compliance report for a satellite by NORAD ID."""
    req = ComplianceCheckRequest(
        norad_id=norad_id,
        include_ai_report=include_ai_report,
        include_citations=include_citations,
    )
    return await check_compliance(req)


@router.get("/compliance/report/{norad_id}/export/json")
async def export_report_json(norad_id: int):
    """Export compliance report as JSON file."""
    req = ComplianceCheckRequest(norad_id=norad_id, include_ai_report=True, include_citations=True)
    report = await check_compliance(req)
    json_str = export_to_json(report)
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="pharos_report_{norad_id}.json"'},
    )


@router.get("/compliance/report/{norad_id}/export/pdf")
async def export_report_pdf(norad_id: int):
    """Export compliance report as PDF file."""
    req = ComplianceCheckRequest(norad_id=norad_id, include_ai_report=True, include_citations=True)
    report = await check_compliance(req)
    pdf_bytes = export_to_pdf(report)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="pharos_report_{norad_id}.pdf"'},
    )


# ─────────────────────────────────────────────────────────────────────────────
# Standards Registry
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/standards")
async def list_standards():
    """List all regulatory standards and their coded rules."""
    registry = load_rules_registry()
    # Group by body
    by_body: dict = {}
    for rule in registry.rules:
        body = rule.body
        if body not in by_body:
            by_body[body] = {"body": body, "rules": []}
        by_body[body]["rules"].append({
            "id": rule.id,
            "standard": rule.standard,
            "title": rule.title,
            "description": rule.description,
            "severity": rule.severity,
            "threshold": rule.threshold.model_dump() if rule.threshold else None,
        })
    return {
        "total_rules": len(registry.rules),
        "bodies": list(by_body.values()),
    }


@router.get("/standards/{rule_id}")
async def get_standard(rule_id: str):
    """Get details for a specific rule including the standard clause text."""
    from app.ai.watsonx_embedding import retrieve_citation
    registry = load_rules_registry()
    rule = next((r for r in registry.rules if r.id == rule_id.upper()), None)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found in registry.")

    citation = retrieve_citation(rule_id=rule_id.upper())
    return {
        "rule": {
            "id": rule.id,
            "standard": rule.standard,
            "body": rule.body,
            "title": rule.title,
            "description": rule.description,
            "severity": rule.severity,
            "threshold": rule.threshold.model_dump() if rule.threshold else None,
        },
        "citation": {
            "clause_text": citation.get("clause_text"),
            "source": citation.get("source"),
            "retrieval_method": citation.get("retrieval_method"),
        },
    }
