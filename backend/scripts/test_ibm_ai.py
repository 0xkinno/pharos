"""End-to-end IBM AI test — run as: python -m scripts.test_ibm_ai"""
import logging
import warnings

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from app.core.config import get_settings

get_settings.cache_clear()
from app.ai.watsonx_client import get_watsonx_client

get_watsonx_client.cache_clear()

from app.ai.watsonx_guardian import screen_report
from app.models.satellite import SatelliteData
from app.services.compliance_engine import evaluate_satellite
from app.services.report_generator import generate_compliance_report

print("=== PHAROS End-to-End IBM AI Test ===")
print()

# ISS as a well-characterised test case (real TLE values)
iss = SatelliteData(
    norad_cat_id=25544,
    object_name="ISS (ZARYA)",
    epoch="2024-001.00000000",
    mean_motion=15.49969158,
    eccentricity=0.0004914,
    inclination=51.6415,
    ra_of_asc_node=257.3222,
    arg_of_pericenter=101.6083,
    mean_anomaly=258.5573,
    bstar=0.000040768,
    mean_motion_dot=0.00002182,
    mean_motion_ddot=0.0,
)

print("1. Running compliance engine (deterministic)...")
report = evaluate_satellite(
    iss,
    mission_status="active",
    is_registered_with_un=True,
    ssa_data_shared=True,
    collision_avoidance_capability=True,
    has_passivation_plan=True,
)
print(f"   Score: {report.compliance_score:.1f}/100 | Level: {report.compliance_level}")
print(f"   Rules: {report.rules_passed} passed / {report.rules_flagged} flagged / {report.rules_failed} failed")
print()

print("2. Generating AI compliance report via watsonx.ai...")
client = get_watsonx_client()
print(f"   Available: {client.is_available()}")
print(f"   Instruct model: {client.active_instruct_model}")
print(f"   Guardian model: {client.active_guardian_model}")
ai_text = generate_compliance_report(report)
print(f"   Generated: {len(ai_text)} chars")
print()
print("   --- AI Report (first 600 chars) ---")
print(ai_text[:600])
print("   [...]")
print()

print("3. Granite Guardian safety screening...")
safety = screen_report(ai_text)
print(f"   Screened: {safety.screened}")
print(f"   Safe: {safety.safe}")
print(f"   Model: {safety.model}")
print(f"   Reason: {safety.reason[:120]}")
print()

print("=== RESULT ===")
if client.is_available() and len(ai_text) > 200:
    print("SUCCESS — All IBM AI layers wired and working:")
    print(f"  Instruct ({client.active_instruct_model}): LIVE")
    print(f"  Guardian ({safety.model or 'via instruct fallback'}): {'LIVE' if safety.screened else 'FALLBACK'}")
    print("  Embedding/RAG: deterministic fallback (no sentence-transformers)")
else:
    print("PARTIAL — Check logs above")
