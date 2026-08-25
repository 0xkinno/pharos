"""
UN COPUOS Rule Evaluators — Long-Term Sustainability of Outer Space Activities

Implements rules derived from the 21 Guidelines for the Long-Term
Sustainability of Outer Space Activities, adopted by the UN Committee on
the Peaceful Uses of Outer Space (COPUOS) in 2019.

Source: UN COPUOS LTS Guidelines (A/74/20, 2019)
Available: https://www.unoosa.org/oosa/en/ourwork/topics/long-term-sustainability-of-outer-space-activities.html
"""
from __future__ import annotations

import logging

from app.models.compliance import RuleResult, RuleStatus

logger = logging.getLogger(__name__)


def check_registration(
    is_registered_with_un: bool = False,
    national_registry_registered: bool = False,
    cospar_id: str | None = None,
) -> RuleResult:
    """
    COPUOS-REG-01: UN COPUOS LTS Guideline B.1 — Registration Convention Compliance

    The UN Registration Convention (1975) requires states to maintain a registry
    of objects launched into outer space and to furnish information to the UN
    Secretary-General. COPUOS LTS Guideline B.1 reinforces this requirement.

    The Convention on Registration of Objects Launched into Outer Space
    (UNGA Res. 3235 (XXIX)) entered into force 1976.
    """
    # COSPAR ID presence indicates international registration
    has_cospar = bool(cospar_id and len(cospar_id.strip()) > 0)

    if is_registered_with_un or has_cospar:
        return RuleResult(
            rule_id="COPUOS-REG-01",
            status=RuleStatus.PASS,
            message=(
                "Satellite has UN registry entry"
                + (f" (COSPAR ID: {cospar_id})" if has_cospar else "")
                + ". Compliant with Registration Convention and COPUOS LTS Guideline B.1."
            ),
            value=None,
            threshold=None,
            unit=None,
            standard_clause="UN COPUOS LTS Guideline B.1",
            body="COPUOS",
        )

    if national_registry_registered:
        return RuleResult(
            rule_id="COPUOS-REG-01",
            status=RuleStatus.FLAG,
            message=(
                "Satellite is registered in national registry but UN registration status "
                "unconfirmed. Under the Registration Convention, launching states must "
                "furnish UN registration data. Verify timely UN notification."
            ),
            value=None,
            threshold=None,
            unit=None,
            standard_clause="UN COPUOS LTS Guideline B.1",
            body="COPUOS",
        )

    return RuleResult(
        rule_id="COPUOS-REG-01",
        status=RuleStatus.FAIL,
        message=(
            "No UN or national registry registration confirmed. "
            "COPUOS LTS Guideline B.1 requires all space objects to be registered "
            "with the UN Registry of Objects Launched into Outer Space (UNOOSA). "
            "Failure to register is a violation of the 1975 Registration Convention."
        ),
        value=None,
        threshold=None,
        unit=None,
        standard_clause="UN COPUOS LTS Guideline B.1",
        body="COPUOS",
    )


def check_data_sharing(
    orbital_data_shared_publicly: bool = False,
    ssa_coordination_active: bool = False,
    shares_with_spacefence: bool = False,
) -> RuleResult:
    """
    COPUOS-COORD-01: UN COPUOS LTS Guideline B.2
    Operators should share orbital data for conjunction assessment.

    COPUOS LTS Guideline B.2 recommends that operators share orbital element
    data and coordinate conjunction assessments. This improves space traffic
    management and reduces collision risk.
    """
    score = sum([
        orbital_data_shared_publicly,
        ssa_coordination_active,
        shares_with_spacefence,
    ])

    if score >= 2:
        return RuleResult(
            rule_id="COPUOS-COORD-01",
            status=RuleStatus.PASS,
            message=(
                "Orbital data sharing and SSA coordination requirements met. "
                "Compliant with COPUOS LTS Guideline B.2."
            ),
            value=float(score),
            threshold=2.0,
            unit="criteria met",
            standard_clause="UN COPUOS LTS Guideline B.2",
            body="COPUOS",
        )

    if score == 1:
        return RuleResult(
            rule_id="COPUOS-COORD-01",
            status=RuleStatus.FLAG,
            message=(
                f"Partial orbital data sharing: {score}/3 criteria met. "
                f"COPUOS LTS Guideline B.2 recommends sharing orbital data publicly, "
                f"participating in SSA coordination, and sharing with SpaceFence/18 SDS. "
                f"Improve data sharing practices."
            ),
            value=float(score),
            threshold=2.0,
            unit="criteria met",
            standard_clause="UN COPUOS LTS Guideline B.2",
            body="COPUOS",
        )

    return RuleResult(
        rule_id="COPUOS-COORD-01",
        status=RuleStatus.FAIL,
        message=(
            "No orbital data sharing or SSA coordination confirmed. "
            "COPUOS LTS Guideline B.2 calls on operators to share orbital data "
            "to support global space traffic management. "
            "Register with space-track.org or equivalent SSA provider."
        ),
        value=float(score),
        threshold=2.0,
        unit="criteria met",
        standard_clause="UN COPUOS LTS Guideline B.2",
        body="COPUOS",
    )


def check_maneuver_notification(
    large_maneuvers_planned: bool = False,
    notification_provided: bool = False,
    advance_notice_hours: float = 0.0,
) -> RuleResult:
    """
    COPUOS-NOTIF-01: UN COPUOS LTS Guideline C.1
    Operators should notify other operators of planned maneuvers that
    may affect conjunction predictions.

    For maneuvers that would significantly alter the orbit prediction,
    advance notification to spaceflight safety coordinators is recommended.
    """
    if not large_maneuvers_planned:
        return RuleResult(
            rule_id="COPUOS-NOTIF-01",
            status=RuleStatus.PASS,
            message=(
                "No large maneuvers planned that would require advance notification. "
                "Compliant with COPUOS LTS Guideline C.1."
            ),
            value=None,
            threshold=None,
            unit=None,
            standard_clause="UN COPUOS LTS Guideline C.1",
            body="COPUOS",
        )

    if notification_provided and advance_notice_hours >= 24.0:
        return RuleResult(
            rule_id="COPUOS-NOTIF-01",
            status=RuleStatus.PASS,
            message=(
                f"Maneuver notification provided {advance_notice_hours:.0f} hours in advance. "
                f"Meets COPUOS LTS Guideline C.1 best practice of 24-hour advance notice."
            ),
            value=advance_notice_hours,
            threshold=24.0,
            unit="hours",
            standard_clause="UN COPUOS LTS Guideline C.1",
            body="COPUOS",
        )

    if notification_provided and advance_notice_hours < 24.0:
        return RuleResult(
            rule_id="COPUOS-NOTIF-01",
            status=RuleStatus.FLAG,
            message=(
                f"Maneuver notification provided only {advance_notice_hours:.0f} hours in advance. "
                f"COPUOS LTS Guideline C.1 recommends at least 24 hours advance notice "
                f"for maneuvers that affect conjunction predictions."
            ),
            value=advance_notice_hours,
            threshold=24.0,
            unit="hours",
            standard_clause="UN COPUOS LTS Guideline C.1",
            body="COPUOS",
        )

    return RuleResult(
        rule_id="COPUOS-NOTIF-01",
        status=RuleStatus.FLAG,
        message=(
            "Large maneuvers planned but notification status unconfirmed. "
            "COPUOS LTS Guideline C.1 recommends notifying other operators and "
            "SSA providers before executing maneuvers that alter orbit predictions."
        ),
        value=None,
        threshold=None,
        unit=None,
        standard_clause="UN COPUOS LTS Guideline C.1",
        body="COPUOS",
    )
