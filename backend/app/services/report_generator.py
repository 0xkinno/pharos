"""
Granite Instruct Report Generator

Generates plain-language compliance reports from the deterministic
compliance engine output using IBM Granite 3.1 8B Instruct.

Architecture principle: Granite EXPLAINS what the engine DETECTED.
The AI never determines compliance. It translates the structured
pass/fail/flag results into operator-readable language.

Fallback: If watsonx.ai is unavailable, returns a structured text
report built from the compliance data without AI prose.
"""
from __future__ import annotations

import logging

from app.models.compliance import ComplianceLevel, ComplianceReport, RuleStatus

logger = logging.getLogger(__name__)


def _build_structured_fallback_report(report: ComplianceReport) -> str:
    """
    Build a structured text report from compliance data without AI.
    Used when watsonx.ai is unavailable.
    """
    level_emoji = {
        ComplianceLevel.COMPLIANT: "✓ COMPLIANT",
        ComplianceLevel.AT_RISK: "⚠ AT RISK",
        ComplianceLevel.NON_COMPLIANT: "✗ NON-COMPLIANT",
        ComplianceLevel.UNKNOWN: "? UNKNOWN",
    }

    lines = [
        f"PHAROS COMPLIANCE REPORT — {report.object_name} (NORAD {report.norad_cat_id})",
        f"Overall Status: {level_emoji.get(report.compliance_level, 'UNKNOWN')}",
        f"Compliance Score: {report.compliance_score:.1f}/100",
        "",
        "ORBITAL PARAMETERS",
        f"  Altitude: {report.mean_altitude_km:.0f} km ({report.orbit_type})",
        f"  Perigee: {report.perigee_km:.0f} km | Apogee: {report.apogee_km:.0f} km",
        f"  Inclination: {report.inclination_deg:.2f}° | Eccentricity: {report.eccentricity:.4f}",
        f"  Estimated Orbital Lifetime: {report.estimated_orbital_lifetime_years:.1f} years",
        "",
        "RULE EVALUATION SUMMARY",
        f"  Passed: {report.rules_passed} | Flagged: {report.rules_flagged} | "
        f"Failed: {report.rules_failed} | Skipped: {report.rules_skipped}",
        "",
        "DETAILED FINDINGS",
    ]

    for result in report.rule_results:
        if result.status == RuleStatus.SKIP:
            continue
        status_str = {
            RuleStatus.PASS: "PASS",
            RuleStatus.FLAG: "FLAG",
            RuleStatus.FAIL: "FAIL",
            RuleStatus.ERROR: "ERROR",
        }.get(result.status, "?")

        lines.append(f"  [{status_str}] {result.rule_id} — {result.standard_clause}")
        lines.append(f"        {result.message}")
        if result.value is not None and result.unit:
            lines.append(f"        Value: {result.value} {result.unit} | Threshold: {result.threshold} {result.unit}")

    lines.extend([
        "",
        f"Generated: {report.report_generated_at.isoformat()}",
        "Rule evaluations are deterministic and independently verifiable.",
    ])

    return "\n".join(lines)


def _build_instruct_messages(report: ComplianceReport) -> tuple[str, str]:
    """
    Build system + user messages for the chat API.
    Returns (system_prompt, user_message).
    """
    failed_rules = [r for r in report.rule_results if r.status == RuleStatus.FAIL]
    flagged_rules = [r for r in report.rule_results if r.status == RuleStatus.FLAG]
    passed_rules = [r for r in report.rule_results if r.status == RuleStatus.PASS]

    findings_text = ""
    if failed_rules:
        findings_text += "NON-COMPLIANT findings:\n"
        for r in failed_rules:
            findings_text += f"  - {r.rule_id} ({r.standard_clause}): {r.message}\n"

    if flagged_rules:
        findings_text += "\nAT-RISK findings requiring attention:\n"
        for r in flagged_rules:
            findings_text += f"  - {r.rule_id} ({r.standard_clause}): {r.message}\n"

    if passed_rules:
        findings_text += f"\nPASSING rules ({len(passed_rules)} checks): "
        findings_text += ", ".join(r.rule_id for r in passed_rules[:5])
        if len(passed_rules) > 5:
            findings_text += f" and {len(passed_rules) - 5} more"
        findings_text += "\n"

    system = (
        "You are PHAROS, an expert satellite orbital compliance analyst writing reports for satellite operators. "
        "Your job is to write a clear, precise, professional compliance assessment based solely on the "
        "deterministic rule evaluation results provided. "
        "Do NOT invent compliance findings — only explain what the evaluator found. "
        "Write for a technically literate satellite operator. Be direct. Use specific numbers. "
        "Do not hedge excessively. State clearly what is compliant, what is at risk, and what requires action."
    )

    user = (
        f"Write a professional compliance assessment for the following satellite.\n\n"
        f"SATELLITE: {report.object_name} (NORAD ID: {report.norad_cat_id})\n"
        f"ORBIT: {report.orbit_type} at {report.mean_altitude_km:.0f} km "
        f"(perigee {report.perigee_km:.0f} km / apogee {report.apogee_km:.0f} km)\n"
        f"INCLINATION: {report.inclination_deg:.2f}°\n"
        f"ESTIMATED ORBITAL LIFETIME: {report.estimated_orbital_lifetime_years:.1f} years\n"
        f"COMPLIANCE SCORE: {report.compliance_score:.1f}/100 — {report.compliance_level.value}\n"
        f"RULES: {report.rules_passed} passed | {report.rules_flagged} flagged | {report.rules_failed} failed\n\n"
        f"RULE EVALUATION FINDINGS:\n{findings_text}\n"
        f"Write a 3-paragraph assessment:\n"
        f"Paragraph 1: Overall compliance status and most critical findings.\n"
        f"Paragraph 2: Specific actions the operator must take (FAIL items) or should consider (FLAG items).\n"
        f"Paragraph 3: Risk context — regulatory implications and consequences of unaddressed violations.\n\n"
        f"Be specific with rule IDs and standard citations."
    )

    return system, user


def generate_compliance_report(report: ComplianceReport) -> str:
    """
    Generate a plain-language compliance report using the best available LLM.

    The AI EXPLAINS what the deterministic engine DETECTED — it never
    determines compliance. Returns a structured fallback if watsonx.ai
    is unavailable.
    """
    from app.ai.watsonx_client import get_watsonx_client

    client = get_watsonx_client()

    if not client.is_available():
        logger.info(
            "AI not available for %s. Using structured fallback.",
            report.object_name,
        )
        return _build_structured_fallback_report(report)

    system, user = _build_instruct_messages(report)

    try:
        # Use _chat directly to get the best response
        generated_text = client._chat(client._instruct_model, system=system, user=user)
        if generated_text:
            logger.info(
                "AI report generated for %s using %s (%d chars)",
                report.object_name,
                client.active_instruct_model,
                len(generated_text),
            )
            return generated_text.strip()
    except Exception as exc:
        logger.error("AI report generation failed: %s", exc)

    return _build_structured_fallback_report(report)
