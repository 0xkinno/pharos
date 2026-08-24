"""
Test new US-South project ID for Granite model access.
python -m scripts.test_us_south
"""
import warnings
warnings.filterwarnings("ignore")

from ibm_watsonx_ai import Credentials, APIClient

COMBOS = [
    (
        "US-SOUTH + NEW KEY + NEW PROJECT",
        "https://us-south.ml.cloud.ibm.com",
        "cKmtteTfWH7VyjGsI2GMPt-zPz9TcmO9zcuL4Ph4_lAP",
        "2399335c-fbe1-4445-9ec2-f037a8dca1a2",
    ),
    (
        "US-SOUTH + OLD KEY + NEW PROJECT",
        "https://us-south.ml.cloud.ibm.com",
        "XPSa8m5ANGlCwzZ1-3ITsmczQrIMGJ6HMSfcDwPYe26O",
        "2399335c-fbe1-4445-9ec2-f037a8dca1a2",
    ),
]

GRANITE_INSTRUCT = [
    "ibm/granite-3-8b-instruct",
    "ibm/granite-3-1-8b-instruct",
    "ibm/granite-3-2-8b-instruct",
    "ibm/granite-13b-instruct-v2",
    "ibm/granite-3b-code-instruct",
]

print("=" * 60)
print("US-SOUTH GRANITE PROBE — new project 2399335c")
print("=" * 60)

winning_combo = None

for label, url, key, pid in COMBOS:
    print(f"\n--- {label} ---")
    try:
        creds = Credentials(url=url, api_key=key)
        client = APIClient(credentials=creds, project_id=pid)
        specs = client.foundation_models.get_model_specs()
        resources = specs.get("resources", [])
        all_ids = sorted(r.get("model_id", "") for r in resources)

        granite_instruct = [m for m in all_ids if "granite" in m.lower() and
                            any(x in m.lower() for x in ["instruct", "chat"])]
        granite_all = [m for m in all_ids if "granite" in m.lower()]

        print(f"  Connected OK — {len(resources)} models")
        print(f"  All Granite models: {granite_all}")
        print(f"  Granite INSTRUCT:   {granite_instruct}")

        if granite_instruct:
            print(f"\n  *** GRANITE INSTRUCT AVAILABLE: {granite_instruct[0]} ***")
            winning_combo = (url, key, pid, granite_instruct[0], label)
            break
        else:
            print(f"  All models: {all_ids}")

    except Exception as exc:
        print(f"  FAILED: {str(exc)[:150]}")

print()
print("=" * 60)
if winning_combo:
    url, key, pid, model, label = winning_combo
    print(f"WINNER: {label}")
    print(f"  URL:     {url}")
    print(f"  PROJECT: {pid}")
    print(f"  GRANITE: {model}")
else:
    print("No Granite instruct found on US-South with new project")
print("=" * 60)
