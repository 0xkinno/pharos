"""
Tests for the FastAPI REST API

Tests all key API endpoints with mocking where necessary.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /api/health."""

    def test_health_returns_200(self):
        """Health endpoint returns 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self):
        """Health response includes status: ok."""
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_service_name(self):
        """Health response includes service name."""
        response = client.get("/api/health")
        data = response.json()
        assert "PHAROS" in data["service"]


class TestRootEndpoint:
    """Tests for GET /."""

    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_lists_key_endpoints(self):
        response = client.get("/")
        data = response.json()
        assert "health" in data or "docs" in data


class TestJudgesEndpoint:
    """Tests for GET /api/judges."""

    def test_judges_returns_200(self):
        """Judges endpoint returns 200 OK."""
        response = client.get("/api/judges")
        assert response.status_code == 200

    def test_judges_has_ibm_stack(self):
        """Judges response includes IBM stack section."""
        response = client.get("/api/judges")
        data = response.json()
        assert "ibm_stack" in data

    def test_judges_has_all_ibm_tools(self):
        """Judges response documents all IBM tools."""
        response = client.get("/api/judges")
        data = response.json()
        stack = data["ibm_stack"]
        assert "bob" in stack
        assert "granite_instruct" in stack
        assert "granite_embedding" in stack
        assert "granite_guardian" in stack
        assert "docling" in stack

    def test_judges_has_limitations(self):
        """Judges response includes honest limitations."""
        response = client.get("/api/judges")
        data = response.json()
        assert "limitations" in data
        assert len(data["limitations"]) >= 3

    def test_judges_has_api_deletion_test(self):
        """Judges response documents API-deletion behavior."""
        response = client.get("/api/judges")
        data = response.json()
        assert "api_deletion_test" in data

    def test_judges_has_compliance_engine_info(self):
        """Judges response includes engine details."""
        response = client.get("/api/judges")
        data = response.json()
        assert "compliance_engine" in data


class TestDemoEndpoint:
    """Tests for GET /api/demo."""

    def test_demo_returns_200(self):
        """Demo endpoint returns 200 OK."""
        response = client.get("/api/demo")
        assert response.status_code == 200

    def test_demo_has_satellites(self):
        """Demo response includes satellite compliance reports."""
        response = client.get("/api/demo")
        data = response.json()
        assert "satellites" in data
        assert len(data["satellites"]) > 0

    def test_demo_satellites_have_compliance_scores(self):
        """Each demo satellite has a compliance score."""
        response = client.get("/api/demo")
        data = response.json()
        for sat in data["satellites"]:
            assert "compliance_score" in sat
            assert 0.0 <= sat["compliance_score"] <= 100.0

    def test_demo_satellites_have_compliance_levels(self):
        """Each demo satellite has a compliance level."""
        response = client.get("/api/demo")
        data = response.json()
        valid_levels = {"COMPLIANT", "AT_RISK", "NON_COMPLIANT", "UNKNOWN"}
        for sat in data["satellites"]:
            assert sat["compliance_level"] in valid_levels

    def test_demo_has_summary(self):
        """Demo response includes summary statistics."""
        response = client.get("/api/demo")
        data = response.json()
        assert "summary" in data
        assert "total_satellites" in data["summary"]

    def test_demo_satellite_has_orbit_type(self):
        """Each demo satellite has orbit type classified."""
        response = client.get("/api/demo")
        data = response.json()
        valid_orbit_types = {"LEO", "MEO", "GEO", "HEO"}
        for sat in data["satellites"]:
            assert sat["orbit_type"] in valid_orbit_types


class TestStandardsEndpoint:
    """Tests for GET /api/standards."""

    def test_standards_returns_200(self):
        """Standards endpoint returns 200 OK."""
        response = client.get("/api/standards")
        assert response.status_code == 200

    def test_standards_lists_all_bodies(self):
        """Standards response includes all 5 regulatory bodies."""
        response = client.get("/api/standards")
        data = response.json()
        assert "bodies" in data
        body_names = [b["body"] for b in data["bodies"]]
        for body in ["FCC", "IADC", "ISO", "ESA", "COPUOS"]:
            assert body in body_names

    def test_standards_has_rule_count(self):
        """Standards response includes total rule count."""
        response = client.get("/api/standards")
        data = response.json()
        assert "total_rules" in data
        assert data["total_rules"] >= 15

    def test_specific_rule_lookup(self):
        """Can look up a specific rule by ID."""
        response = client.get("/api/standards/FCC-DEORBIT-01")
        assert response.status_code == 200
        data = response.json()
        assert "rule" in data
        assert data["rule"]["id"] == "FCC-DEORBIT-01"

    def test_unknown_rule_returns_404(self):
        """Unknown rule ID returns 404."""
        response = client.get("/api/standards/NONEXISTENT-RULE")
        assert response.status_code == 404
