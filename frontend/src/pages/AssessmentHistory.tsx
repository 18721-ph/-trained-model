import { useState } from 'react'
import { RiskResult } from '../components/results/RiskResult'
import type { AssessmentRecord } from '../types/workspace'

export function AssessmentHistory({ records, onNew }: { records: AssessmentRecord[]; onNew: () => void }) {
  const [filter, setFilter] = useState('ALL')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const visible = records.filter(record => filter === 'ALL' || record.result.prediction === filter)
  const selected = records.find(record => record.id === selectedId)
  return <>
    <p className="eyebrow">SESSION RECORDS</p><h1 className="mt-3 text-3xl font-semibold">Assessment History</h1>
    <p className="mb-7 mt-3 text-sm text-slate-500">Review successful assessments from this session. Refreshing the page clears these records.</p>
    <section className="panel p-6">
      <label className="block max-w-xs text-sm" htmlFor="history-filter">Filter by prediction<select id="history-filter" className="mt-2" value={filter} onChange={event => { setFilter(event.target.value); setSelectedId(null) }}><option value="ALL">All predictions</option><option value="DEFAULT">DEFAULT</option><option value="NO DEFAULT">NO DEFAULT</option></select></label>
      {!records.length ? <div className="py-8"><h2>No assessments recorded yet</h2><p className="my-3 text-sm text-slate-500">Complete an assessment with session history enabled to see it here.</p><button className="action-button" onClick={onNew}>New assessment</button></div> : !visible.length ? <p className="py-8 text-sm">No assessments match this filter.</p> : <ul className="mt-5 divide-y divide-slate-200">{visible.map(record => <li key={record.id} className="flex flex-wrap items-center justify-between gap-4 py-4"><div><p className="font-medium">{record.result.prediction} · {(record.result.default_probability * 100).toFixed(2)}% default probability</p><p className="mt-1 text-sm text-slate-500">{new Date(record.createdAt).toLocaleString()} · Loan amount: {record.applicant.loan_amnt.toLocaleString()}</p></div><button className="secondary-button" aria-pressed={selectedId === record.id} onClick={() => setSelectedId(selectedId === record.id ? null : record.id)}>View details<span className="sr-only"> for {record.id}</span></button></li>)}</ul>}
    </section>
    {selected && <section className="mt-6 grid items-start gap-6 xl:grid-cols-2" aria-label="Assessment details"><div className="panel p-6"><h2>Applicant details</h2><p className="mt-2 text-sm text-slate-500">Assessed {new Date(selected.createdAt).toLocaleString()}</p><dl className="mt-5 grid gap-4 sm:grid-cols-2">{Object.entries(selected.applicant).map(([key, value]) => <div key={key}><dt className="text-xs capitalize text-slate-500">{key.replaceAll('_', ' ')}</dt><dd className="mt-1 break-words text-sm">{value}</dd></div>)}</dl></div><RiskResult result={selected.result} loading={false} error="" /></section>}
  </>
}
