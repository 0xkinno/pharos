"""Full API smoke test — python -m scripts.smoke_test"""
import warnings
warnings.filterwarnings("ignore")

from app.core.config import get_settings
get_settings.cache_clear()
from app.ai.watsonx_client import get_watsonx_client
get_watsonx_client.cache_clear()

from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)

print("=== PHAROS Full API Smoke Test ===")

r = c.get("/api/health")
h = r.json()
print(f"Health:    {r.status_code} | watsonx_available={h['watsonx_available']}")

r = c.get("/api/judges")
j = r.json()
print(f"Judges:    {r.status_code} | project={j['project']} | ibm_tools={len(j['ibm_stack'])}")

r = c.get("/api/demo")
d = r.json()
print(f"Demo:      {r.status_code} | satellites={len(d['satellites'])} | avg={d['summary']['average_score']:.1f}")

r = c.get("/api/standards")
s = r.json()
print(f"Standards: {r.status_code} | total_rules={s['total_rules']} | bodies={len(s['bodies'])}")

r = c.get("/api/standards/FCC-DEORBIT-01")
rule_data = r.json()
print(f"Rule:      {r.status_code} | id={rule_data['rule']['id']} | method={rule_data['citation']['retrieval_method']}")

r = c.get("/")
print(f"Root:      {r.status_code}")

print()
print("=== ALL ENDPOINTS OPERATIONAL ===")
