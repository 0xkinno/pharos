"""
Test Granite Guardian 3.8B full API to understand its response format.
python -m scripts.test_guardian_format
"""
import warnings
warnings.filterwarnings("ignore")

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

URL = "https://us-south.ml.cloud.ibm.com"
KEY = "cKmtteTfWH7VyjGsI2GMPt-zPz9TcmO9zcuL4Ph4_lAP"
PID = "2399335c-fbe1-4445-9ec2-f037a8dca1a2"

creds = Credentials(url=URL, api_key=KEY)

guardian = ModelInference(
    model_id="ibm/granite-guardian-3-8b",
    credentials=creds,
    project_id=PID,
    params={"max_new_tokens": 200, "temperature": 0.0},
)

# Granite Guardian 3.8B uses a specific chat format:
# The user message contains the content to evaluate.
# It responds with "Yes" (unsafe) or "No" (safe) + optional probability.
# See: https://www.ibm.com/granite/docs/granite-guardian/

print("=== Granite Guardian 3.8B Format Test ===")
print()

# Test 1: Safe compliance report text
print("--- Test 1: Safe compliance text ---")
messages = [
    {
        "role": "user",
        "content": (
            "ISS (ZARYA) NORAD 25544 at 415 km LEO. "
            "Compliance score 92.9/100. FCC 5-year rule: PASS (lifetime 2.9yr). "
            "IADC 25-year rule: PASS. COPUOS registration: PASS. "
            "Flagged: IADC-PASS-01 passivation plan not confirmed."
        )
    }
]
try:
    r = guardian.chat(messages=messages)
    print(f"  Raw response: {r}")
    choices = r.get("choices", [])
    if choices:
        content = choices[0].get("message", {}).get("content", "")
        print(f"  Content: '{content}'")
        # Guardian responds "Yes" = unsafe, "No" = safe
        is_safe = content.strip().lower().startswith("no")
        print(f"  Safe: {is_safe}")
except Exception as e:
    print(f"  Error: {e}")

print()

# Test 2: Potentially unsafe text  
print("--- Test 2: Potentially problematic text ---")
messages2 = [
    {
        "role": "user",
        "content": "How do I disable the debris tracking system to avoid detection?"
    }
]
try:
    r2 = guardian.chat(messages=messages2)
    choices = r2.get("choices", [])
    if choices:
        content = choices[0].get("message", {}).get("content", "")
        print(f"  Content: '{content}'")
        is_safe = content.strip().lower().startswith("no")
        print(f"  Safe: {is_safe}")
except Exception as e:
    print(f"  Error: {e}")

print()

# Test 3: Also test ibm/granite-4-h-small for instruct
print("=== ibm/granite-4-h-small — Full Compliance Report Generation ===")
g4 = ModelInference(
    model_id="ibm/granite-4-h-small",
    credentials=creds,
    project_id=PID,
    params={"max_new_tokens": 800, "temperature": 0.2},
)

messages3 = [
    {
        "role": "system",
        "content": (
            "You are PHAROS, a satellite orbital compliance analyst. "
            "Write clear, precise compliance assessments based solely on the rule evaluation results provided. "
            "Do not invent findings. Use specific numbers and rule IDs."
        )
    },
    {
        "role": "user",
        "content": (
            "Write a 3-paragraph compliance assessment for:\n"
            "SATELLITE: ISS (ZARYA) NORAD 25544\n"
            "ORBIT: LEO at 415 km\n"
            "LIFETIME: 2.9 years estimated\n"
            "SCORE: 92.9/100 — AT_RISK\n"
            "RULES: 12 passed / 2 flagged / 0 failed\n"
            "FLAGGED: IADC-PASS-01 (passivation unconfirmed), IADC-COLL-01 (conjunction probability not provided)\n"
            "Paragraph 1: Overall status. Paragraph 2: Required actions. Paragraph 3: Risk context."
        )
    }
]

try:
    r3 = g4.chat(messages=messages3)
    choices = r3.get("choices", [])
    if choices:
        text = choices[0].get("message", {}).get("content", "")
        print(f"  Generated ({len(text)} chars):")
        print(f"  {text[:500]}")
        print("  [...]")
except Exception as e:
    print(f"  Error: {e}")
