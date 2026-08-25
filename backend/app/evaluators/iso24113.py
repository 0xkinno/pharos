"""
ISO 24113 Rule Evaluators — Space Systems: Space Debris Mitigation Requirements

ISO 24113:2019 is the primary international standard for space debris
mitigation. It defines requirements for protected orbital regions and
disposal orbit criteria.

Source: ISO 24113:2019 "Space systems — Space debris mitigation requirements"
Available summary: https://www.iso.org/standard/72383.html
Technical Committee: ISO/TC 20/SC 14 (Space systems and operations)
"""
from __future__ import annotations

import logging

from app.models.compliance import RuleResult, RuleStatus
from app.services.lifetime_estimator import estimate_orbital_lifetime_years

logger = logging.getLogger(__name__)

# Protected regions
LEO_UPPER_LIMIT_KM = 2000.0    # Protected Region A: 0–2000 km
GEO_ALTITUDE_KM = 35786.0      # Nominal GEO altitude
GEO_BELT_HALF_WIDTH_KM = 200.0 # Protected Region B: ±200 km around GEO
GEO_LOWER_BOUND_KM = GEO_ALTITUDE_KM - GEO_BELT_HALF_WIDTH_KM
GEO_UPPER_BOUND_KM = GEO_ALTITUDE_KM + GEO_BELT_HALF_WIDTH_KM
GRAVEYARD_MIN_KM_ABOVE_GEO = 200.0  # Minimum graveyard altitude above GEO belt


def check_leo_protected_region(
    altitude_km: float,
    area_to_mass_ratio: float = 0.01,
    eccentricity: float = 0.0,
) -> RuleResult:
    """
    ISO-ORBIT-01: ISO 24113:2019, Section 6.2.2
    Protected Region A (LEO): Spacecraft must not remain in the LEO
    protected region (up to 2000 km) for more than 25 years post-mission.

    ISO 24113 defines two protected orbital regions:
    - Protected Region A: Sphere of 2000 km altitude
    - Protected Region B: Zone ±200 km around GEO

    For LEO, the standard requires post-mission disposal within 25 years,
    consistent with the IADC guideline.
    """
    if altitude_km >= LEO_UPPER_LIMIT_KM:
        return RuleResult(
            rule_id="ISO-ORBIT-01",
            status=RuleStatus.SKIP,
            message=(
                f"Satellite at {altitude_km:.0f} km is above LEO Protected Region A "
                f"(below {LEO_UPPER_LIMIT_KM:.0f} km). ISO-ORBIT-01 does not apply."
            ),
            value=altitude_km,
            threshold=LEO_UPPER_LIMIT_KM,
            unit="km",
            standard_clause="ISO 24113:2019, Section 6.2.2",
            body="ISO",
        )

    estimated_lifetime = estimate_orbital_lifetime_years(
        altitude_km=altitude_km,
        area_to_mass_ratio=area_to_mass_ratio,
        eccentricity=eccentricity,
    )

    if estimated_lifetime <= 25.0:
        return RuleResult(
            rule_id="ISO-ORBIT-01",
            status=RuleStatus.PASS,
            message=(
                f"Satellite in LEO Protected Region A at {altitude_km:.0f} km. "
                f"Estimated orbital lifetime {estimated_lifetime:.1f} years is within "
                f"ISO 24113 25-year disposal requirement."
            ),
            value=estimated_lifetime,
            threshold=25.0,
            unit="years",
            standard_clause="ISO 24113:2019, Section 6.2.2",
            body="ISO",
        )

    return RuleResult(
        rule_id="ISO-ORBIT-01",
        status=RuleStatus.FAIL,
        message=(
            f"Satellite in LEO Protected Region A at {altitude_km:.0f} km. "
            f"Estimated orbital lifetime {estimated_lifetime:.1f} years EXCEEDS "
            f"ISO 24113:2019 Section 6.2.2 requirement of 25 years. "
            f"Disposal maneuver to lower orbit or controlled reentry required."
        ),
        value=estimated_lifetime,
        threshold=25.0,
        unit="years",
        standard_clause="ISO 24113:2019, Section 6.2.2",
        body="ISO",
    )


def check_geo_disposal(
    altitude_km: float,
    mission_status: str = "active",
    final_altitude_km: float | None = None,
) -> RuleResult:
    """
    ISO-ORBIT-02: ISO 24113:2019, Section 6.2.3
    Protected Region B (GEO): GEO satellites must be moved to a graveyard
    orbit at least 200 km above the GEO protected belt at end of mission.

    The GEO protected region spans ±200 km around the nominal GEO altitude
    of 35,786 km. Graveyard orbit must be at least 200 km above the upper
    boundary, i.e., above 35,786 + 200 + 200 = 36,186 km.
    """
    is_in_geo_belt = GEO_LOWER_BOUND_KM <= altitude_km <= GEO_UPPER_BOUND_KM

    if not is_in_geo_belt:
        return RuleResult(
            rule_id="ISO-ORBIT-02",
            status=RuleStatus.SKIP,
            message=(
                f"Satellite at {altitude_km:.0f} km is not in the GEO Protected Region B "
                f"({GEO_LOWER_BOUND_KM:.0f}–{GEO_UPPER_BOUND_KM:.0f} km). "
                f"ISO-ORBIT-02 (GEO disposal) does not apply."
            ),
            value=altitude_km,
            threshold=None,
            unit="km",
            standard_clause="ISO 24113:2019, Section 6.2.3",
            body="ISO",
        )

    # Calculate minimum graveyard altitude
    min_graveyard_km = GEO_UPPER_BOUND_KM + GRAVEYARD_MIN_KM_ABOVE_GEO  # 36,186 km

    if mission_status == "active":
        return RuleResult(
            rule_id="ISO-ORBIT-02",
            status=RuleStatus.FLAG,
            message=(
                f"Satellite is in GEO Protected Region B at {altitude_km:.0f} km. "
                f"At end of mission, must be raised to graveyard orbit above "
                f"{min_graveyard_km:.0f} km (+{GRAVEYARD_MIN_KM_ABOVE_GEO:.0f} km above GEO belt). "
                f"Verify disposal propellant margin."
            ),
            value=altitude_km,
            threshold=min_graveyard_km,
            unit="km",
            standard_clause="ISO 24113:2019, Section 6.2.3",
            body="ISO",
        )

    # Check if disposed to graveyard orbit
    if final_altitude_km is None:
        return RuleResult(
            rule_id="ISO-ORBIT-02",
            status=RuleStatus.FLAG,
            message=(
                f"Satellite is decommissioned but final disposal orbit altitude unknown. "
                f"ISO 24113:2019 requires disposal to graveyard orbit above {min_graveyard_km:.0f} km."
            ),
            value=altitude_km,
            threshold=min_graveyard_km,
            unit="km",
            standard_clause="ISO 24113:2019, Section 6.2.3",
            body="ISO",
        )

    if final_altitude_km >= min_graveyard_km:
        return RuleResult(
            rule_id="ISO-ORBIT-02",
            status=RuleStatus.PASS,
            message=(
                f"GEO disposal confirmed: satellite raised to {final_altitude_km:.0f} km, "
                f"which is {final_altitude_km - GEO_UPPER_BOUND_KM:.0f} km above the GEO belt "
                f"(minimum required: {GRAVEYARD_MIN_KM_ABOVE_GEO:.0f} km above belt)."
            ),
            value=final_altitude_km,
            threshold=min_graveyard_km,
            unit="km",
            standard_clause="ISO 24113:2019, Section 6.2.3",
            body="ISO",
        )

    return RuleResult(
        rule_id="ISO-ORBIT-02",
        status=RuleStatus.FAIL,
        message=(
            f"GEO disposal orbit {final_altitude_km:.0f} km is INSUFFICIENT. "
            f"Minimum graveyard altitude: {min_graveyard_km:.0f} km "
            f"({GRAVEYARD_MIN_KM_ABOVE_GEO:.0f} km above GEO belt upper boundary at "
            f"{GEO_UPPER_BOUND_KM:.0f} km). "
            f"Deficit: {min_graveyard_km - final_altitude_km:.0f} km."
        ),
        value=final_altitude_km,
        threshold=min_graveyard_km,
        unit="km",
        standard_clause="ISO 24113:2019, Section 6.2.3",
        body="ISO",
    )


def check_debris_generation_limit(
    fragments_released: int = 0,
    mission_type: str = "deployment",
) -> RuleResult:
    """
    ISO-DEBRIS-01: ISO 24113:2019, Section 6.3
    Operations in protected regions shall not intentionally release debris.

    ISO 24113 prohibits the intentional release of objects that will remain
    in protected orbital regions. This includes lens caps, protective covers,
    and other operational debris releases.
    """
    if fragments_released == 0:
        return RuleResult(
            rule_id="ISO-DEBRIS-01",
            status=RuleStatus.PASS,
            message=(
                "No intentional debris release reported. "
                "Compliant with ISO 24113:2019 Section 6.3 no-debris-release requirement."
            ),
            value=float(fragments_released),
            threshold=0.0,
            unit="fragments",
            standard_clause="ISO 24113:2019, Section 6.3",
            body="ISO",
        )

    return RuleResult(
        rule_id="ISO-DEBRIS-01",
        status=RuleStatus.FAIL,
        message=(
            f"{fragments_released} intentional debris fragment(s) released. "
            f"ISO 24113:2019 Section 6.3 prohibits intentional release of objects "
            f"that remain in protected orbital regions. "
            f"Operational design must avoid any debris release."
        ),
        value=float(fragments_released),
        threshold=0.0,
        unit="fragments",
        standard_clause="ISO 24113:2019, Section 6.3",
        body="ISO",
    )
