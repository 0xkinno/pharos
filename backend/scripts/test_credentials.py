"""
Test all credential combinations to find what works with Granite.
python -m scripts.test_credentials
"""
import warnings
warnings.filterwarnings("ignore")

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai import APIClient

# All credential combinations to test
COMBOS = [
    # (label, url, api_key, project_id)
    (
        "EU-DE + NEW KEY + EU-DE project",
        "https://eu-de.ml.cloud.ibm.com",
        "cKmtteTfWH7VyjGsI2GMPt-zPz9TcmO9zcuL4Ph4_lAP",
        "4f974d75-8efe-41bc-a2b3-12a54c2cb255",
    ),
    (
        "US-SOUTH + NEW KEY + US-SOUTH project",
        "https://us-south.ml.cloud.ibm.com",
        "cKmtteTfWH7VyjGsI2GMPt-zPz9TcmO9zcuL4Ph4_lAP",
        "0b9d8b8c-5316-4322-b488-6d30ea8d3300",
    ),
    (
        "US-SOUTH + OLD KEY + EU-DE project",
        "https://us-south.ml.cloud.ibm.com",
        "XPSa8m5ANGlCwzZ1-3ITsmczQrIMGJ6HMSfcDwPYe26O",
        "4f974d75-8efe-41bc-a2b3-12a54c2cb255",
    ),
    (
        "EU-DE + OLD KEY + EU-DE project",
        "https://eu-de.ml.cloud.ibm.com",
        "XPSa8m5ANGlCwzZ1-3ITsmczQrIMGJ6HMSfcDwPYe26O",
        "4f974d75-8efe-41bc-a2b3-12a54c2cb255",
    ),
    (
        "US-SOUTH + NEW KEY + EU-DE project",
        "https://us-south.ml.cloud.ibm.com",
        "cKmtteTfWH7VyjGsI2GMPt-zPz9TcmO9zcuL4Ph4_lAP",
        "4f974d75-8efe-41bc-a2b3-12a54c2cb255",
    ),
]

GRANITE_CANDIDATES = [
    "ibm/granite-3-8b-instruct",
    "ibm/granite-3-1-8b-instruct",
    "ibm/granite-3-2-8b-instruct",
    "ibm/granite-13b-instruct-v2",
    "ibm/granite-3b-code-instruct",
    "meta-llama/llama-3-3-70b-instruct",  # known working in EU-DE
]

print("=" * 70)
print("WATSONX.AI CREDENTIAL + GRANITE MODEL PROBE")
print("=" * 70)

best_combo = None
best_models = []

for label, url, key, pid in COMBOS:
    print(f"\n--- {label} ---")
    try:
        creds = Credentials(url=url, api_key=key)
        client = APIClient(credentials=creds, project_id=pid)
        specs = client.foundation_models.get_model_specs()
        resources = specs.get("resources", [])
        all_ids = [r.get("model_id", "") for r in resources]

        granite = [m for m in all_ids if "granite" in m.lower() and
                   any(x in m.lower() for x in ["instruct", "chat"])]
        print(f"  Connected OK — {len(resources)} models available")
        print(f"  Granite instruct models: {granite}")

        if granite:
            best_combo = (url, key, pid, label)
            best_models = granite
            print(f"  *** GRANITE AVAILABLE — USE THIS COMBO ***")
            break
        else:
            print(f"  No Granite instruct models — checking all available:")
            print(f"  {sorted(all_ids)[:10]}")

    except Exception as exc:
        err = str(exc)[:120]
        print(f"  FAILED: {err}")

print()
print("=" * 70)
if best_combo:
    url, key, pid, label = best_combo
    print(f"WINNER: {label}")
    print(f"URL:     {url}")
    print(f"PROJECT: {pid}")
    print(f"GRANITE: {best_models}")
else:
    print("NO WORKING COMBINATION FOUND — using EU-DE with Llama fallback")
print("=" * 70)
