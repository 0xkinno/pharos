"""
Demo Data Endpoint

Serves pre-computed compliance reports for the demo dataset.
This endpoint requires NO API keys and loads in <1 second.

Pre-computed for 5 real satellites:
  - Starlink-1007 (NORAD 44713): Active LEO, altitude ~550 km
  - ISS (ZARYA) (NORAD 25544): Active LEO, ~400 km, special considerations
  - Cosmos 2251 Debris (NORAD 33781): Non-compliant debris fragment
  - NOAA-15 (NORAD 25338): Active but aged LEO weather satellite
  - Intelsat 901 (NORAD 26824): GEO satellite, disposal rules apply
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter

from app.models.compliance import (
    ComplianceReport, ComplianceLevel, RuleResult, RuleStatus, DemoDataset, DemoSatellite
)
from app.services.compliance_engine import evaluate_satellite
from app.services.celestrak_client import _omm_to_satellite_data
from app.models.satellite import SatelliteData, OrbitalElements

logger = logging.getLogger(__name__)
router = APIRouter()

_DEMO_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "demo" / "demo_report.json"


def _make_mock_satellite(
    norad_id: int,
    name: str,
    mean_motion: float,
    eccentricity: float,
    inclination: float,
    bstar: float = 0.0002,
    intldes: Optional[str] = None,
) -> SatelliteData:
    """Build a SatelliteData with computed orbital elements."""
    import math
    MU = 398600.4418
    n_rad_s = mean_motion * 2 * math.pi / 86400.0
    a_km = (MU / (n_rad_s ** 2)) ** (1.0 / 3.0)

    elements = OrbitalElements(
        semi_major_axis_km=a_km,
        eccentricity=eccentricity,
        inclination_deg=inclination,
        raan_deg=100.0,
        arg_of_perigee_deg=90.0,
        mean_anomaly_deg=180.0,
        mean_motion_rev_per_day=mean_motion,
        bstar_drag=bstar,
        epoch="2024-01-15T12:00:00",
    )

    return SatelliteData(
        norad_cat_id=norad_id,
        object_name=name,
        object_type="PAYLOAD",
        classification_type="U",
        international_designator=intldes,
        epoch="2024-01-15T12:00:00",
        mean_motion=mean_motion,
        eccentricity=eccentricity,
        inclination=inclination,
        ra_of_asc_node=100.0,
        arg_of_pericenter=90.0,
        mean_anomaly=180.0,
        bstar=bstar,
        orbital_elements=elements,
    )


# Demo satellite definitions (based on real orbital parameters)
_DEMO_SATELLITES = [
    {
        "norad_id": 44713,
        "name": "STARLINK-1007",
        "description": "Active Starlink LEO broadband satellite at ~550 km altitude",
        "mean_motion": 15.06,      # ~550 km altitude
        "eccentricity": 0.00015,
        "inclination": 53.0,
        "bstar": 0.0002,
        "intldes": "2019-074A",
        "mission_status": "active",
        "has_propulsion": True,
        "ssa_data_shared": True,
        "collision_avoidance_capability": True,
    },
    {
        "norad_id": 25544,
        "name": "ISS (ZARYA)",
        "description": "International Space Station — active, manned, ~410 km altitude",
        "mean_motion": 15.49,      # ~410 km altitude
        "eccentricity": 0.0004,
        "inclination": 51.64,
        "bstar": 0.00015,
        "intldes": "1998-067A",
        "mission_status": "active",
        "satellite_mass_kg": 420000.0,
        "has_propulsion": True,
        "ssa_data_shared": True,
        "collision_avoidance_capability": True,
    },
    {
        "norad_id": 33781,
        "name": "COSMOS 2251 DEB",
        "description": "Debris fragment from the 2009 Iridium-Cosmos collision",
        "mean_motion": 14.21,      # ~775 km altitude (debris fragment)
        "eccentricity": 0.0032,
        "inclination": 74.0,
        "bstar": 0.0001,
        "intldes": "2009-005A",
        "mission_status": "decommissioned",
        "years_since_mission_end": 15.5,  # Cosmos 2251 decommissioned ~2008
        "has_propulsion": False,
        "ssa_data_shared": False,
        "collision_avoidance_capability": False,
        "has_passivation_plan": False,
        "object_type": "DEBRIS",
    },
    {
        "norad_id": 25338,
        "name": "NOAA 15",
        "description": "NOAA-15 weather satellite — active but aging, LEO polar orbit ~810 km",
        "mean_motion": 14.13,      # ~810 km altitude
        "eccentricity": 0.001,
        "inclination": 98.7,
        "bstar": 0.00005,
        "intldes": "1998-030A",
        "mission_status": "active",
        "satellite_mass_kg": 1457.0,
        "has_propulsion": False,
        "ssa_data_shared": True,
        "collision_avoidance_capability": False,
    },
    {
        "norad_id": 26824,
        "name": "INTELSAT 901",
        "description": "GEO communications satellite at ~35,786 km altitude",
        "mean_motion": 1.0027,     # GEO
        "eccentricity": 0.0002,
        "inclination": 0.05,
        "bstar": 0.000001,
        "intldes": "2001-024A",
        "mission_status": "active",
        "satellite_mass_kg": 4720.0,
        "has_propulsion": True,
        "ssa_data_shared": True,
        "collision_avoidance_capability": True,
    },
]


def _build_demo_report(sat_def: dict) -> DemoSatellite:
    """Build a demo DemoSatellite with compliance report."""
    sat = _make_mock_satellite(
        norad_id=sat_def["norad_id"],
        name=sat_def["name"],
        mean_motion=sat_def["mean_motion"],
        eccentricity=sat_def["eccentricity"],
        inclination=sat_def["inclination"],
        bstar=sat_def.get("bstar", 0.0002),
        intldes=sat_def.get("intldes"),
    )

    # Override object type for debris
    if sat_def.get("object_type") == "DEBRIS":
        sat.object_type = "DEBRIS"

    report = evaluate_satellite(
        sat=sat,
        mission_status=sat_def.get("mission_status", "active"),
        years_since_mission_end=sat_def.get("years_since_mission_end", 0.0),
        satellite_mass_kg=sat_def.get("satellite_mass_kg", 100.0),
        area_to_mass_ratio=sat_def.get("area_to_mass_ratio", 0.01),
        has_propulsion=sat_def.get("has_propulsion", True),
        has_passivation_plan=sat_def.get("has_passivation_plan", False),
        pressure_vessels_vented=sat_def.get("pressure_vessels_vented", False),
        batteries_discharged=sat_def.get("batteries_discharged", False),
        is_registered_with_un=sat_def.get("is_registered_with_un", True),
        ssa_data_shared=sat_def.get("ssa_data_shared", True),
        collision_avoidance_capability=sat_def.get("collision_avoidance_capability", True),
    )

    # Add fallback structured AI report (no API key needed)
    from app.services.report_generator import _build_structured_fallback_report
    report.ai_report_text = _build_structured_fallback_report(report)
    report.ai_available = False
    report.ai_report_safe = True

    # Add RAG citations
    from app.services.rag_service import enrich_report_with_citations
    enrich_report_with_citations(report.rule_results)

    return DemoSatellite(
        norad_cat_id=sat_def["norad_id"],
        object_name=sat_def["name"],
        description=sat_def["description"],
        compliance_report=report,
    )


_demo_dataset_cache: Optional[DemoDataset] = None


def get_demo_dataset() -> DemoDataset:
    """Build and cache the demo dataset."""
    global _demo_dataset_cache
    if _demo_dataset_cache is not None:
        return _demo_dataset_cache

    # Try to load from file first
    if _DEMO_DATA_PATH.exists():
        try:
            with open(_DEMO_DATA_PATH) as f:
                data = json.load(f)
            _demo_dataset_cache = DemoDataset(**data)
            return _demo_dataset_cache
        except Exception as exc:
            logger.warning("Failed to load demo data from file: %s. Regenerating.", exc)

    # Generate fresh
    logger.info("Generating demo dataset...")
    satellites = [_build_demo_report(s) for s in _DEMO_SATELLITES]

    compliant_count = sum(1 for s in satellites if s.compliance_report.compliance_level.value == "COMPLIANT")
    at_risk_count = sum(1 for s in satellites if s.compliance_report.compliance_level.value == "AT_RISK")
    non_compliant_count = sum(1 for s in satellites if s.compliance_report.compliance_level.value == "NON_COMPLIANT")

    _demo_dataset_cache = DemoDataset(
        generated_at=datetime.now(timezone.utc),
        satellites=satellites,
        summary={
            "total_satellites": len(satellites),
            "compliant": compliant_count,
            "at_risk": at_risk_count,
            "non_compliant": non_compliant_count,
            "average_score": round(
                sum(s.compliance_report.compliance_score for s in satellites) / len(satellites), 1
            ),
        },
    )
    return _demo_dataset_cache


@router.get("/api/demo")
async def get_demo():
    """
    Pre-computed demo compliance report.
    No API keys required. Loads from committed data or regenerates.
    """
    dataset = get_demo_dataset()
    return {
        "generated_at": dataset.generated_at.isoformat(),
        "note": "Pre-computed demo data. No API keys required.",
        "summary": dataset.summary,
        "satellites": [
            {
                "norad_cat_id": s.norad_cat_id,
                "object_name": s.object_name,
                "description": s.description,
                "compliance_score": s.compliance_report.compliance_score,
                "compliance_level": s.compliance_report.compliance_level.value,
                "orbit_type": s.compliance_report.orbit_type,
                "mean_altitude_km": s.compliance_report.mean_altitude_km,
                "rules_passed": s.compliance_report.rules_passed,
                "rules_flagged": s.compliance_report.rules_flagged,
                "rules_failed": s.compliance_report.rules_failed,
                "estimated_orbital_lifetime_years": s.compliance_report.estimated_orbital_lifetime_years,
            }
            for s in dataset.satellites
        ],
    }


@router.get("/api/demo/{norad_id}")
async def get_demo_satellite(norad_id: int):
    """Get full demo report for a specific satellite."""
    dataset = get_demo_dataset()
    sat = next((s for s in dataset.satellites if s.norad_cat_id == norad_id), None)
    if sat is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Satellite {norad_id} not in demo dataset.")
    return sat.compliance_report
