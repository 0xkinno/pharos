"""
PHAROS Compliance Engine — Master Orchestrator

Coordinates all rule evaluations for a given satellite and produces a
complete ComplianceReport. This is the core of PHAROS.

Architecture principle: The engine is DETERMINISTIC. AI never makes
compliance decisions. The engine evaluates rules; IBM Granite explains
the results in plain language.

API-deletion proof: The compliance engine runs and produces full
pass/fail/flag results even with no internet connection and no API keys.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

from app.models.compliance import ComplianceReport, RuleResult, RuleStatus, ComplianceLevel
from app.models.satellite import SatelliteData
from app.models.standards import RuleDefinition, StandardsRegistry
from app.services.lifetime_estimator import estimate_orbital_lifetime_years
from app.services.orbital_propagator import classify_orbit, compute_orbital_elements_from_sgp4
import app.evaluators.fcc as fcc
import app.evaluators.iadc as iadc
import app.evaluators.iso24113 as iso24113
import app.evaluators.esa_zero_debris as esa
import app.evaluators.copuos as copuos

logger = logging.getLogger(__name__)

_REGISTRY_PATH = Path(__file__).parent.parent.parent / "rules" / "rules_registry.yaml"
_registry_cache: Optional[StandardsRegistry] = None


def load_rules_registry() -> StandardsRegistry:
    """Load and cache the rules registry from YAML."""
    global _registry_cache
    if _registry_cache is not None:
        return _registry_cache

    with open(_REGISTRY_PATH, encoding="utf-8", errors="replace") as f:
        data = yaml.safe_load(f)

    rules = [RuleDefinition(**r) for r in data["rules"]]
    _registry_cache = StandardsRegistry(rules=rules)
    return _registry_cache


def evaluate_satellite(
    sat: SatelliteData,
    mission_status: str = "active",
    years_since_mission_end: float = 0.0,
    satellite_mass_kg: float = 100.0,
    area_to_mass_ratio: float = 0.01,
    has_propulsion: bool = True,
    # Passivation data
    has_passivation_plan: bool = False,
    pressure_vessels_vented: bool = False,
    batteries_discharged: bool = False,
    # Registration data
    is_registered_with_un: bool = True,
    national_registry_registered: bool = True,
    # Operations data
    ssa_data_shared: bool = True,
    collision_avoidance_capability: bool = True,
    # Solar activity for lifetime estimation
    solar_activity: str = "moderate",
) -> ComplianceReport:
    """
    Run the full compliance evaluation for a satellite.

    This is the primary entry point for compliance checking.
    Returns a ComplianceReport with all rule results.
    """
    # Ensure orbital elements are computed
    if sat.orbital_elements is None:
        sat.orbital_elements = compute_orbital_elements_from_sgp4(sat)

    if sat.orbital_elements is None:
        logger.error("Cannot compute orbital elements for satellite %d", sat.norad_cat_id)
        # Return minimal report with error
        return ComplianceReport(
            norad_cat_id=sat.norad_cat_id,
            object_name=sat.object_name,
            epoch=sat.epoch,
            mean_altitude_km=0.0,
            perigee_km=0.0,
            apogee_km=0.0,
            inclination_deg=sat.inclination,
            eccentricity=sat.eccentricity,
            mean_motion_rev_per_day=sat.mean_motion,
            estimated_orbital_lifetime_years=0.0,
            orbit_type="UNKNOWN",
            rule_results=[],
            compliance_score=0.0,
            compliance_level=ComplianceLevel.UNKNOWN,
        )

    elements = sat.orbital_elements
    mean_altitude = elements.mean_altitude_km
    perigee = elements.perigee_km
    apogee = elements.apogee_km
    orbit_type = classify_orbit(mean_altitude, elements.inclination_deg)

    # Estimate orbital lifetime at current orbit
    estimated_lifetime = estimate_orbital_lifetime_years(
        altitude_km=perigee if elements.eccentricity > 0.05 else mean_altitude,
        area_to_mass_ratio=area_to_mass_ratio,
        eccentricity=elements.eccentricity,
        solar_activity=solar_activity,
    )

    rule_results: list[RuleResult] = []

    # ── FCC Rules ────────────────────────────────────────────────
    # FCC-LEO-01: Classification check
    rule_results.append(fcc.check_leo_orbit_altitude(altitude_km=mean_altitude))

    # FCC-DEORBIT-01: 5-year deorbit rule
    if orbit_type == "LEO":
        rule_results.append(fcc.check_deorbit_lifetime(
            altitude_km=perigee if elements.eccentricity > 0.05 else mean_altitude,
            area_to_mass_ratio=area_to_mass_ratio,
            eccentricity=elements.eccentricity,
            mission_status=mission_status,
            years_since_mission_end=years_since_mission_end,
        ))
    else:
        rule_results.append(RuleResult(
            rule_id="FCC-DEORBIT-01",
            status=RuleStatus.SKIP,
            message=f"FCC-DEORBIT-01 applies to LEO only. Satellite is in {orbit_type}.",
            value=mean_altitude,
            threshold=2000.0,
            unit="km",
            standard_clause="FCC 47 CFR Part 25.114(d)(14)",
            body="FCC",
        ))

    # FCC-DEORBIT-02: Casualty risk
    if orbit_type in ("LEO", "MEO"):
        rule_results.append(fcc.check_casualty_risk(
            altitude_km=mean_altitude,
            satellite_mass_kg=satellite_mass_kg,
        ))
    else:
        rule_results.append(RuleResult(
            rule_id="FCC-DEORBIT-02",
            status=RuleStatus.SKIP,
            message=f"Casualty risk assessment not applicable for {orbit_type}.",
            value=None,
            threshold=None,
            unit=None,
            standard_clause="FCC 47 CFR Part 25.114(d)(14)",
            body="FCC",
        ))

    # ── IADC Rules ───────────────────────────────────────────────
    # IADC-LIFE-01: 25-year lifetime
    if orbit_type == "LEO":
        rule_results.append(iadc.check_orbital_lifetime(
            altitude_km=perigee if elements.eccentricity > 0.05 else mean_altitude,
            area_to_mass_ratio=area_to_mass_ratio,
            eccentricity=elements.eccentricity,
            solar_activity=solar_activity,
        ))
    else:
        rule_results.append(RuleResult(
            rule_id="IADC-LIFE-01",
            status=RuleStatus.SKIP,
            message=f"IADC 25-year rule applies to LEO only. Satellite is in {orbit_type}.",
            value=None,
            threshold=None,
            unit=None,
            standard_clause="IADC-02-01 Rev 3, Section 5.3.2",
            body="IADC",
        ))

    # IADC-PASS-01: Passivation
    rule_results.append(iadc.check_passivation(
        has_passivation_plan=has_passivation_plan,
        remaining_propellant_estimated=has_propulsion,
        pressure_vessels_vented=pressure_vessels_vented,
        batteries_discharged=batteries_discharged,
    ))

    # IADC-COLL-01: Collision probability during disposal
    # We don't have conjunction data per-satellite; flag for operator review
    rule_results.append(iadc.check_disposal_collision_probability(
        collision_probability=0.0  # Unknown — will trigger FLAG for operator review
    ))

    # IADC-REENTRY-01: Controlled reentry target
    if orbit_type == "LEO" and estimated_lifetime > 5.0:
        rule_results.append(iadc.check_controlled_reentry_accuracy(
            target_zone_defined=False,  # Unknown from TLE data alone
        ))

    # ── ISO 24113 Rules ───────────────────────────────────────────
    # ISO-ORBIT-01: LEO protected region
    if orbit_type == "LEO":
        rule_results.append(iso24113.check_leo_protected_region(
            altitude_km=mean_altitude,
            area_to_mass_ratio=area_to_mass_ratio,
            eccentricity=elements.eccentricity,
        ))
    else:
        rule_results.append(RuleResult(
            rule_id="ISO-ORBIT-01",
            status=RuleStatus.SKIP,
            message=f"ISO-ORBIT-01 (LEO Protected Region A) does not apply. Satellite is in {orbit_type}.",
            value=mean_altitude,
            threshold=2000.0,
            unit="km",
            standard_clause="ISO 24113:2019, Section 6.2.2",
            body="ISO",
        ))

    # ISO-ORBIT-02: GEO protected region
    if orbit_type == "GEO":
        rule_results.append(iso24113.check_geo_disposal(
            altitude_km=mean_altitude,
            mission_status=mission_status,
        ))
    else:
        rule_results.append(RuleResult(
            rule_id="ISO-ORBIT-02",
            status=RuleStatus.SKIP,
            message=f"ISO-ORBIT-02 (GEO Protected Region B) does not apply. Satellite is in {orbit_type}.",
            value=mean_altitude,
            threshold=None,
            unit="km",
            standard_clause="ISO 24113:2019, Section 6.2.3",
            body="ISO",
        ))

    # ISO-DEBRIS-01: No intentional debris release
    rule_results.append(iso24113.check_debris_generation_limit(
        fragments_released=0,  # Assume compliant unless operator reports otherwise
    ))

    # ── ESA Zero Debris Charter Rules ────────────────────────────
    rule_results.append(esa.check_no_intentional_release(
        intentional_debris_released=False,
        operational_debris_count=0,
    ))
    rule_results.append(esa.check_disposal_probability(
        disposal_success_probability=0.0,  # Operator-provided; estimate from orbit
        has_propulsion=has_propulsion,
        altitude_km=mean_altitude,
        area_to_mass_ratio=area_to_mass_ratio,
    ))
    rule_results.append(esa.check_debris_free_operations(
        operational_maneuvers_planned=has_propulsion,
        collision_avoidance_capability=collision_avoidance_capability,
        ssa_data_shared=ssa_data_shared,
    ))

    # ── UN COPUOS Rules ───────────────────────────────────────────
    rule_results.append(copuos.check_registration(
        is_registered_with_un=is_registered_with_un,
        national_registry_registered=national_registry_registered,
        cospar_id=sat.international_designator,
    ))
    rule_results.append(copuos.check_data_sharing(
        orbital_data_shared_publicly=ssa_data_shared,
        ssa_coordination_active=ssa_data_shared,
        shares_with_spacefence=False,  # Unknown from TLE
    ))
    rule_results.append(copuos.check_maneuver_notification(
        large_maneuvers_planned=False,  # Assume no large maneuvers without operator data
    ))

    # Build the report
    standards_checked = list({r.standard_clause.split(",")[0].split("§")[0].strip()
                               for r in rule_results if r.status != RuleStatus.SKIP})

    report = ComplianceReport(
        norad_cat_id=sat.norad_cat_id,
        object_name=sat.object_name,
        epoch=sat.epoch,
        report_generated_at=datetime.now(timezone.utc),
        mean_altitude_km=round(mean_altitude, 2),
        perigee_km=round(perigee, 2),
        apogee_km=round(apogee, 2),
        inclination_deg=round(elements.inclination_deg, 4),
        eccentricity=round(elements.eccentricity, 6),
        mean_motion_rev_per_day=round(elements.mean_motion_rev_per_day, 6),
        estimated_orbital_lifetime_years=estimated_lifetime,
        orbit_type=orbit_type,
        rule_results=rule_results,
        compliance_score=0.0,  # will be computed
        compliance_level=ComplianceLevel.UNKNOWN,
        standards_checked=standards_checked,
        data_sources=["CelesTrak GP API (public OMM data)"],
    )

    report.compute_score()
    return report
