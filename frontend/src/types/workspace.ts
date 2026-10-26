import type { ApplicantRequest, PredictionResponse } from './prediction'

export type Page = 'dashboard' | 'assessment' | 'history' | 'model' | 'settings' | 'password'
export interface AssessmentRecord {
  id: string
  createdAt: string
  applicant: ApplicantRequest
  result: PredictionResponse
}
