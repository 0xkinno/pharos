"""
Tests for IADC Rule Evaluators

Tests for: IADC-LIFE-01, IADC-PASS-01, IADC-COLL-01, IADC-REENTRY-01
"""
from app.evaluators import iadc
from app.models.compliance import RuleStatus


class TestIADCLife01:
    """IADC-LIFE-01: 25-year orbital lifetime limit."""

    def test_very_low_orbit_passes(self):
        """Satellite at 300 km has very short lifetime → PASS."""
        result = iadc.check_orbital_lifetime(altitude_km=300.0)
        assert result.rule_id == "IADC-LIFE-01"
        assert result.status == RuleStatus.PASS
        assert result.value is not None
        assert result.value <= 25.0

    def test_medium_leo_passes(self):
        """Satellite at 400 km → PASS (within 25 years, ~3-5 yr)."""
        result = iadc.check_orbital_lifetime(altitude_km=400.0)
        assert result.status == RuleStatus.PASS

    def test_high_leo_fails(self):
        """Satellite at 1000 km has long lifetime > 25 years → FAIL."""
        result = iadc.check_orbital_lifetime(altitude_km=1000.0)
        assert result.rule_id == "IADC-LIFE-01"
        assert result.status == RuleStatus.FAIL
        assert result.value > 25.0

    def test_very_high_leo_fails(self):
        """Satellite at 1500 km has effectively infinite lifetime → FAIL."""
        result = iadc.check_orbital_lifetime(altitude_km=1500.0)
        assert result.status == RuleStatus.FAIL

    def test_threshold_is_25_years(self):
        """Threshold must be 25.0 years."""
        result = iadc.check_orbital_lifetime(altitude_km=500.0)
        assert result.threshold == 25.0
        assert result.unit == "years"

    def test_cites_iadc_section(self):
        """Result cites IADC-02-01 Rev 3."""
        result = iadc.check_orbital_lifetime(altitude_km=500.0)
        assert "IADC-02-01" in result.standard_clause
        assert "5.3.2" in result.standard_clause
        assert result.body == "IADC"


class TestIADCPass01:
    """IADC-PASS-01: Passivation requirement."""

    def test_full_passivation_passes(self):
        """All passivation steps completed → PASS."""
        result = iadc.check_passivation(
            has_passivation_plan=True,
            remaining_propellant_estimated=False,
            pressure_vessels_vented=True,
            batteries_discharged=True,
        )
        assert result.rule_id == "IADC-PASS-01"
        assert result.status == RuleStatus.PASS

    def test_no_passivation_fails(self):
        """No passivation plan at all → FAIL."""
        result = iadc.check_passivation(
            has_passivation_plan=False,
            pressure_vessels_vented=False,
            batteries_discharged=False,
        )
        assert result.rule_id == "IADC-PASS-01"
        assert result.status == RuleStatus.FAIL

    def test_plan_exists_incomplete_flags(self):
        """Plan exists but items unconfirmed → FLAG."""
        result = iadc.check_passivation(
            has_passivation_plan=True,
            remaining_propellant_estimated=True,
            pressure_vessels_vented=False,
            batteries_discharged=False,
        )
        assert result.status == RuleStatus.FLAG

    def test_cites_passivation_section(self):
        """Must cite IADC section 5.2.3."""
        result = iadc.check_passivation(has_passivation_plan=True, pressure_vessels_vented=True, batteries_discharged=True)
        assert "5.2.3" in result.standard_clause


class TestIADCColl01:
    """IADC-COLL-01: Collision probability during disposal."""

    def test_zero_probability_flags(self):
        """No data (p=0) → FLAG for operator review."""
        result = iadc.check_disposal_collision_probability(0.0)
        assert result.rule_id == "IADC-COLL-01"
        assert result.status == RuleStatus.FLAG

    def test_low_probability_passes(self):
        """P(c) = 0.0001 < 0.001 threshold → PASS."""
        result = iadc.check_disposal_collision_probability(0.0001)
        assert result.status == RuleStatus.PASS

    def test_probability_at_threshold_passes(self):
        """P(c) = 0.0009 < 0.001 → PASS."""
        result = iadc.check_disposal_collision_probability(0.0009)
        assert result.status == RuleStatus.PASS

    def test_probability_above_threshold_fails(self):
        """P(c) = 0.002 > 0.001 threshold → FAIL."""
        result = iadc.check_disposal_collision_probability(0.002)
        assert result.status == RuleStatus.FAIL

    def test_threshold_is_001(self):
        """Threshold must be 0.001."""
        result = iadc.check_disposal_collision_probability(0.0001)
        assert result.threshold == 0.001
