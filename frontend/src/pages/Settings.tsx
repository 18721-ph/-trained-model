import { useState } from 'react'
import { checkApiConnection } from '../services/predictionApi'

export function Settings({ keepHistory, onKeepHistoryChange, recordCount, onClear }: { keepHistory: boolean; onKeepHistoryChange: (value: boolean) => void; recordCount: number; onClear: () => void }) {
  const [checking, setChecking] = useState(false)
  const [connection, setConnection] = useState('Not checked')
  const [confirmClear, setConfirmClear] = useState(false)
  async function checkConnection() {
    setChecking(true); setConnection('Checking connection…')
    try { await checkApiConnection(); setConnection('Prediction service is available.') }
    catch { setConnection('Could not reach the prediction service. Start the backend on port 8001 and try again.') }
    finally { setChecking(false) }
  }
  return <>
    <p className="eyebrow">WORKSPACE PREFERENCES</p><h1 className="mb-7 mt-3 text-3xl font-semibold">Settings</h1>
    <section className="panel p-6"><h2>Session history</h2><p className="mt-3 text-sm text-slate-500">Records and preferences stay in memory for this session only. Turning history off stops future records; existing records remain until cleared.</p>
      <label className="mt-5 flex items-center gap-3 text-sm"><input type="checkbox" className="!min-h-0 !w-5" checked={keepHistory} onChange={event => onKeepHistoryChange(event.target.checked)} />Keep completed assessments in session history</label>
      <p className="my-5 text-sm">{recordCount} retained assessment{recordCount === 1 ? '' : 's'}</p>
      {confirmClear ? <div><p className="mb-3 text-sm">Clear all retained assessments? This cannot be undone. The current assessment form and result will remain open.</p><div className="flex gap-3"><button className="action-button" onClick={() => { onClear(); setConfirmClear(false) }}>Confirm clear history</button><button className="secondary-button" onClick={() => setConfirmClear(false)}>Cancel</button></div></div> : <button className="secondary-button" disabled={!recordCount} onClick={() => setConfirmClear(true)}>Clear session history</button>}
    </section>
    <section className="panel mt-6 p-6"><h2>Prediction service</h2><p className="my-3 text-sm text-slate-500">Check whether the configured API responds before starting an assessment.</p><button className="secondary-button" disabled={checking} onClick={checkConnection}>{checking ? 'Checking…' : 'Check connection'}</button><p role="status" className="mt-3 text-sm">{connection}</p></section>
    <section className="panel mt-6 p-6"><h2>Model configuration</h2><p className="mt-3 text-sm text-slate-500">The saved model controls the decision threshold. Workspace preferences do not change predictions or model settings.</p></section>
  </>
}
