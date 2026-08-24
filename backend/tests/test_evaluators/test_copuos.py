"""
Tests for UN COPUOS Rule Evaluators

Tests for: COPUOS-REG-01, COPUOS-COORD-01, COPUOS-NOTIF-01
"""
import pytest
from app.models.compliance import RuleStatus
import app.evaluators.copuos as copuos


class TestCOPUOSReg01:
    """COPUOS-REG-01: Registration Convention compliance."""

    def test_with_cospar_id_passes(self):
        """Satellite with COSPAR ID → PASS."""
        result = copuos.check_registration(cospar_id="2024-001A")
        assert result.rule_id == "COPUOS-REG-01"
        assert result.status == RuleStatus.PASS
        assert "2024-001A" in result.message

    def test_un_registered_passes(self):
        """UN registration confirmed → PASS."""
        result = copuos.check_registration(is_registered_with_un=True)
        assert result.status == RuleStatus.PASS

    def test_national_only_flags(self):
        """National registry only, UN confirmation unknown → FLAG."""
        result = copuos.check_registration(
            is_registered_with_un=False,
            national_registry_registered=True,
            cospar_id=None,
        )
        assert result.rule_id == "COPUOS-REG-01"
        assert result.status == RuleStatus.FLAG

    def test_no_registration_fails(self):
        """No registration at all → FAIL."""
        result = copuos.check_registration(
            is_registered_with_un=False,
            national_registry_registered=False,
            cospar_id=None,
        )
        assert result.rule_id == "COPUOS-REG-01"
        assert result.status == RuleStatus.FAIL

    def test_cites_copuos_guideline_b1(self):
        """Must cite COPUOS LTS Guideline B.1."""
        result = copuos.check_registration(cospar_id="2024-001A")
        assert "B.1" in result.standard_clause
        assert result.body == "COPUOS"


class TestCOPUOSCoord01:
    """COPUOS-COORD-01: Orbital data sharing and conjunction assessment."""

    def test_all_sharing_passes(self):
        """All data sharing criteria met → PASS."""
        result = copuos.check_data_sharing(
            orbital_data_shared_publicly=True,
            ssa_coordination_active=True,
            shares_with_spacefence=True,
        )
        assert result.rule_id == "COPUOS-COORD-01"
        assert result.status == RuleStatus.PASS

    def test_partial_sharing_flags(self):
        """One criterion met → FLAG."""
        result = copuos.check_data_sharing(
            orbital_data_shared_publicly=True,
            ssa_coordination_active=False,
            shares_with_spacefence=False,
        )
        assert result.status == RuleStatus.FLAG

    def test_no_sharing_fails(self):
        """No data sharing → FAIL."""
        result = copuos.check_data_sharing(
            orbital_data_shared_publicly=False,
            ssa_coordination_active=False,
            shares_with_spacefence=False,
        )
        assert result.rule_id == "COPUOS-COORD-01"
        assert result.status == RuleStatus.FAIL

    def test_cites_copuos_guideline_b2(self):
        """Must cite COPUOS LTS Guideline B.2."""
        result = copuos.check_data_sharing(True, True, True)
        assert "B.2" in result.standard_clause


class TestCOPUOSNotif01:
    """COPUOS-NOTIF-01: Maneuver notification."""

    def test_no_maneuvers_passes(self):
        """No large maneuvers planned → PASS."""
        result = copuos.check_maneuver_notification(large_maneuvers_planned=False)
        assert result.rule_id == "COPUOS-NOTIF-01"
        assert result.status == RuleStatus.PASS

    def test_maneuver_with_24h_notice_passes(self):
        """Maneuver with 24+ hours notice → PASS."""
        result = copuos.check_maneuver_notification(
            large_maneuvers_planned=True,
            notification_provided=True,
            advance_notice_hours=48.0,
        )
        assert result.status == RuleStatus.PASS

    def test_maneuver_with_short_notice_flags(self):
        """Maneuver with < 24 hours notice → FLAG."""
        result = copuos.check_maneuver_notification(
            large_maneuvers_planned=True,
            notification_provided=True,
            advance_notice_hours=12.0,
        )
        assert result.status == RuleStatus.FLAG

    def test_maneuver_no_notification_flags(self):
        """Maneuver planned but no notification → FLAG."""
        result = copuos.check_maneuver_notification(
            large_maneuvers_planned=True,
            notification_provided=False,
        )
        assert result.status == RuleStatus.FLAG

    def test_cites_copuos_guideline_c1(self):
        """Must cite COPUOS LTS Guideline C.1."""
        result = copuos.check_maneuver_notification(False)
        assert "C.1" in result.standard_clause
