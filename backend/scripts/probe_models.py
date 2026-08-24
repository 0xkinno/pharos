"""
Probe US-South watsonx.ai for available Granite models.
python -m scripts.probe_models
"""
import warnings
warnings.filterwarnings("ignore")
import logging
logging.basicConfig(level=logging.WARNING)

from app.core.config import get_settings
get_settings.cache_clear()

s = get_settings()
print(f"URL:        {s.watsonx_url}")
print(f"Project:    {s.watsonx_project_id}")
print(f"Key prefix: {s.watsonx_api_key[:8] if s.watsonx_api_key else 'MISSING'}...")
print()

try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference

    creds = Credentials(url=s.watsonx_url, api_key=s.watsonx_api_key)

    # Probe a model that we KNOW works to get the full catalog via the error message
    # or use the client directly
    try:
        from ibm_watsonx_ai import APIClient
        client = APIClient(credentials=creds, project_id=s.watsonx_project_id)
        specs = client.foundation_models.get_model_specs()
        resources = specs.get("resources", [])
        print(f"Total models in catalog: {len(resources)}")
        print()

        granite_models = []
        instruct_models = []
        all_models = []

        for r in resources:
            mid = r.get("model_id", "")
            label = r.get("label", "")
            all_models.append(mid)
            if "granite" in mid.lower():
                granite_models.append(mid)
            if any(x in mid.lower() for x in ["instruct", "chat"]):
                instruct_models.append(mid)

        print("=== GRANITE MODELS ===")
        for m in sorted(granite_models):
            print(f"  {m}")

        print()
        print("=== ALL INSTRUCT/CHAT MODELS ===")
        for m in sorted(instruct_models):
            print(f"  {m}")

        print()
        print("=== FULL MODEL LIST ===")
        for m in sorted(all_models):
            print(f"  {m}")

    except Exception as exc:
        print(f"APIClient probe failed: {exc}")
        print("Falling back to probe by model ID...")

        # Priority-ordered Granite instruct candidates
        candidates = [
            "ibm/granite-3-8b-instruct",
            "ibm/granite-3-1-8b-instruct",
            "ibm/granite-3-2-8b-instruct",
            "ibm/granite-3b-code-instruct",
            "ibm/granite-13b-instruct-v2",
            "ibm/granite-20b-instruct-v2",
            "ibm/granite-7b-instruct",
            "ibm/granite-8b-code-instruct",
        ]
        print()
        for mid in candidates:
            try:
                m = ModelInference(
                    model_id=mid,
                    credentials=creds,
                    project_id=s.watsonx_project_id,
                    params={"max_new_tokens": 5},
                )
                print(f"  AVAILABLE: {mid}")
            except Exception as e:
                print(f"  NOT FOUND: {mid} — {str(e)[:80]}")

except ImportError as e:
    print(f"SDK not installed: {e}")
