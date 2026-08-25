"""
PDF Compliance Report Exporter

Generates a professional PDF compliance report using ReportLab.
"""
from __future__ import annotations

import logging
from io import BytesIO

from app.models.compliance import ComplianceReport, RuleStatus

logger = logging.getLogger(__name__)

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab not installed. PDF export will return a plain text fallback.")


# Status colors for PDF
_STATUS_COLORS = {
    RuleStatus.PASS: (0.06, 0.72, 0.51),   # Green
    RuleStatus.FLAG: (0.96, 0.62, 0.04),   # Amber
    RuleStatus.FAIL: (0.94, 0.27, 0.27),   # Red
    RuleStatus.SKIP: (0.53, 0.53, 0.63),   # Grey
    RuleStatus.ERROR: (0.5, 0.0, 0.5),     # Purple
}


def _hex_color(r: float, g: float, b: float):
    """Convert 0-1 RGB to ReportLab Color."""
    from reportlab.lib.colors import Color
    return Color(r, g, b)


def export_to_pdf(report: ComplianceReport) -> bytes:
    """
    Generate a PDF compliance report.
    Returns PDF bytes or plain text bytes if ReportLab is unavailable.
    """
    if not REPORTLAB_AVAILABLE:
        return _export_plain_text_fallback(report)

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    story = []

    # Colors
    pharos_blue = colors.HexColor("#3b82f6")
    text_primary = colors.HexColor("#1f2937")
    muted = colors.HexColor("#6b7280")
    pass_color = colors.HexColor("#10b981")
    flag_color = colors.HexColor("#f59e0b")
    fail_color = colors.HexColor("#ef4444")

    # Custom styles
    title_style = ParagraphStyle(
        "PharosTitle",
        fontSize=24,
        fontName="Helvetica-Bold",
        textColor=pharos_blue,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "PharosSubtitle",
        fontSize=12,
        fontName="Helvetica",
        textColor=muted,
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "PharosHeading",
        fontSize=14,
        fontName="Helvetica-Bold",
        textColor=text_primary,
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "PharosBody",
        fontSize=10,
        fontName="Helvetica",
        textColor=text_primary,
        spaceAfter=4,
    )
    small_style = ParagraphStyle(
        "PharosSmall",
        fontSize=8,
        fontName="Helvetica",
        textColor=muted,
    )

    compliance_color = {
        "COMPLIANT": pass_color,
        "AT_RISK": flag_color,
        "NON_COMPLIANT": fail_color,
        "UNKNOWN": muted,
    }.get(report.compliance_level.value, muted)

    # Header
    story.append(Paragraph("PHAROS", title_style))
    story.append(Paragraph("Satellite Compliance Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=pharos_blue))
    story.append(Spacer(1, 6 * mm))

    # Satellite info
    story.append(Paragraph(f"{report.object_name}", heading_style))
    story.append(Paragraph(
        f"NORAD ID: {report.norad_cat_id} | Orbit: {report.orbit_type} | "
        f"Generated: {report.report_generated_at.strftime('%Y-%m-%d %H:%M UTC') if report.report_generated_at else 'N/A'}",
        small_style,
    ))
    story.append(Spacer(1, 4 * mm))

    # Compliance score box
    score_data = [
        [
            Paragraph("<b>Compliance Score</b>", body_style),
            Paragraph(f"<b>{report.compliance_score:.1f} / 100</b>", body_style),
        ],
        [
            Paragraph("<b>Status</b>", body_style),
            Paragraph(
                f"<font color='#{_color_to_hex(compliance_color)}'><b>{report.compliance_level.value.replace('_', ' ')}</b></font>",
                body_style,
            ),
        ],
        [
            Paragraph("Rules Passed / Flagged / Failed", body_style),
            Paragraph(
                f"{report.rules_passed} / {report.rules_flagged} / {report.rules_failed}",
                body_style,
            ),
        ],
    ]
    score_table = Table(score_data, colWidths=[80 * mm, 80 * mm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, pharos_blue),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 4 * mm))

    # Orbital parameters
    story.append(Paragraph("Orbital Parameters", heading_style))
    orbital_data = [
        ["Parameter", "Value"],
        ["Mean Altitude", f"{report.mean_altitude_km:.0f} km"],
        ["Perigee / Apogee", f"{report.perigee_km:.0f} km / {report.apogee_km:.0f} km"],
        ["Inclination", f"{report.inclination_deg:.2f}°"],
        ["Eccentricity", f"{report.eccentricity:.6f}"],
        ["Mean Motion", f"{report.mean_motion_rev_per_day:.4f} rev/day"],
        ["Est. Orbital Lifetime", f"{report.estimated_orbital_lifetime_years:.1f} years"],
    ]
    orbital_table = Table(orbital_data, colWidths=[80 * mm, 80 * mm])
    orbital_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), pharos_blue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(orbital_table)
    story.append(Spacer(1, 4 * mm))

    # Rule Results
    story.append(Paragraph("Rule Evaluation Results", heading_style))

    rule_header = ["Rule ID", "Body", "Status", "Threshold / Value", "Standard Clause"]
    rule_rows = [rule_header]
    for r in report.rule_results:
        status_map = {
            RuleStatus.PASS: "PASS",
            RuleStatus.FLAG: "FLAG",
            RuleStatus.FAIL: "FAIL",
            RuleStatus.SKIP: "SKIP",
            RuleStatus.ERROR: "ERROR",
        }
        threshold_val = ""
        if r.value is not None and r.threshold is not None and r.unit:
            threshold_val = f"{r.value:.2f} / {r.threshold:.2f} {r.unit}"

        rule_rows.append([
            r.rule_id,
            r.body,
            status_map.get(r.status, "?"),
            threshold_val,
            Paragraph(r.standard_clause[:50], small_style),
        ])

    col_widths = [30 * mm, 20 * mm, 18 * mm, 38 * mm, 54 * mm]
    rules_table = Table(rule_rows, colWidths=col_widths)

    # Color-code status column
    rules_style = [
        ("BACKGROUND", (0, 0), (-1, 0), pharos_blue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]
    for i, r in enumerate(report.rule_results, start=1):
        color = {
            RuleStatus.PASS: colors.HexColor("#d1fae5"),
            RuleStatus.FLAG: colors.HexColor("#fef3c7"),
            RuleStatus.FAIL: colors.HexColor("#fee2e2"),
            RuleStatus.SKIP: colors.HexColor("#f3f4f6"),
        }.get(r.status, colors.white)
        rules_style.append(("BACKGROUND", (0, i), (-1, i), color))

    rules_table.setStyle(TableStyle(rules_style))
    story.append(rules_table)
    story.append(Spacer(1, 4 * mm))

    # AI Report
    if report.ai_report_text:
        story.append(Paragraph("AI-Generated Compliance Assessment", heading_style))
        story.append(Paragraph("(Generated by IBM Granite 3.1 8B Instruct via watsonx.ai)", small_style))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(report.ai_report_text.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 4 * mm))

    # Footer
    story.append(HRFlowable(width="100%", thickness=0.5, color=muted))
    story.append(Paragraph(
        "PHAROS is a pre-check compliance tool, not a certification authority. "
        "Orbital lifetime estimates use a simplified King-Hele model (±30–50% uncertainty). "
        "This report does not constitute legal or regulatory advice.",
        small_style,
    ))

    doc.build(story)
    return buf.getvalue()


def _color_to_hex(color) -> str:
    """Convert ReportLab color to hex string (without #)."""
    try:
        return f"{int(color.red * 255):02x}{int(color.green * 255):02x}{int(color.blue * 255):02x}"
    except Exception:
        return "000000"


def _export_plain_text_fallback(report: ComplianceReport) -> bytes:
    """Fallback: return plain text as bytes when ReportLab is unavailable."""
    lines = [
        "PHAROS Compliance Report",
        f"Satellite: {report.object_name} (NORAD {report.norad_cat_id})",
        f"Compliance Score: {report.compliance_score}/100 — {report.compliance_level.value}",
        "",
        f"Rules: {report.rules_passed} passed, {report.rules_flagged} flagged, {report.rules_failed} failed",
        "",
    ]
    for r in report.rule_results:
        if r.status.value != "SKIP":
            lines.append(f"[{r.status.value}] {r.rule_id}: {r.message}")
    return "\n".join(lines).encode("utf-8")
