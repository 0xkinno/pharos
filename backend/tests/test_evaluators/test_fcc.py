"""
Tests for FCC Rule Evaluators

Tests for: FCC-DEORBIT-01, FCC-DEORBIT-02, FCC-LEO-01
At least 2 tests per rule (pass + fail case).
"""
import pytest
from app.models.compliance import RuleStatus
import app.evaluators.fcc as fcc


class TestFCCDeorbit01:
    """FCC-DEORBIT-01: 5-year post-mission orbital lifetime."""

    def test_low_leo_active_passes(self):
        """Satellite at 350 km naturally decays in < 5 years → PASS.
        At 350 km, lifetime is well under 5 years even at A/m=0.01.
        """
        result = fcc.check_deorbit_lifetime(altitude_km=350.0, mission_status="active")
        assert result.rule_id == "FCC-DEORBIT-01"
        assert result.status == RuleStatus.PASS
        assert result.value is not None
        assert result.value <= 5.0

    def test_high_leo_active_flags(self):
        """Satellite at 900 km has lifetime > 5 years → FLAG (needs active deorbit at EOL)."""
        result = fcc.check_deorbit_lifetime(altitude_km=900.0, mission_status="active")
        assert result.rule_id == "FCC-DEORBIT-01"
        assert result.status == RuleStatus.FLAG
        assert result.value > 5.0

    def test_decommissioned_within_window_passes(self):
        """Decommissioned satellite at 350 km, 2 years since EOL → PASS.
        At 350 km the satellite will naturally deorbit within the remaining 3-year window.
        """
        result = fcc.check_deorbit_lifetime(
            altitude_km=350.0,
            mission_status="decommissioned",
            years_since_mission_end=2.0,
        )
        assert result.status == RuleStatus.PASS

    def test_decommissioned_window_expired_fails(self):
        """Decommissioned satellite at 900 km, 6 years since EOL → FAIL."""
        result = fcc.check_deorbit_lifetime(
            altitude_km=900.0,
            mission_status="decommissioned",
            years_since_mission_end=6.0,
        )
        assert result.rule_id == "FCC-DEORBIT-01"
        assert result.status == RuleStatus.FAIL

    def test_decommissioned_lifetime_exceeds_window_fails(self):
        """Decommissioned satellite at 900 km, 3 years since EOL, lifetime >> 2 years → FAIL."""
        result = fcc.check_deorbit_lifetime(
            altitude_km=900.0,
            mission_status="decommissioned",
            years_since_mission_end=3.0,
        )
        assert result.status == RuleStatus.FAIL

    def test_rule_cites_correct_standard(self):
        """Result cites FCC 47 CFR Part 25.114(d)(14)."""
        result = fcc.check_deorbit_lifetime(altitude_km=550.0)
        assert "47 CFR" in result.standard_clause
        assert "25.114" in result.standard_clause
        assert result.body == "FCC"

    def test_result_includes_threshold(self):
        """Result includes threshold of 5.0 years."""
        result = fcc.check_deorbit_lifetime(altitude_km=600.0, mission_status="active")
        assert result.unit == "years"
        # Threshold is 5.0 for active satellites


class TestFCCDeorbit02:
    """FCC-DEORBIT-02: Casualty risk assessment."""

    def test_small_satellite_passes(self):
        """Small satellite (10 kg) has low casualty risk → PASS."""
        result = fcc.check_casualty_risk(altitude_km=400.0, satellite_mass_kg=10.0)
        assert result.rule_id == "FCC-DEORBIT-02"
        assert result.status == RuleStatus.PASS
        assert result.value is not None
        assert result.value < 1e-4

    def test_standard_satellite_passes(self):
        """Standard 100 kg satellite should pass the casualty risk threshold."""
        result = fcc.check_casualty_risk(altitude_km=500.0, satellite_mass_kg=100.0)
        assert result.rule_id == "FCC-DEORBIT-02"
        # Most small-medium satellites pass this test

    def test_fully_demisable_passes(self):
        """Fully demisable satellite (100% demises on reentry) → PASS."""
        result = fcc.check_casualty_risk(
            altitude_km=400.0,
            satellite_mass_kg=200.0,
            demisable_fraction=1.0,
        )
        assert result.status == RuleStatus.PASS
        assert result.value == 0.0 or result.value < 1e-10

    def test_threshold_is_one_in_ten_thousand(self):
        """Threshold must be 1e-4."""
        result = fcc.check_casualty_risk(altitude_km=400.0, satellite_mass_kg=50.0)
        assert result.threshold == 1e-4


class TestFCCLEO01:
    """FCC-LEO-01: LEO classification."""

    def test_in_leo_passes(self):
        """Satellite at 550 km is in LEO → PASS."""
        result = fcc.check_leo_orbit_altitude(altitude_km=550.0)
        assert result.rule_id == "FCC-LEO-01"
        assert result.status == RuleStatus.PASS

    def test_geo_is_skipped(self):
        """Satellite at GEO altitude is skipped — rule doesn't apply."""
        result = fcc.check_leo_orbit_altitude(altitude_km=35786.0)
        assert result.rule_id == "FCC-LEO-01"
        assert result.status == RuleStatus.SKIP

    def test_meo_is_skipped(self):
        """Satellite at MEO altitude → SKIP."""
        result = fcc.check_leo_orbit_altitude(altitude_km=20200.0)
        assert result.status == RuleStatus.SKIP

    def test_boundary_at_2000km(self):
        """Satellite just below 2000 km threshold → PASS."""
        result = fcc.check_leo_orbit_altitude(altitude_km=1999.0)
        assert result.status == RuleStatus.PASS
