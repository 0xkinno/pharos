"""
ESA Zero Debris Charter Rule Evaluators

Implements rules derived from the ESA Zero Debris Charter, adopted in
November 2023 at the ESA Space Summit. The charter commits signatories to
achieving near-zero debris creation by 2030.

Source: ESA Zero Debris Charter (2023)
Available: https://www.esa.int/Space_Safety/Space_Debris/ESA_s_Zero_Debris_charter
Signatories include: ESA, national space agencies, and commercial operators
"""
from __future__ import annotations

import logging

from app.models.compliance import RuleResult, RuleStatus
from app.services.lifetime_estimator import estimate_orbital_lifetime_years

logger = logging.getLogger(__name__)


def check_no_intentional_release(
    intentional_debris_released: bool = False,
    operational_debris_count: int = 0,
) -> RuleResult:
    """
    ESA-ZD-01: ESA Zero Debris Charter, Commitment 2
    No intentional release of debris in orbit.

    The ESA Zero Debris Charter's Commitment 2 requires that signatories
    ensure no intentional release of debris in orbit. This is a stronger
    commitment than most existing guidelines — it applies not just to
    protected regions but to all orbital altitudes.
    """
    if not intentional_debris_released and operational_debris_count == 0:
        return RuleResult(
            rule_id="ESA-ZD-01",
            status=RuleStatus.PASS,
            message=(
                "No intentional debris release detected. "
                "Compliant with ESA Zero Debris Charter Commitment 2."
            ),
            value=float(operational_debris_count),
            threshold=0.0,
            unit="debris objects",
            standard_clause="ESA Zero Debris Charter, Commitment 2",
            body="ESA",
        )

    total_debris = operational_debris_count + (1 if intentional_debris_released else 0)
    return RuleResult(
        rule_id="ESA-ZD-01",
        status=RuleStatus.FAIL,
        message=(
            f"Intentional debris release detected: {total_debris} object(s). "
            f"ESA Zero Debris Charter Commitment 2 prohibits any intentional "
            f"release of debris in orbit. The charter targets near-zero debris "
            f"creation by 2030 across all orbital regimes."
        ),
        value=float(total_debris),
        threshold=0.0,
        unit="debris objects",
        standard_clause="ESA Zero Debris Charter, Commitment 2",
        body="ESA",
    )


def check_disposal_probability(
    disposal_success_probability: float = 0.0,
    has_propulsion: bool = True,
    altitude_km: float = 400.0,
    area_to_mass_ratio: float = 0.01,
) -> RuleResult:
    """
    ESA-ZD-02: ESA Zero Debris Charter, Commitment 3
    Probability of successful post-mission disposal must exceed 0.9 (90%).

    The Zero Debris Charter requires that all missions have a minimum
    0.9 probability of successful post-mission disposal. This accounts for
    hardware reliability, propulsion redundancy, and disposal plan robustness.
    """
    min_threshold = 0.9

    if disposal_success_probability > 0:
        # Operator-provided probability
        if disposal_success_probability >= min_threshold:
            return RuleResult(
                rule_id="ESA-ZD-02",
                status=RuleStatus.PASS,
                message=(
                    f"Disposal success probability {disposal_success_probability:.2f} "
                    f"meets ESA Zero Debris Charter requirement of ≥0.90 (90%)."
                ),
                value=disposal_success_probability,
                threshold=min_threshold,
                unit="probability",
                standard_clause="ESA Zero Debris Charter, Commitment 3",
                body="ESA",
            )
        else:
            return RuleResult(
                rule_id="ESA-ZD-02",
                status=RuleStatus.FAIL,
                message=(
                    f"Disposal success probability {disposal_success_probability:.2f} "
                    f"is BELOW the ESA Zero Debris Charter requirement of 0.90. "
                    f"Improve propulsion redundancy, disposal plan robustness, "
                    f"and failure mode analysis."
                ),
                value=disposal_success_probability,
                threshold=min_threshold,
                unit="probability",
                standard_clause="ESA Zero Debris Charter, Commitment 3",
                body="ESA",
            )

    # No operator-provided probability — estimate from orbit and propulsion
    # Natural decay < 5 years → high disposal probability even without propulsion
    natural_lifetime = estimate_orbital_lifetime_years(altitude_km=altitude_km, area_to_mass_ratio=area_to_mass_ratio)

    if natural_lifetime <= 1.0:
        estimated_p = 0.99
    elif natural_lifetime <= 5.0:
        estimated_p = 0.95
    elif natural_lifetime <= 10.0:
        estimated_p = 0.85
    elif natural_lifetime <= 25.0:
        estimated_p = 0.70 if has_propulsion else 0.50
    else:
        estimated_p = 0.50 if has_propulsion else 0.20

    if estimated_p >= min_threshold:
        return RuleResult(
            rule_id="ESA-ZD-02",
            status=RuleStatus.PASS,
            message=(
                f"Estimated disposal probability ~{estimated_p:.2f} based on orbit parameters. "
                f"Natural orbital lifetime: {natural_lifetime:.1f} years. "
                f"Meets ESA Zero Debris Charter 0.90 threshold."
            ),
            value=estimated_p,
            threshold=min_threshold,
            unit="probability",
            standard_clause="ESA Zero Debris Charter, Commitment 3",
            body="ESA",
        )

    return RuleResult(
        rule_id="ESA-ZD-02",
        status=RuleStatus.FLAG,
        message=(
            f"Estimated disposal probability ~{estimated_p:.2f} may be below "
            f"ESA Zero Debris Charter requirement of 0.90. "
            f"Natural orbital lifetime: {natural_lifetime:.1f} years. "
            f"Operator should provide detailed disposal reliability analysis."
        ),
        value=estimated_p,
        threshold=min_threshold,
        unit="probability",
        standard_clause="ESA Zero Debris Charter, Commitment 3",
        body="ESA",
    )


def check_debris_free_operations(
    operational_maneuvers_planned: bool = True,
    collision_avoidance_capability: bool = True,
    ssa_data_shared: bool = False,
) -> RuleResult:
    """
    ESA-ZD-03: ESA Zero Debris Charter, Commitment 4
    Operational missions should be debris-free (no collision avoidance debris creation).

    This commitment requires that satellites have collision avoidance capability
    and that operators share space situational awareness (SSA) data.
    """
    issues = []
    if not operational_maneuvers_planned:
        issues.append("No collision avoidance maneuvers planned")
    if not collision_avoidance_capability:
        issues.append("No collision avoidance capability (propulsion)")
    if not ssa_data_shared:
        issues.append("SSA data not shared with space traffic management providers")

    if not issues:
        return RuleResult(
            rule_id="ESA-ZD-03",
            status=RuleStatus.PASS,
            message=(
                "Debris-free operations requirements met: collision avoidance capability "
                "confirmed, maneuvers planned, SSA data sharing active."
            ),
            value=None,
            threshold=None,
            unit=None,
            standard_clause="ESA Zero Debris Charter, Commitment 4",
            body="ESA",
        )

    if collision_avoidance_capability:
        return RuleResult(
            rule_id="ESA-ZD-03",
            status=RuleStatus.FLAG,
            message=(
                f"Some debris-free operations items need attention: {'; '.join(issues)}. "
                f"ESA Zero Debris Charter Commitment 4 targets fully debris-free operations."
            ),
            value=None,
            threshold=None,
            unit=None,
            standard_clause="ESA Zero Debris Charter, Commitment 4",
            body="ESA",
        )

    return RuleResult(
        rule_id="ESA-ZD-03",
        status=RuleStatus.FAIL,
        message=(
            f"Debris-free operations requirements not met: {'; '.join(issues)}. "
            f"ESA Zero Debris Charter requires collision avoidance capability "
            f"for all missions in protected orbital regions."
        ),
        value=None,
        threshold=None,
        unit=None,
        standard_clause="ESA Zero Debris Charter, Commitment 4",
        body="ESA",
    )
