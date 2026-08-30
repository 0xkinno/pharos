/**
 * PHAROS TypeScript API Client Types
 * Mirrors the backend Pydantic models.
 */

export type RuleStatus = 'PASS' | 'FLAG' | 'FAIL' | 'SKIP' | 'ERROR'
export type ComplianceLevel = 'COMPLIANT' | 'AT_RISK' | 'NON_COMPLIANT' | 'UNKNOWN'
export type OrbitType = 'LEO' | 'MEO' | 'GEO' | 'HEO' | 'UNKNOWN'

export interface RuleResult {
  rule_id: string
  status: RuleStatus
  message: string
  value: number | null
  threshold: number | null
  unit: string | null
  standard_clause: string
  body: string
  retrieved_clause_text: string | null
  retrieved_clause_source: string | null
}

export interface ComplianceReport {
  norad_cat_id: number
  object_name: string
  epoch: string
  report_generated_at: string
  mean_altitude_km: number
  perigee_km: number
  apogee_km: number
  inclination_deg: number
  eccentricity: number
  mean_motion_rev_per_day: number
  estimated_orbital_lifetime_years: number
  orbit_type: OrbitType
  rule_results: RuleResult[]
  compliance_score: number
  compliance_level: ComplianceLevel
  rules_passed: number
  rules_flagged: number
  rules_failed: number
  rules_skipped: number
  ai_report_text: string | null
  ai_report_safe: boolean | null
  ai_available: boolean
  standards_checked: string[]
  data_sources: string[]
}

export interface SatelliteSearchResult {
  norad_cat_id: number
  object_name: string
  object_type?: string
  epoch?: string
  mean_motion?: number
  eccentricity?: number
  inclination?: number
  mean_altitude_km?: number | null
}

export interface DemoSatelliteSummary {
  norad_cat_id: number
  object_name: string
  description: string
  compliance_score: number
  compliance_level: ComplianceLevel
  orbit_type: OrbitType
  mean_altitude_km: number
  rules_passed: number
  rules_flagged: number
  rules_failed: number
  estimated_orbital_lifetime_years: number
}

export interface DemoDataset {
  generated_at: string
  note: string
  summary: {
    total_satellites: number
    compliant: number
    at_risk: number
    non_compliant: number
    average_score: number
  }
  satellites: DemoSatelliteSummary[]
}

export interface StandardsRule {
  id: string
  standard: string
  title: string
  description: string
  severity: string
  threshold: Record<string, number> | null
}

export interface StandardsBody {
  body: string
  rules: StandardsRule[]
}

export interface StandardsResponse {
  total_rules: number
  bodies: StandardsBody[]
}

export interface JudgesResponse {
  project: string
  tagline: string
  challenge: string
  theme: string
  ibm_stack: Record<string, unknown>
  api_deletion_test: {
    description: string
    result: string
    evidence: string
  }
  limitations: string[]
  compliance_engine: {
    total_rules: number
    standards_bodies: string[]
    rules_by_body: Record<string, string[]>
  }
  test_count: string
}

export interface ComplianceCheckRequest {
  norad_id: number
  mission_status?: 'active' | 'end-of-life' | 'decommissioned'
  years_since_mission_end?: number
  satellite_mass_kg?: number
  area_to_mass_ratio?: number
  has_propulsion?: boolean
  has_passivation_plan?: boolean
  is_registered_with_un?: boolean
  ssa_data_shared?: boolean
  collision_avoidance_capability?: boolean
  solar_activity?: 'low' | 'moderate' | 'high'
  include_ai_report?: boolean
  include_citations?: boolean
}

export interface HealthResponse {
  status: string
  service: string
  version: string
  watsonx_available: boolean
}
