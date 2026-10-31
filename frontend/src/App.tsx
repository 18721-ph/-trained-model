import { useEffect, useRef, useState } from 'react'
import { Shell } from './components/layout/Shell'
import { RiskAssessmentPage } from './pages/RiskAssessmentPage'
import { ModelInformation } from './pages/ModelInformation'
import { Dashboard } from './pages/Dashboard'
import { AssessmentHistory } from './pages/AssessmentHistory'
import { Settings } from './pages/Settings'
import type { AssessmentRecord, Page } from './types/workspace'
import type { ApplicantRequest, PredictionResponse } from './types/prediction'
import { changePassword, getCurrentUser, login, logout, type CurrentUser } from './services/authApi'
import { LoginPage } from './pages/LoginPage'
import { ChangePasswordPage } from './pages/ChangePasswordPage'
import { NotFoundPage } from './pages/NotFoundPage'
export default function App() {
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [checkingSession, setCheckingSession] = useState(true)
  const [page, setPage] = useState<Page>('assessment')
  const [records, setRecords] = useState<AssessmentRecord[]>([])
  const [keepHistory, setKeepHistory] = useState(true)
  const historyEnabled = useRef(true)
  const isNotFound = window.location.pathname !== '/'
  function updateHistoryPreference(enabled: boolean) {
    historyEnabled.current = enabled
    setKeepHistory(enabled)
  }
  function recordAssessment(applicant: ApplicantRequest, result: PredictionResponse) {
    if (historyEnabled.current) setRecords(current => [{ id: crypto.randomUUID(), createdAt: new Date().toISOString(), applicant, result }, ...current])
  }
  useEffect(() => {
    if (isNotFound) return
    getCurrentUser().then(setUser).catch(() => setUser(null)).finally(() => setCheckingSession(false))
  }, [isNotFound])
  if (isNotFound) return <NotFoundPage />
  if (checkingSession) return <main className="grid min-h-screen place-items-center text-sm text-slate-600">Checking secure session…</main>
  if (!user) return <LoginPage onLogin={async (username, password) => setUser(await login(username, password))} />
  async function signOut() { try { await logout() } finally { setUser(null); setRecords([]) } }
  return <Shell page={page} onNavigate={setPage} displayName={user.display_name} onLogout={signOut}>
    <div hidden={page !== 'assessment'}><RiskAssessmentPage onComplete={recordAssessment} keepHistory={keepHistory} /></div>
    {page === 'dashboard' && <Dashboard records={records} onNavigate={setPage} />}
    {page === 'history' && <AssessmentHistory records={records} onNew={() => setPage('assessment')} />}
    {page === 'model' && <ModelInformation />}
    {page === 'settings' && <Settings keepHistory={keepHistory} onKeepHistoryChange={updateHistoryPreference} recordCount={records.length} onClear={() => setRecords([])} />}
    {page === 'password' && <ChangePasswordPage onChange={async (currentPassword, newPassword) => { const updated = await changePassword(currentPassword, newPassword); setUser(updated); return updated }} />}
  </Shell>
}
