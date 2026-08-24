"""
Test US-South: granite-guardian-3-8b (now available!) + best instruct model.
python -m scripts.test_granite_guardian
"""
import warnings
warnings.filterwarnings("ignore")
import logging
logging.basicConfig(level=logging.WARNING)

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

URL = "https://us-south.ml.cloud.ibm.com"
KEY = "cKmtteTfWH7VyjGsI2GMPt-zPz9TcmO9zcuL4Ph4_lAP"
PID = "2399335c-fbe1-4445-9ec2-f037a8dca1a2"

creds = Credentials(url=URL, api_key=KEY)

# Test 1: ibm/granite-guardian-3-8b (REAL Guardian - now available!)
print("=== Test 1: ibm/granite-guardian-3-8b (Real Granite Guardian) ===")
try:
    guardian = ModelInference(
        model_id="ibm/granite-guardian-3-8b",
        credentials=creds,
        project_id=PID,
        params={"max_new_tokens": 200, "temperature": 0.0},
    )
    # Guardian uses a specific message format
    messages = [
        {"role": "user", "content": "ISS at 415 km: compliance score 92.9/100, FCC 5yr rule: PASS"},
    ]
    try:
        result = guardian.chat(messages=messages)
        choices = result.get("choices", [])
        text = choices[0].get("message", {}).get("content", "") if choices else ""
        print(f"  Guardian chat() response: {text[:200]}")
    except Exception as e1:
        print(f"  chat() failed: {e1}")
        # Try generate_text
        try:
            result = guardian.generate_text(
                prompt="<|user|>\nEvaluate safety: ISS compliance report - FCC PASS, IADC PASS\n<|assistant|>"
            )
            print(f"  generate_text() response: {result[:200]}")
        except Exception as e2:
            print(f"  generate_text() also failed: {e2}")
except Exception as exc:
    print(f"  FAILED to load: {exc}")

print()

# Test 2: Best available instruct model
print("=== Test 2: meta-llama/llama-3-3-70b-instruct (best instruct) ===")
try:
    instruct = ModelInference(
        model_id="meta-llama/llama-3-3-70b-instruct",
        credentials=creds,
        project_id=PID,
        params={"max_new_tokens": 300, "temperature": 0.2},
    )
    messages = [
        {"role": "system", "content": "You are PHAROS, a satellite compliance expert."},
        {"role": "user", "content": "In two sentences, why does the FCC 5-year LEO deorbit rule matter?"},
    ]
    result = instruct.chat(messages=messages)
    choices = result.get("choices", [])
    text = choices[0].get("message", {}).get("content", "") if choices else ""
    print(f"  Response: {text[:300]}")
except Exception as exc:
    print(f"  FAILED: {exc}")

print()

# Test 3: ibm/granite-4-h-small (IBM Granite - may support chat)
print("=== Test 3: ibm/granite-4-h-small (IBM Granite model) ===")
try:
    g4 = ModelInference(
        model_id="ibm/granite-4-h-small",
        credentials=creds,
        project_id=PID,
        params={"max_new_tokens": 300, "temperature": 0.2},
    )
    messages = [
        {"role": "system", "content": "You are PHAROS, a satellite compliance expert."},
        {"role": "user", "content": "In two sentences, why does the FCC 5-year LEO deorbit rule matter?"},
    ]
    result = g4.chat(messages=messages)
    choices = result.get("choices", [])
    text = choices[0].get("message", {}).get("content", "") if choices else ""
    print(f"  Response: {text[:300]}")
except Exception as exc:
    print(f"  FAILED: {exc}")

print()
print("=== SUMMARY ===")
print("Available on US-South (2399335c):")
print("  ibm/granite-guardian-3-8b  — REAL Granite Guardian")
print("  ibm/granite-4-h-small      — IBM Granite (test above)")
print("  meta-llama/llama-3-3-70b   — best instruct fallback")
print("  ibm/granite-embedding-278m — Granite Embedding (already wired)")
