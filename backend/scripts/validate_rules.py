"""
Validate All Rules Against Test Fixtures

Runs every rule evaluator against known inputs and verifies the expected
output. This validates the rule engine is working correctly before
building the embedding index or running the live demo.

Usage:
    cd backend
    python scripts/validate_rules.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def run_validation() -> bool:
    """Run all rule evaluator validation tests. Returns True if all pass."""
    import app.evaluators.esa_zero_debris as esa
    from app.evaluators import copuos, fcc, iadc, iso24113
    from app.models.compliance import RuleStatus

    tests = []
    failures = []

    def check(test_name: str, result, expected_status: RuleStatus):
        tests.append(test_name)
        if result.status == expected_status:
            logger.info("  PASS: %s → %s", test_name, result.status.value)
        else:
            failures.append(f"{test_name}: expected {expected_status.value}, got {result.status.value}: {result.message}")
            logger.error("  FAIL: %s → expected %s, got %s", test_name, expected_status.value, result.status.value)

    logger.info("--- FCC Rules ---")
    # FCC-DEORBIT-01: Low LEO → PASS
    check("FCC-DEORBIT-01 @ 450km active", fcc.check_deorbit_lifetime(450.0), RuleStatus.PASS)
    # FCC-DEORBIT-01: High LEO → FLAG
    check("FCC-DEORBIT-01 @ 900km active (needs active deorbit)", fcc.check_deorbit_lifetime(900.0), RuleStatus.FLAG)
    # FCC-DEORBIT-01: High LEO, expired window → FAIL
    check("FCC-DEORBIT-01 @ 900km EOL expired", fcc.check_deorbit_lifetime(900.0, mission_status="decommissioned", years_since_mission_end=6.0), RuleStatus.FAIL)
    # FCC-DEORBIT-02: Small satellite → PASS
    check("FCC-DEORBIT-02 @ 10kg satellite", fcc.check_casualty_risk(400.0, satellite_mass_kg=10.0), RuleStatus.PASS)
    # FCC-LEO-01: In LEO → PASS
    check("FCC-LEO-01 @ 550km (LEO)", fcc.check_leo_orbit_altitude(550.0), RuleStatus.PASS)
    # FCC-LEO-01: GEO → SKIP
    check("FCC-LEO-01 @ 35786km (GEO)", fcc.check_leo_orbit_altitude(35786.0), RuleStatus.SKIP)

    logger.info("--- IADC Rules ---")
    # IADC-LIFE-01: Low orbit → PASS
    check("IADC-LIFE-01 @ 450km", iadc.check_orbital_lifetime(450.0), RuleStatus.PASS)
    # IADC-LIFE-01: High orbit → FAIL
    check("IADC-LIFE-01 @ 1000km", iadc.check_orbital_lifetime(1000.0), RuleStatus.FAIL)
    # IADC-PASS-01: No plan → FAIL
    check("IADC-PASS-01 no plan", iadc.check_passivation(has_passivation_plan=False, pressure_vessels_vented=False, batteries_discharged=False), RuleStatus.FAIL)
    # IADC-PASS-01: Full passivation → PASS
    check("IADC-PASS-01 full passivation", iadc.check_passivation(has_passivation_plan=True, pressure_vessels_vented=True, batteries_discharged=True), RuleStatus.PASS)
    # IADC-COLL-01: No data → FLAG
    check("IADC-COLL-01 no data", iadc.check_disposal_collision_probability(0.0), RuleStatus.FLAG)
    # IADC-COLL-01: Low probability → PASS
    check("IADC-COLL-01 p=0.0001", iadc.check_disposal_collision_probability(0.0001), RuleStatus.PASS)
    # IADC-COLL-01: High probability → FAIL
    check("IADC-COLL-01 p=0.002", iadc.check_disposal_collision_probability(0.002), RuleStatus.FAIL)

    logger.info("--- ISO 24113 Rules ---")
    # ISO-ORBIT-01: Low orbit → PASS
    check("ISO-ORBIT-01 @ 450km", iso24113.check_leo_protected_region(450.0), RuleStatus.PASS)
    # ISO-ORBIT-01: High LEO → FAIL
    check("ISO-ORBIT-01 @ 1000km (long lifetime)", iso24113.check_leo_protected_region(1000.0), RuleStatus.FAIL)
    # ISO-ORBIT-01: GEO → SKIP
    check("ISO-ORBIT-01 @ 35786km (not LEO)", iso24113.check_leo_protected_region(35786.0), RuleStatus.SKIP)
    # ISO-ORBIT-02: Not in GEO belt → SKIP
    check("ISO-ORBIT-02 @ 550km (not GEO)", iso24113.check_geo_disposal(550.0), RuleStatus.SKIP)
    # ISO-ORBIT-02: GEO active → FLAG
    check("ISO-ORBIT-02 @ 35786km active", iso24113.check_geo_disposal(35786.0, mission_status="active"), RuleStatus.FLAG)
    # ISO-ORBIT-02: GEO disposed → PASS
    check("ISO-ORBIT-02 @ 35786km disposed to 36400km", iso24113.check_geo_disposal(35786.0, mission_status="decommissioned", final_altitude_km=36400.0), RuleStatus.PASS)
    # ISO-ORBIT-02: GEO disposed but insufficient → FAIL
    check("ISO-ORBIT-02 insufficient graveyard", iso24113.check_geo_disposal(35786.0, mission_status="decommissioned", final_altitude_km=35900.0), RuleStatus.FAIL)
    # ISO-DEBRIS-01: No debris → PASS
    check("ISO-DEBRIS-01 no release", iso24113.check_debris_generation_limit(0), RuleStatus.PASS)
    # ISO-DEBRIS-01: Debris released → FAIL
    check("ISO-DEBRIS-01 5 fragments", iso24113.check_debris_generation_limit(5), RuleStatus.FAIL)

    logger.info("--- ESA Zero Debris Rules ---")
    # ESA-ZD-01: No debris → PASS
    check("ESA-ZD-01 no debris", esa.check_no_intentional_release(False, 0), RuleStatus.PASS)
    # ESA-ZD-01: Debris released → FAIL
    check("ESA-ZD-01 debris released", esa.check_no_intentional_release(True, 2), RuleStatus.FAIL)
    # ESA-ZD-02: High probability → PASS
    check("ESA-ZD-02 p=0.95", esa.check_disposal_probability(0.95), RuleStatus.PASS)
    # ESA-ZD-02: Low probability → FAIL
    check("ESA-ZD-02 p=0.70", esa.check_disposal_probability(0.70), RuleStatus.FAIL)
    # ESA-ZD-03: Full compliance → PASS
    check("ESA-ZD-03 full compliance", esa.check_debris_free_operations(True, True, True), RuleStatus.PASS)
    # ESA-ZD-03: No capability → FAIL
    check("ESA-ZD-03 no CA capability", esa.check_debris_free_operations(False, False, False), RuleStatus.FAIL)

    logger.info("--- COPUOS Rules ---")
    # COPUOS-REG-01: COSPAR ID → PASS
    check("COPUOS-REG-01 with COSPAR", copuos.check_registration(cospar_id="2024-001A"), RuleStatus.PASS)
    # COPUOS-REG-01: No registration → FAIL
    check("COPUOS-REG-01 no registration", copuos.check_registration(is_registered_with_un=False, national_registry_registered=False, cospar_id=None), RuleStatus.FAIL)
    # COPUOS-COORD-01: Full sharing → PASS
    check("COPUOS-COORD-01 all sharing", copuos.check_data_sharing(True, True, True), RuleStatus.PASS)
    # COPUOS-COORD-01: No sharing → FAIL
    check("COPUOS-COORD-01 no sharing", copuos.check_data_sharing(False, False, False), RuleStatus.FAIL)
    # COPUOS-NOTIF-01: No maneuvers → PASS
    check("COPUOS-NOTIF-01 no maneuvers", copuos.check_maneuver_notification(False), RuleStatus.PASS)
    # COPUOS-NOTIF-01: Maneuver, 48h notice → PASS
    check("COPUOS-NOTIF-01 48h notice", copuos.check_maneuver_notification(True, True, 48.0), RuleStatus.PASS)

    logger.info("\n--- Results ---")
    logger.info("Total tests: %d", len(tests))
    logger.info("Passed: %d", len(tests) - len(failures))
    logger.info("Failed: %d", len(failures))

    if failures:
        logger.error("\nFailed tests:")
        for f in failures:
            logger.error("  %s", f)
        return False

    logger.info("\nAll validation tests passed! ✓")
    return True


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
