"""
Pydantic models for compliance results and reports.
"""
from enum import Enum
from typing import Optional, Any
from datetime import datetime

from pydantic import BaseModel, Field


class RuleStatus(str, Enum):
    PASS = "PASS"
    FLAG = "FLAG"
    FAIL = "FAIL"
    SKIP = "SKIP"  # Rule not applicable to this orbit type
    ERROR = "ERROR"  # Evaluation failed (data missing)


class ComplianceLevel(str, Enum):
    COMPLIANT = "COMPLIANT"
    AT_RISK = "AT_RISK"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNKNOWN = "UNKNOWN"


class RuleResult(BaseModel):
    """Result from a single rule evaluation."""
    rule_id: str = Field(..., description="e.g. FCC-DEORBIT-01")
    status: RuleStatus
    message: str = Field(..., description="Human-readable result message")
    value: Optional[float] = Field(None, description="The measured value (e.g. lifetime in years)")
    threshold: Optional[float] = Field(None, description="The regulatory threshold")
    unit: Optional[str] = Field(None, description="Unit for value/threshold (e.g. 'years', 'km')")
    standard_clause: str = Field(..., description="Exact regulatory citation")
    body: str = Field(..., description="Regulatory body (FCC, IADC, ISO, ESA, COPUOS)")
    # RAG-retrieved clause text
    retrieved_clause_text: Optional[str] = Field(
        None,
        description="Verbatim text from the standards corpus, retrieved by Granite Embedding"
    )
    retrieved_clause_source: Optional[str] = Field(None)


class ComplianceReport(BaseModel):
    """Full compliance report for a single satellite."""
    # Satellite identification
    norad_cat_id: int
    object_name: str
    epoch: str
    report_generated_at: datetime = Field(default_factory=datetime.utcnow)

    # Orbital parameters used for evaluation
    mean_altitude_km: float
    perigee_km: float
    apogee_km: float
    inclination_deg: float
    eccentricity: float
    mean_motion_rev_per_day: float
    estimated_orbital_lifetime_years: float
    orbit_type: str  # "LEO", "MEO", "GEO", "HEO"

    # Rule evaluation results
    rule_results: list[RuleResult] = Field(default_factory=list)

    # Aggregate scoring
    compliance_score: float = Field(..., ge=0.0, le=100.0)
    compliance_level: ComplianceLevel
    rules_passed: int = 0
    rules_flagged: int = 0
    rules_failed: int = 0
    rules_skipped: int = 0

    # AI layer outputs
    ai_report_text: Optional[str] = Field(
        None,
        description="Plain-language compliance report from Granite Instruct"
    )
    ai_report_safe: Optional[bool] = Field(
        None,
        description="Content safety screening result from Granite Guardian"
    )
    ai_available: bool = Field(
        False,
        description="Whether IBM watsonx.ai was available when this report was generated"
    )

    # Metadata
    standards_checked: list[str] = Field(default_factory=list)
    data_sources: list[str] = Field(default_factory=list)

    def compute_score(self) -> None:
        """Compute compliance score and level from rule results."""
        applicable = [r for r in self.rule_results if r.status != RuleStatus.SKIP]
        if not applicable:
            self.compliance_score = 100.0
            self.compliance_level = ComplianceLevel.UNKNOWN
            return

        passed = sum(1 for r in applicable if r.status == RuleStatus.PASS)
        flagged = sum(1 for r in applicable if r.status == RuleStatus.FLAG)
        failed = sum(1 for r in applicable if r.status == RuleStatus.FAIL)

        self.rules_passed = passed
        self.rules_flagged = flagged
        self.rules_failed = failed
        self.rules_skipped = sum(1 for r in self.rule_results if r.status == RuleStatus.SKIP)

        total = len(applicable)
        # Score: PASS=1.0, FLAG=0.5, FAIL=0.0 (normalized to 0-100)
        weighted = (passed * 1.0 + flagged * 0.5 + failed * 0.0) / total
        self.compliance_score = round(weighted * 100, 1)

        if self.rules_failed > 0:
            self.compliance_level = ComplianceLevel.NON_COMPLIANT
        elif self.rules_flagged > 0:
            self.compliance_level = ComplianceLevel.AT_RISK
        else:
            self.compliance_level = ComplianceLevel.COMPLIANT


class DemoSatellite(BaseModel):
    """Pre-computed demo satellite entry."""
    norad_cat_id: int
    object_name: str
    description: str
    compliance_report: ComplianceReport


class DemoDataset(BaseModel):
    """Pre-computed demo dataset."""
    generated_at: datetime
    satellites: list[DemoSatellite]
    summary: dict[str, Any] = Field(default_factory=dict)
