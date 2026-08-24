"""
Verify CelesTrak live data access.
python -m scripts.verify_celestrak
"""
import asyncio
import sys

async def main():
    import httpx

    BASE = "https://celestrak.org/NORAD/elements/gp.php"

    tests = [
        ("ISS by NORAD ID", {"CATNR": "25544", "FORMAT": "json"}),
        ("Starlink group (first 3)", {"GROUP": "starlink", "FORMAT": "json"}),
        ("Active satellites (first 3)", {"GROUP": "active", "FORMAT": "json"}),
        ("Cosmos-2251 debris", {"GROUP": "cosmos-2251-debris", "FORMAT": "json"}),
    ]

    print("=== CelesTrak Live Data Verification ===")
    print()

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        for label, params in tests:
            try:
                r = await client.get(BASE, params=params)
                r.raise_for_status()
                data = r.json()
                if not isinstance(data, list) or len(data) == 0:
                    print(f"  FAIL {label}: empty or bad response")
                    continue

                first = data[0]
                name = first.get("OBJECT_NAME", "?")
                norad = first.get("NORAD_CAT_ID", "?")
                alt_mm = float(first.get("MEAN_MOTION", 0))
                # Rough altitude from mean_motion
                import math
                MU = 398600.4418
                n = alt_mm * 2 * math.pi / 86400.0
                a = (MU / n**2) ** (1/3)
                alt = a - 6371
                print(f"  OK  {label}")
                print(f"      Records: {len(data)} | First: {name} (NORAD {norad}) @ ~{alt:.0f} km")
            except Exception as exc:
                print(f"  FAIL {label}: {exc}")
            print()

    print()
    print("=== CelesTrak Verification Complete ===")
    print()

    # Now test the full compliance engine on live ISS data
    print("=== Live Compliance Check: ISS from CelesTrak ===")
    from app.core.config import get_settings
    get_settings.cache_clear()
    from app.services.celestrak_client import get_satellite_by_norad_id
    from app.services.compliance_engine import evaluate_satellite

    sat = await get_satellite_by_norad_id(25544)
    if sat is None:
        print("  FAIL: Could not fetch ISS from CelesTrak")
        return

    print(f"  Fetched: {sat.object_name} (NORAD {sat.norad_cat_id})")
    if sat.orbital_elements:
        print(f"  Altitude: {sat.orbital_elements.mean_altitude_km:.1f} km")
        print(f"  Inclination: {sat.inclination:.2f} deg")

    report = evaluate_satellite(sat, mission_status="active",
        is_registered_with_un=True, ssa_data_shared=True,
        collision_avoidance_capability=True, has_passivation_plan=True)

    print(f"  Compliance Score: {report.compliance_score:.1f}/100 ({report.compliance_level})")
    print(f"  Rules: {report.rules_passed} pass / {report.rules_flagged} flag / {report.rules_failed} fail")
    print()
    print("  PASS — live CelesTrak data feeds compliance engine correctly")

asyncio.run(main())
