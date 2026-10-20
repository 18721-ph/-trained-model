import { useRef, useState } from 'react'
import { ApplicantForm } from '../components/assessment/ApplicantForm'
import { RiskResult } from '../components/results/RiskResult'
import { predictApplicant } from '../services/predictionApi'
import type { ApplicantRequest, PredictionResponse } from '../types/prediction'
export function RiskAssessmentPage() {
  const [result, setResult] = useState<PredictionResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const pending = useRef(false)
  async function assess(applicant: ApplicantRequest) {
    if (pending.current) return
    pending.current = true
    setLoading(true); setError(''); setResult(null)
    try { setResult(await predictApplicant(applicant)) }
    catch (error) { setError(error instanceof Error ? error.message : 'Unable to complete the assessment. Please try again.') }
    finally { pending.current = false; setLoading(false) }
  }
  return <><p className="eyebrow">CREDIT OPERATIONS / NEW ASSESSMENT</p><h1 className="mt-3 text-3xl font-semibold tracking-tight">New Risk Assessment</h1><p className="mb-7 mt-3 text-sm text-slate-500">A clearer view of borrower risk, informed by your project model.</p><div className="grid items-start gap-6 xl:grid-cols-[1.15fr_1fr]"><ApplicantForm loading={loading} onSubmit={assess} onEdit={() => { setResult(null); setError('') }} /><RiskResult result={result} loading={loading} error={error} /></div><p className="mt-7 text-xs text-slate-500">Local prototype · Applicant details are used for this assessment only.</p></>
}
