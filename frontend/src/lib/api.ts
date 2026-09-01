/**
 * PHAROS Backend API Client
 * All API calls go through this module for consistent error handling and typing.
 */

import type {
  ComplianceReport,
  ComplianceCheckRequest,
  SatelliteSearchResult,
  DemoDataset,
  StandardsResponse,
  JudgesResponse,
  HealthResponse,
} from './types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://pharos-backend-deployment--ojilerekingsley.replit.app'

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function fetchApi<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE}${path}`
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new ApiError(
      response.status,
      error.detail || error.message || `HTTP ${response.status}`,
    )
  }

  return response.json() as Promise<T>
}

export const api = {
  // Health
  health: (): Promise<HealthResponse> =>
    fetchApi<HealthResponse>('/api/health'),

  // Satellite search
  searchSatellites: (query: string, limit = 20): Promise<SatelliteSearchResult[]> =>
    fetchApi<SatelliteSearchResult[]>(
      `/api/satellites/search?query=${encodeURIComponent(query)}&limit=${limit}`,
    ),

  // Compliance checking
  checkCompliance: (request: ComplianceCheckRequest): Promise<ComplianceReport> =>
    fetchApi<ComplianceReport>('/api/compliance/check', {
      method: 'POST',
      body: JSON.stringify(request),
    }),

  getComplianceReport: (
    noradId: number,
    includeAi = true,
    includeCitations = true,
  ): Promise<ComplianceReport> =>
    fetchApi<ComplianceReport>(
      `/api/compliance/report/${noradId}?include_ai_report=${includeAi}&include_citations=${includeCitations}`,
    ),

  // Export
  getReportJsonUrl: (noradId: number): string =>
    `${API_BASE}/api/compliance/report/${noradId}/export/json`,

  getReportPdfUrl: (noradId: number): string =>
    `${API_BASE}/api/compliance/report/${noradId}/export/pdf`,

  // Demo data
  getDemo: (): Promise<DemoDataset> =>
    fetchApi<DemoDataset>('/api/demo'),

  getDemoSatellite: (noradId: number): Promise<ComplianceReport> =>
    fetchApi<ComplianceReport>(`/api/demo/${noradId}`),

  // Standards
  getStandards: (): Promise<StandardsResponse> =>
    fetchApi<StandardsResponse>('/api/standards'),

  getStandardRule: (ruleId: string): Promise<{
    rule: Record<string, unknown>
    citation: Record<string, unknown>
  }> =>
    fetchApi(`/api/standards/${ruleId}`),

  // Judges
  getJudges: (): Promise<JudgesResponse> =>
    fetchApi<JudgesResponse>('/api/judges'),
}

export { ApiError }
