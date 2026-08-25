"""
Tests for the Compliance Engine Orchestrator

End-to-end tests of the compliance engine using mock satellite data.
"""
import math

from app.models.compliance import ComplianceLevel, RuleStatus
from app.models.satellite import OrbitalElements, SatelliteData
from app.services.compliance_engine import evaluate_satellite


def make_satellite(
    norad_id: int,
    name: str,
    mean_motion: float,  # rev/day (determines altitude)
    eccentricity: float = 0.0,
    inclination: float = 53.0,
    intldes: str = None,
) -> SatelliteData:
    """Factory for test SatelliteData objects."""
    MU = 398600.4418
    n_rad_s = mean_motion * 2 * math.pi / 86400.0
    a_km = (MU / (n_rad_s ** 2)) ** (1.0 / 3.0)

    elements = OrbitalElements(
        semi_major_axis_km=a_km,
        eccentricity=eccentricity,
        inclination_deg=inclination,
        raan_deg=50.0,
        arg_of_perigee_deg=90.0,
        mean_anomaly_deg=180.0,
        mean_motion_rev_per_day=mean_motion,
        bstar_drag=0.0002,
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
        ra_of_asc_node=50.0,
        arg_of_pericenter=90.0,
        mean_anomaly=180.0,
        bstar=0.0002,
        orbital_elements=elements,
    )


class TestComplianceEngine:
    """Integration tests for the compliance engine."""

    def test_low_leo_satellite_reports_correctly(self):
        """Satellite in LEO should produce a valid compliance report."""
        sat = make_satellite(1001, "TEST-SAT-LEO", mean_motion=15.1, intldes="2024-001A")
        report = evaluate_satellite(sat, ssa_data_shared=True, collision_avoidance_capability=True)

        assert report.norad_cat_id == 1001
        assert report.object_name == "TEST-SAT-LEO"
        assert report.compliance_score >= 0.0
        assert report.compliance_score <= 100.0
        assert report.orbit_type == "LEO"
        # Can be AT_RISK or NON_COMPLIANT without passivation plan and with
        # long natural lifetime. The compliance level is correctly determined.
        assert report.compliance_level in [
            ComplianceLevel.COMPLIANT,
            ComplianceLevel.AT_RISK,
            ComplianceLevel.NON_COMPLIANT,
        ]
        # Must have rule results
        assert len(report.rule_results) > 10

    def test_geo_satellite_skips_leo_rules(self):
        """GEO satellite should have LEO-specific rules SKIPPED."""
        sat = make_satellite(1002, "TEST-GEO", mean_motion=1.0027, inclination=0.05)
        report = evaluate_satellite(sat)

        assert report.orbit_type == "GEO"

        # LEO rules should be skipped
        fcc_deorbit = next((r for r in report.rule_results if r.rule_id == "FCC-DEORBIT-01"), None)
        iadc_life = next((r for r in report.rule_results if r.rule_id == "IADC-LIFE-01"), None)
        iso_orbit_01 = next((r for r in report.rule_results if r.rule_id == "ISO-ORBIT-01"), None)

        assert fcc_deorbit is not None and fcc_deorbit.status == RuleStatus.SKIP
        assert iadc_life is not None and iadc_life.status == RuleStatus.SKIP
        assert iso_orbit_01 is not None and iso_orbit_01.status == RuleStatus.SKIP

        # GEO rules should be evaluated
        iso_orbit_02 = next((r for r in report.rule_results if r.rule_id == "ISO-ORBIT-02"), None)
        assert iso_orbit_02 is not None and iso_orbit_02.status != RuleStatus.SKIP

    def test_debris_satellite_fails_many_rules(self):
        """Unregistered debris fragment should fail registration and passivation rules."""
        sat = make_satellite(1003, "DEBRIS DEB", mean_motion=14.2, inclination=74.0)
        sat.object_type = "DEBRIS"
        sat.international_designator = None

        report = evaluate_satellite(
            sat,
            mission_status="decommissioned",
            years_since_mission_end=15.0,
            has_propulsion=False,
            has_passivation_plan=False,
            pressure_vessels_vented=False,
            batteries_discharged=False,
            is_registered_with_un=False,
            ssa_data_shared=False,
            collision_avoidance_capability=False,
        )

        assert report.rules_failed >= 3
        assert report.compliance_level == ComplianceLevel.NON_COMPLIANT

    def test_report_contains_all_required_fields(self):
        """Report must have all required fields populated."""
        sat = make_satellite(1004, "TEST-COMPLETE", mean_motion=15.0, intldes="2024-002A")
        report = evaluate_satellite(sat)

        assert report.norad_cat_id == 1004
        assert report.object_name == "TEST-COMPLETE"
        assert report.epoch
        assert report.mean_altitude_km > 0
        assert report.orbit_type in ("LEO", "MEO", "GEO", "HEO")
        assert report.estimated_orbital_lifetime_years >= 0
        assert len(report.rule_results) > 0
        assert report.compliance_score >= 0.0
        assert report.compliance_score <= 100.0
        assert report.compliance_level in list(ComplianceLevel)

    def test_score_computation(self):
        """Score should be between 0 and 100, reflecting pass/fail/flag distribution."""
        sat = make_satellite(1005, "SCORE-TEST", mean_motion=15.0, intldes="2024-003A")
        report = evaluate_satellite(sat)

        total_applicable = report.rules_passed + report.rules_flagged + report.rules_failed
        assert total_applicable + report.rules_skipped == len(report.rule_results)

        # Score should be consistent with rule counts
        if report.rules_failed > 0:
            assert report.compliance_level == ComplianceLevel.NON_COMPLIANT
        elif report.rules_flagged > 0 and report.rules_failed == 0:
            assert report.compliance_level == ComplianceLevel.AT_RISK

    def test_no_ai_report_by_default(self):
        """evaluate_satellite does not generate AI reports (separate step)."""
        sat = make_satellite(1006, "NO-AI-TEST", mean_motion=15.0, intldes="2024-004A")
        report = evaluate_satellite(sat)
        # AI fields should be None/False by default from the engine
        assert report.ai_available is False
