import type { ApplicantRequest, PredictionResponse } from '../types/prediction'
import { getCsrfToken } from './authApi'
const baseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001').replace(/\/$/, '')
export async function checkApiConnection(): Promise<void> {
  const response = await fetch(`${baseUrl}/`, { signal: AbortSignal.timeout(10000) })
  if (!response.ok) throw new Error('API unavailable')
  const data: unknown = await response.json()
  if (!record(data) || data.message !== 'Loan Default Prediction API is running') throw new Error('Unexpected API response')
}
const record = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null
const probability = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 1
function factors(value: unknown) {
  return Array.isArray(value) && value.every(item => record(item) && typeof item.feature === 'string' && typeof item.impact === 'number' && Number.isFinite(item.impact))
}
function validResponse(value: unknown): value is PredictionResponse {
  return record(value) && probability(value.default_probability) && probability(value.no_default_probability)
    && Math.abs(value.default_probability + value.no_default_probability - 1) < 0.00001
    && probability(value.decision_threshold) && ['DEFAULT', 'NO DEFAULT'].includes(String(value.prediction))
    && factors(value.top_risk_factors) && factors(value.top_protective_factors)
}
export async function predictApplicant(applicant: ApplicantRequest): Promise<PredictionResponse> {
  let response: Response
  try {
    response = await fetch(`${baseUrl}/predict`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': await getCsrfToken() }, body: JSON.stringify(applicant), signal: AbortSignal.timeout(60000) })
  } catch { throw new Error('Unable to reach the prediction service. Check that the local API is running on port 8001, then try again.') }
  let data: unknown
  try { data = await response.json() } catch { throw new Error('The prediction service returned an unreadable response. Please try again.') }
  if (!response.ok) {
    if (response.status === 401 || response.status === 403) throw new Error('Your session has expired. Please sign in again.')
    if (response.status === 422 && record(data) && Array.isArray(data.detail)) {
      const messages = data.detail.filter(record).map(item => {
        const field = Array.isArray(item.loc) ? item.loc.filter(part => part !== 'body').join(' ').replaceAll('_', ' ') : ''
        return typeof item.msg === 'string' ? `${field ? `${field}: ` : ''}${item.msg.replace(/^Value error, /, '')}` : ''
      }).filter(Boolean)
      if (messages.length) throw new Error(messages.join(' '))
    }
    throw new Error(response.status === 422 ? 'Please check the applicant details and try again.' : 'The prediction service could not complete this assessment. Please try again.')
  }
  if (!validResponse(data)) throw new Error('The prediction service returned an invalid result. Please try again.')
  return data
}
