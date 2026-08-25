"""
Tests for ISO 24113 Rule Evaluators

Tests for: ISO-ORBIT-01, ISO-ORBIT-02, ISO-DEBRIS-01
"""
import app.evaluators.iso24113 as iso
from app.models.compliance import RuleStatus


class TestISOOrbit01:
    """ISO-ORBIT-01: LEO Protected Region A."""

    def test_low_leo_passes(self):
        """Satellite at 350 km → PASS (short lifetime < 25 years)."""
        result = iso.check_leo_protected_region(altitude_km=350.0)
        assert result.rule_id == "ISO-ORBIT-01"
        assert result.status == RuleStatus.PASS

    def test_high_leo_fails(self):
        """Satellite at 1000 km has lifetime > 25 years → FAIL."""
        result = iso.check_leo_protected_region(altitude_km=1000.0)
        assert result.rule_id == "ISO-ORBIT-01"
        assert result.status == RuleStatus.FAIL

    def test_geo_is_skipped(self):
        """GEO satellite → SKIP (not in Protected Region A)."""
        result = iso.check_leo_protected_region(altitude_km=35786.0)
        assert result.status == RuleStatus.SKIP

    def test_above_2000_is_skipped(self):
        """Satellite at 2100 km → SKIP."""
        result = iso.check_leo_protected_region(altitude_km=2100.0)
        assert result.status == RuleStatus.SKIP

    def test_cites_iso_section_622(self):
        """Cites ISO 24113:2019 Section 6.2.2."""
        result = iso.check_leo_protected_region(altitude_km=500.0)
        assert "ISO 24113" in result.standard_clause
        assert "6.2.2" in result.standard_clause


class TestISOOrbit02:
    """ISO-ORBIT-02: GEO Protected Region B."""

    def test_leo_is_skipped(self):
        """LEO satellite → SKIP (not in Protected Region B)."""
        result = iso.check_geo_disposal(altitude_km=550.0)
        assert result.rule_id == "ISO-ORBIT-02"
        assert result.status == RuleStatus.SKIP

    def test_geo_active_is_flagged(self):
        """Active GEO satellite → FLAG (needs disposal at EOL)."""
        result = iso.check_geo_disposal(altitude_km=35786.0, mission_status="active")
        assert result.rule_id == "ISO-ORBIT-02"
        assert result.status == RuleStatus.FLAG

    def test_geo_correct_disposal_passes(self):
        """GEO satellite disposed to 36400 km (above graveyard minimum) → PASS."""
        result = iso.check_geo_disposal(
            altitude_km=35786.0,
            mission_status="decommissioned",
            final_altitude_km=36400.0,
        )
        assert result.status == RuleStatus.PASS

    def test_geo_insufficient_disposal_fails(self):
        """GEO satellite disposed to 35900 km (below 36186 km minimum) → FAIL."""
        result = iso.check_geo_disposal(
            altitude_km=35786.0,
            mission_status="decommissioned",
            final_altitude_km=35900.0,
        )
        assert result.status == RuleStatus.FAIL

    def test_geo_no_disposal_data_flags(self):
        """Decommissioned GEO with no final altitude data → FLAG."""
        result = iso.check_geo_disposal(
            altitude_km=35800.0,
            mission_status="decommissioned",
            final_altitude_km=None,
        )
        assert result.status == RuleStatus.FLAG

    def test_cites_iso_section_623(self):
        """Cites ISO 24113:2019 Section 6.2.3."""
        result = iso.check_geo_disposal(altitude_km=35786.0)
        assert "6.2.3" in result.standard_clause


class TestISODebris01:
    """ISO-DEBRIS-01: No intentional debris release."""

    def test_zero_debris_passes(self):
        """No debris released → PASS."""
        result = iso.check_debris_generation_limit(fragments_released=0)
        assert result.rule_id == "ISO-DEBRIS-01"
        assert result.status == RuleStatus.PASS

    def test_any_debris_fails(self):
        """Any intentional debris release → FAIL."""
        result = iso.check_debris_generation_limit(fragments_released=1)
        assert result.status == RuleStatus.FAIL

    def test_multiple_fragments_fails(self):
        """Multiple fragments → FAIL."""
        result = iso.check_debris_generation_limit(fragments_released=10)
        assert result.status == RuleStatus.FAIL
        assert result.value == 10.0

    def test_cites_iso_section_63(self):
        """Cites ISO 24113:2019 Section 6.3."""
        result = iso.check_debris_generation_limit(fragments_released=0)
        assert "6.3" in result.standard_clause
