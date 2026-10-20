import { useState } from 'react'
import { Shell } from './components/layout/Shell'
import { RiskAssessmentPage } from './pages/RiskAssessmentPage'
import { ModelInformation } from './pages/ModelInformation'
export default function App() {
  const [page, setPage] = useState<'assessment' | 'model'>('assessment')
  return <Shell page={page} onNavigate={setPage}><div hidden={page !== 'assessment'}><RiskAssessmentPage /></div>{page === 'model' && <ModelInformation />}</Shell>
}
