"""
JSON Compliance Report Exporter

Serializes a ComplianceReport to a well-structured JSON format
suitable for programmatic consumption, archival, and machine-to-machine
integration.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.models.compliance import ComplianceReport


def export_to_json(report: ComplianceReport, indent: int = 2) -> str:
    """
    Serialize a ComplianceReport to a formatted JSON string.

    The output includes all rule results, citations, orbital parameters,
    compliance scores, and AI report text.
    """
    data = _report_to_dict(report)
    return json.dumps(data, indent=indent, default=_json_serializer)


def _json_serializer(obj: Any) -> Any:
    """Custom JSON serializer for non-standard types."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _report_to_dict(report: ComplianceReport) -> dict:
    """Convert a ComplianceReport to a plain dictionary."""
    return {
        "schema_version": "1.0",
        "generated_by": "PHAROS v1.0.0",
        "data_source": "CelesTrak GP API",
        "satellite": {
            "norad_cat_id": report.norad_cat_id,
            "object_name": report.object_name,
            "epoch": report.epoch,
        },
        "orbital_parameters": {
            "mean_altitude_km": report.mean_altitude_km,
            "perigee_km": report.perigee_km,
            "apogee_km": report.apogee_km,
            "inclination_deg": report.inclination_deg,
            "eccentricity": report.eccentricity,
            "mean_motion_rev_per_day": report.mean_motion_rev_per_day,
            "orbit_type": report.orbit_type,
            "estimated_orbital_lifetime_years": report.estimated_orbital_lifetime_years,
        },
        "compliance_summary": {
            "compliance_score": report.compliance_score,
            "compliance_level": report.compliance_level.value,
            "rules_passed": report.rules_passed,
            "rules_flagged": report.rules_flagged,
            "rules_failed": report.rules_failed,
            "rules_skipped": report.rules_skipped,
            "standards_checked": report.standards_checked,
        },
        "rule_results": [
            {
                "rule_id": r.rule_id,
                "status": r.status.value,
                "standard_clause": r.standard_clause,
                "body": r.body,
                "message": r.message,
                "value": r.value,
                "threshold": r.threshold,
                "unit": r.unit,
                "retrieved_clause_text": r.retrieved_clause_text,
                "retrieved_clause_source": r.retrieved_clause_source,
            }
            for r in report.rule_results
        ],
        "ai_report": {
            "text": report.ai_report_text,
            "safety_screened": report.ai_report_safe,
            "ai_available": report.ai_available,
        },
        "metadata": {
            "report_generated_at": report.report_generated_at.isoformat() if report.report_generated_at else None,
            "data_sources": report.data_sources,
        },
    }
