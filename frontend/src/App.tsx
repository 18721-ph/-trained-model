import { useRef, useState } from 'react'
import { Shell } from './components/layout/Shell'
import { RiskAssessmentPage } from './pages/RiskAssessmentPage'
import { ModelInformation } from './pages/ModelInformation'
import { Dashboard } from './pages/Dashboard'
import { AssessmentHistory } from './pages/AssessmentHistory'
import { Settings } from './pages/Settings'
import type { AssessmentRecord, Page } from './types/workspace'
import type { ApplicantRequest, PredictionResponse } from './types/prediction'
export default function App() {
  const [page, setPage] = useState<Page>('assessment')
  const [records, setRecords] = useState<AssessmentRecord[]>([])
  const [keepHistory, setKeepHistory] = useState(true)
  const historyEnabled = useRef(true)
  function updateHistoryPreference(enabled: boolean) {
    historyEnabled.current = enabled
    setKeepHistory(enabled)
  }
  function recordAssessment(applicant: ApplicantRequest, result: PredictionResponse) {
    if (historyEnabled.current) setRecords(current => [{ id: crypto.randomUUID(), createdAt: new Date().toISOString(), applicant, result }, ...current])
  }
  return <Shell page={page} onNavigate={setPage}>
    <div hidden={page !== 'assessment'}><RiskAssessmentPage onComplete={recordAssessment} keepHistory={keepHistory} /></div>
    {page === 'dashboard' && <Dashboard records={records} onNavigate={setPage} />}
    {page === 'history' && <AssessmentHistory records={records} onNew={() => setPage('assessment')} />}
    {page === 'model' && <ModelInformation />}
    {page === 'settings' && <Settings keepHistory={keepHistory} onKeepHistoryChange={updateHistoryPreference} recordCount={records.length} onClear={() => setRecords([])} />}
  </Shell>
}
