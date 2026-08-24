"""
Tests for ESA Zero Debris Charter Rule Evaluators

Tests for: ESA-ZD-01, ESA-ZD-02, ESA-ZD-03
"""
import pytest
from app.models.compliance import RuleStatus
import app.evaluators.esa_zero_debris as esa


class TestESAZeroDebris01:
    """ESA-ZD-01: No intentional debris release."""

    def test_no_debris_passes(self):
        """No intentional debris release → PASS."""
        result = esa.check_no_intentional_release(
            intentional_debris_released=False,
            operational_debris_count=0,
        )
        assert result.rule_id == "ESA-ZD-01"
        assert result.status == RuleStatus.PASS

    def test_intentional_release_fails(self):
        """Any intentional debris release → FAIL."""
        result = esa.check_no_intentional_release(
            intentional_debris_released=True,
            operational_debris_count=0,
        )
        assert result.rule_id == "ESA-ZD-01"
        assert result.status == RuleStatus.FAIL

    def test_operational_debris_fails(self):
        """Operational debris objects released → FAIL."""
        result = esa.check_no_intentional_release(
            intentional_debris_released=False,
            operational_debris_count=3,
        )
        assert result.status == RuleStatus.FAIL
        assert result.value == 3.0

    def test_cites_esa_charter_commitment_2(self):
        """Must cite ESA Zero Debris Charter Commitment 2."""
        result = esa.check_no_intentional_release(False, 0)
        assert "Commitment 2" in result.standard_clause
        assert result.body == "ESA"


class TestESAZeroDebris02:
    """ESA-ZD-02: Disposal probability ≥ 90%."""

    def test_high_probability_passes(self):
        """P(disposal) = 0.95 → PASS."""
        result = esa.check_disposal_probability(disposal_success_probability=0.95)
        assert result.rule_id == "ESA-ZD-02"
        assert result.status == RuleStatus.PASS

    def test_exact_threshold_passes(self):
        """P(disposal) = 0.90 → PASS (exactly at threshold)."""
        result = esa.check_disposal_probability(disposal_success_probability=0.90)
        assert result.status == RuleStatus.PASS

    def test_below_threshold_fails(self):
        """P(disposal) = 0.70 → FAIL."""
        result = esa.check_disposal_probability(disposal_success_probability=0.70)
        assert result.rule_id == "ESA-ZD-02"
        assert result.status == RuleStatus.FAIL

    def test_estimated_low_orbit_passes(self):
        """Low orbit satellite (300 km) → estimated P very high → PASS.
        At 300 km, natural lifetime is < 1 year, so disposal probability estimate is 0.99.
        """
        result = esa.check_disposal_probability(
            disposal_success_probability=0.0,  # Estimate from orbit
            altitude_km=300.0,
        )
        assert result.status == RuleStatus.PASS

    def test_threshold_is_09(self):
        """Threshold must be 0.9."""
        result = esa.check_disposal_probability(disposal_success_probability=0.95)
        assert result.threshold == 0.9

    def test_cites_esa_charter_commitment_3(self):
        """Must cite ESA Zero Debris Charter Commitment 3."""
        result = esa.check_disposal_probability(disposal_success_probability=0.95)
        assert "Commitment 3" in result.standard_clause


class TestESAZeroDebris03:
    """ESA-ZD-03: Debris-free operations."""

    def test_full_compliance_passes(self):
        """All criteria met → PASS."""
        result = esa.check_debris_free_operations(
            operational_maneuvers_planned=True,
            collision_avoidance_capability=True,
            ssa_data_shared=True,
        )
        assert result.rule_id == "ESA-ZD-03"
        assert result.status == RuleStatus.PASS

    def test_no_ca_capability_fails(self):
        """No collision avoidance capability → FAIL."""
        result = esa.check_debris_free_operations(
            operational_maneuvers_planned=False,
            collision_avoidance_capability=False,
            ssa_data_shared=False,
        )
        assert result.status == RuleStatus.FAIL

    def test_partial_compliance_flags(self):
        """CA capability but no SSA sharing → FLAG."""
        result = esa.check_debris_free_operations(
            operational_maneuvers_planned=True,
            collision_avoidance_capability=True,
            ssa_data_shared=False,
        )
        assert result.status == RuleStatus.FLAG
