"""
FCC Rule Evaluators — FCC 47 CFR Part 25

Implements rules derived from the FCC's satellite disposal regulations,
including the landmark 5-year deorbit rule adopted in September 2022
(effective for new satellites from September 2024).

Sources:
  - FCC 47 CFR Part 25.114(d)(14): Post-mission disposal requirements
  - FCC 22-74: "Mitigation of Orbital Debris in the New Space Age" (2022)
  - https://www.fcc.gov/document/fcc-adopts-new-5-year-rule-deorbiting-satellites
"""
from __future__ import annotations

import logging

from app.models.compliance import RuleResult, RuleStatus
from app.services.lifetime_estimator import estimate_orbital_lifetime_years

logger = logging.getLogger(__name__)


def check_deorbit_lifetime(
    altitude_km: float,
    area_to_mass_ratio: float = 0.01,
    eccentricity: float = 0.0,
    mission_status: str = "active",
    years_since_mission_end: float = 0.0,
) -> RuleResult:
    """
    FCC-DEORBIT-01: FCC 47 CFR Part 25.114(d)(14)
    LEO satellites must deorbit within 5 years of mission end.

    Adopted: September 2022. The FCC cut the acceptable post-mission orbital
    lifetime from 25 years to 5 years for LEO satellites, effective
    September 29, 2024 for new satellite applications.

    Evaluator logic:
    - Active satellite: checks if natural lifetime is ≤ 5 years (compliant if so)
    - Active satellite with natural lifetime > 5 years: FLAGGED (will need active deorbit at EOL)
    - Decommissioned satellite: checks remaining compliance window vs estimated lifetime
    """
    estimated_lifetime = estimate_orbital_lifetime_years(
        altitude_km=altitude_km,
        area_to_mass_ratio=area_to_mass_ratio,
        eccentricity=eccentricity,
    )

    if mission_status == "active":
        if estimated_lifetime <= 5.0:
            return RuleResult(
                rule_id="FCC-DEORBIT-01",
                status=RuleStatus.PASS,
                message=(
                    f"Current orbit will naturally decay within {estimated_lifetime:.1f} years. "
                    f"Compliant with FCC 5-year rule if decommissioned now."
                ),
                value=estimated_lifetime,
                threshold=5.0,
                unit="years",
                standard_clause="FCC 47 CFR Part 25.114(d)(14)",
                body="FCC",
            )
        else:
            return RuleResult(
                rule_id="FCC-DEORBIT-01",
                status=RuleStatus.FLAG,
                message=(
                    f"Current orbital lifetime estimated at {estimated_lifetime:.1f} years. "
                    f"This exceeds the 5-year deorbit requirement. "
                    f"An active deorbit maneuver will be required at end of mission. "
                    f"Verify propellant margin for disposal burn."
                ),
                value=estimated_lifetime,
                threshold=5.0,
                unit="years",
                standard_clause="FCC 47 CFR Part 25.114(d)(14)",
                body="FCC",
            )

    # End-of-life or decommissioned satellite
    remaining_window = 5.0 - years_since_mission_end

    if remaining_window <= 0:
        return RuleResult(
            rule_id="FCC-DEORBIT-01",
            status=RuleStatus.FAIL,
            message=(
                f"5-year compliance window expired {abs(remaining_window):.1f} years ago. "
                f"Estimated remaining orbital lifetime: {estimated_lifetime:.1f} years. "
                f"NON-COMPLIANT with FCC 47 CFR Part 25.114(d)(14)."
            ),
            value=estimated_lifetime,
            threshold=5.0,
            unit="years",
            standard_clause="FCC 47 CFR Part 25.114(d)(14)",
            body="FCC",
        )
    elif estimated_lifetime > remaining_window:
        return RuleResult(
            rule_id="FCC-DEORBIT-01",
            status=RuleStatus.FAIL,
            message=(
                f"Estimated orbital lifetime ({estimated_lifetime:.1f} years) exceeds "
                f"remaining compliance window ({remaining_window:.1f} years). "
                f"Active deorbit maneuver required immediately."
            ),
            value=estimated_lifetime,
            threshold=remaining_window,
            unit="years",
            standard_clause="FCC 47 CFR Part 25.114(d)(14)",
            body="FCC",
        )
    else:
        return RuleResult(
            rule_id="FCC-DEORBIT-01",
            status=RuleStatus.PASS,
            message=(
                f"Satellite will naturally deorbit within compliance window. "
                f"Estimated lifetime: {estimated_lifetime:.1f} years, "
                f"window remaining: {remaining_window:.1f} years."
            ),
            value=estimated_lifetime,
            threshold=remaining_window,
            unit="years",
            standard_clause="FCC 47 CFR Part 25.114(d)(14)",
            body="FCC",
        )


def check_casualty_risk(
    altitude_km: float,
    satellite_mass_kg: float = 100.0,
    demisable_fraction: float = 0.9,
) -> RuleResult:
    """
    FCC-DEORBIT-02: FCC 47 CFR Part 25.114(d)(14) — Casualty Risk Assessment
    Controlled reentry required if human casualty risk exceeds 1:10,000 (1e-4).

    The FCC requires that uncontrolled reentry casualty risk be less than
    1 in 10,000 (E(c) < 1 × 10^-4). Above this threshold, a controlled
    reentry must be planned.

    Simplified casualty risk model based on effective casualty area.
    """
    # Surviving mass (fraction that survives reentry without demising)
    surviving_mass_kg = satellite_mass_kg * (1.0 - demisable_fraction)

    # Effective casualty area (m^2) — empirical correlation from NASA Debris Assessment Tool
    # Ac = 0.785 * (0.2 * m_s^(1/3) + 0.56)^2  ... simplified
    # Using a simplified linear model for small satellites:
    if surviving_mass_kg <= 0:
        casualty_area_m2 = 0.0
    else:
        # Approximate: spherical fragment with radius proportional to mass^(1/3)
        import math
        fragment_radius_m = 0.56 * (surviving_mass_kg ** (1.0 / 3.0)) * 0.1
        casualty_area_m2 = math.pi * (fragment_radius_m + 0.6) ** 2

    # World population density (people/m^2) averaged over Earth's surface
    WORLD_POP = 8_100_000_000
    EARTH_SURFACE_M2 = 5.101e14
    pop_density = WORLD_POP / EARTH_SURFACE_M2  # ~1.59e-5 people/m^2

    # Fraction of Earth's surface that is land with population
    LAND_FRACTION = 0.3
    INHABITED_FRACTION = 0.95  # Most land is inhabited

    casualty_risk = casualty_area_m2 * pop_density * LAND_FRACTION * INHABITED_FRACTION

    threshold = 1e-4  # 1 in 10,000

    if casualty_risk <= threshold:
        return RuleResult(
            rule_id="FCC-DEORBIT-02",
            status=RuleStatus.PASS,
            message=(
                f"Estimated casualty risk E(c) ≈ {casualty_risk:.2e} is below "
                f"the FCC threshold of 1×10⁻⁴ (1:10,000). "
                f"Uncontrolled reentry is permissible."
            ),
            value=casualty_risk,
            threshold=threshold,
            unit="probability",
            standard_clause="FCC 47 CFR Part 25.114(d)(14)",
            body="FCC",
        )
    else:
        return RuleResult(
            rule_id="FCC-DEORBIT-02",
            status=RuleStatus.FAIL,
            message=(
                f"Estimated casualty risk E(c) ≈ {casualty_risk:.2e} EXCEEDS "
                f"the FCC threshold of 1×10⁻⁴. "
                f"Controlled reentry must be planned. "
                f"Surviving mass: {surviving_mass_kg:.1f} kg, "
                f"effective casualty area: {casualty_area_m2:.2f} m²."
            ),
            value=casualty_risk,
            threshold=threshold,
            unit="probability",
            standard_clause="FCC 47 CFR Part 25.114(d)(14)",
            body="FCC",
        )


def check_leo_orbit_altitude(altitude_km: float) -> RuleResult:
    """
    FCC-LEO-01: FCC definition of LEO (below 2000 km).
    Determines which rules apply. Not a pass/fail — informational classification.
    """
    is_leo = altitude_km < 2000.0

    if not is_leo:
        return RuleResult(
            rule_id="FCC-LEO-01",
            status=RuleStatus.SKIP,
            message=(
                f"Satellite altitude {altitude_km:.0f} km is above LEO (2000 km). "
                f"FCC 5-year deorbit rule applies only to LEO satellites."
            ),
            value=altitude_km,
            threshold=2000.0,
            unit="km",
            standard_clause="FCC 47 CFR Part 25.114(d)(14)",
            body="FCC",
        )

    return RuleResult(
        rule_id="FCC-LEO-01",
        status=RuleStatus.PASS,
        message=(
            f"Satellite confirmed in LEO at {altitude_km:.0f} km altitude. "
            f"FCC post-mission disposal rules (5-year deorbit) are applicable."
        ),
        value=altitude_km,
        threshold=2000.0,
        unit="km",
        standard_clause="FCC 47 CFR Part 25.114(d)(14)",
        body="FCC",
    )
