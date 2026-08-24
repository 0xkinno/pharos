"""
IADC Rule Evaluators — IADC Space Debris Mitigation Guidelines (IADC-02-01 Rev 3)

Implements rules derived from the Inter-Agency Space Debris Coordination
Committee (IADC) Space Debris Mitigation Guidelines, the foundational
international technical consensus document for debris mitigation.

Source: IADC-02-01, Rev. 3 (2021)
Available: https://www.iadc-home.org/documents_public/
Members: ASI, CNES, CNSA, CSA, DLR, ESA, ISRO, JAXA, NASA, ROSCOSMOS, UKSA
"""
from __future__ import annotations

import logging

from app.models.compliance import RuleResult, RuleStatus
from app.services.lifetime_estimator import estimate_orbital_lifetime_years

logger = logging.getLogger(__name__)


def check_orbital_lifetime(
    altitude_km: float,
    area_to_mass_ratio: float = 0.01,
    eccentricity: float = 0.0,
    solar_activity: str = "moderate",
) -> RuleResult:
    """
    IADC-LIFE-01: IADC-02-01 Rev 3, Section 5.3.2
    Post-mission orbital lifetime should not exceed 25 years.

    This is the original IADC guideline (not legally binding, but widely adopted).
    Note: The FCC's 5-year rule (FCC-DEORBIT-01) is stricter for US-licensed operators.
    The IADC 25-year guideline remains the international consensus for operators
    not subject to the FCC's jurisdiction.
    """
    estimated_lifetime = estimate_orbital_lifetime_years(
        altitude_km=altitude_km,
        area_to_mass_ratio=area_to_mass_ratio,
        eccentricity=eccentricity,
        solar_activity=solar_activity,
    )

    if estimated_lifetime <= 25.0:
        return RuleResult(
            rule_id="IADC-LIFE-01",
            status=RuleStatus.PASS,
            message=(
                f"Estimated orbital lifetime {estimated_lifetime:.1f} years is within "
                f"the IADC 25-year guideline."
            ),
            value=estimated_lifetime,
            threshold=25.0,
            unit="years",
            standard_clause="IADC-02-01 Rev 3, Section 5.3.2",
            body="IADC",
        )
    else:
        return RuleResult(
            rule_id="IADC-LIFE-01",
            status=RuleStatus.FAIL,
            message=(
                f"Estimated orbital lifetime {estimated_lifetime:.1f} years EXCEEDS "
                f"the IADC 25-year guideline. Disposal orbit maneuver required. "
                f"Note: IADC guidelines are not legally binding but are adopted by "
                f"all major space agencies."
            ),
            value=estimated_lifetime,
            threshold=25.0,
            unit="years",
            standard_clause="IADC-02-01 Rev 3, Section 5.3.2",
            body="IADC",
        )


def check_passivation(
    has_passivation_plan: bool = False,
    remaining_propellant_estimated: bool = True,
    pressure_vessels_vented: bool = False,
    batteries_discharged: bool = False,
) -> RuleResult:
    """
    IADC-PASS-01: IADC-02-01 Rev 3, Section 5.2.3
    Residual energy sources must be depleted (passivated) at end of mission.

    Passivation prevents on-orbit explosions that create debris clouds.
    The Ariane 44L rocket body that exploded in 1986 generated >500 trackable
    fragments. Passivation requirements prevent such events.

    Sources of stored energy:
    - Residual propellant (propellant dump or burn-to-depletion)
    - Pressurized systems (vent all pressurant)
    - Batteries (discharge to safe level)
    - Flywheels (spin down)
    """
    issues = []
    if not has_passivation_plan:
        issues.append("No documented passivation plan")
    if remaining_propellant_estimated and not has_passivation_plan:
        issues.append("Residual propellant estimated but passivation unconfirmed")
    if not pressure_vessels_vented:
        issues.append("Pressure vessels not confirmed vented")
    if not batteries_discharged:
        issues.append("Battery discharge to safe level not confirmed")

    if not issues:
        return RuleResult(
            rule_id="IADC-PASS-01",
            status=RuleStatus.PASS,
            message=(
                "Passivation requirements met: passivation plan documented, "
                "pressure vessels vented, batteries discharged."
            ),
            value=None,
            threshold=None,
            unit=None,
            standard_clause="IADC-02-01 Rev 3, Section 5.2.3",
            body="IADC",
        )

    if has_passivation_plan:
        # Has plan but some items unconfirmed → FLAG
        return RuleResult(
            rule_id="IADC-PASS-01",
            status=RuleStatus.FLAG,
            message=(
                f"Passivation plan exists but some items unconfirmed: "
                f"{'; '.join(issues)}. "
                f"Verify all passivation steps are completed at EOL."
            ),
            value=None,
            threshold=None,
            unit=None,
            standard_clause="IADC-02-01 Rev 3, Section 5.2.3",
            body="IADC",
        )

    return RuleResult(
        rule_id="IADC-PASS-01",
        status=RuleStatus.FAIL,
        message=(
            f"Passivation requirements NOT met: {'; '.join(issues)}. "
            f"IADC-02-01 Rev 3 Section 5.2.3 requires all stored energy sources "
            f"to be depleted at end of operational mission."
        ),
        value=None,
        threshold=None,
        unit=None,
        standard_clause="IADC-02-01 Rev 3, Section 5.2.3",
        body="IADC",
    )


def check_disposal_collision_probability(
    collision_probability: float = 0.0,
) -> RuleResult:
    """
    IADC-COLL-01: IADC-02-01 Rev 3, Section 5.3.1
    Probability of collision during disposal phase should be less than 0.001.

    During the disposal maneuver (deorbit burn), the satellite crosses multiple
    orbital shells. The probability of collision with resident space objects
    during this crossing should be less than 1 in 1,000 (0.001).
    """
    threshold = 0.001

    if collision_probability <= 0.0:
        # Not enough data to assess — flag for review
        return RuleResult(
            rule_id="IADC-COLL-01",
            status=RuleStatus.FLAG,
            message=(
                "Collision probability during disposal phase could not be assessed "
                "(no conjunction data available). Operators should obtain space "
                "situational awareness data from SSA providers before executing "
                "disposal maneuver. IADC-02-01 Rev 3 Section 5.3.1 requires P(c) < 0.001."
            ),
            value=collision_probability,
            threshold=threshold,
            unit="probability",
            standard_clause="IADC-02-01 Rev 3, Section 5.3.1",
            body="IADC",
        )

    if collision_probability < threshold:
        return RuleResult(
            rule_id="IADC-COLL-01",
            status=RuleStatus.PASS,
            message=(
                f"Collision probability during disposal P(c) = {collision_probability:.2e} "
                f"is below the IADC threshold of 0.001 (1 in 1,000)."
            ),
            value=collision_probability,
            threshold=threshold,
            unit="probability",
            standard_clause="IADC-02-01 Rev 3, Section 5.3.1",
            body="IADC",
        )

    return RuleResult(
        rule_id="IADC-COLL-01",
        status=RuleStatus.FAIL,
        message=(
            f"Collision probability during disposal P(c) = {collision_probability:.2e} "
            f"EXCEEDS the IADC threshold of 0.001. "
            f"Disposal maneuver must be re-planned to reduce collision risk."
        ),
        value=collision_probability,
        threshold=threshold,
        unit="probability",
        standard_clause="IADC-02-01 Rev 3, Section 5.3.1",
        body="IADC",
    )


def check_controlled_reentry_accuracy(
    target_zone_defined: bool = False,
    impact_zone_land_fraction: float = 0.3,
) -> RuleResult:
    """
    IADC-REENTRY-01: IADC-02-01 Rev 3, Section 5.4
    Controlled reentries should target uninhabited ocean zones.

    Controlled reentry disposal maneuvers should target unpopulated areas,
    specifically the South Pacific Oceanic Uninhabited Area (SPOUA) —
    also called Point Nemo.
    """
    if not target_zone_defined:
        return RuleResult(
            rule_id="IADC-REENTRY-01",
            status=RuleStatus.FLAG,
            message=(
                "No controlled reentry target zone defined. "
                "If satellite mass or altitude requires controlled reentry, "
                "IADC-02-01 Section 5.4 recommends targeting uninhabited ocean areas "
                "(e.g., South Pacific Oceanic Uninhabited Area)."
            ),
            value=None,
            threshold=None,
            unit=None,
            standard_clause="IADC-02-01 Rev 3, Section 5.4",
            body="IADC",
        )

    # Impact zone predominantly ocean (land fraction < 5%)
    if impact_zone_land_fraction <= 0.05:
        return RuleResult(
            rule_id="IADC-REENTRY-01",
            status=RuleStatus.PASS,
            message=(
                f"Controlled reentry target zone defined with land fraction "
                f"{impact_zone_land_fraction:.0%}. Target zone is predominantly ocean."
            ),
            value=impact_zone_land_fraction,
            threshold=0.05,
            unit="land fraction",
            standard_clause="IADC-02-01 Rev 3, Section 5.4",
            body="IADC",
        )

    return RuleResult(
        rule_id="IADC-REENTRY-01",
        status=RuleStatus.FLAG,
        message=(
            f"Controlled reentry target zone has land fraction {impact_zone_land_fraction:.0%}, "
            f"which includes populated areas. IADC recommends targeting uninhabited ocean regions."
        ),
        value=impact_zone_land_fraction,
        threshold=0.05,
        unit="land fraction",
        standard_clause="IADC-02-01 Rev 3, Section 5.4",
        body="IADC",
    )
