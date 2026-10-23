import type { AssessmentRecord, Page } from '../types/workspace'

export function Dashboard({ records, onNavigate }: { records: AssessmentRecord[]; onNavigate: (page: Page) => void }) {
  const defaults = records.filter(record => record.result.prediction === 'DEFAULT').length
  const average = records.length ? `${(100 * records.reduce((sum, record) => sum + record.result.default_probability, 0) / records.length).toFixed(2)}%` : '—'
  return <>
    <p className="eyebrow">WORKSPACE OVERVIEW</p>
    <h1 className="mt-3 text-3xl font-semibold">Dashboard</h1>
    <p className="mb-7 mt-3 text-sm text-slate-500">Completed assessments retained in this session. These figures are not model performance metrics.</p>
    <dl aria-label="Session statistics" className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {([['Assessments', records.length], ['Predicted default', defaults], ['Predicted no default', records.length - defaults], ['Mean default probability', average]] as const).map(([label, value]) => <div className="panel p-6" key={label}><dt className="text-sm text-slate-500">{label}</dt><dd className="mt-3 text-3xl font-semibold">{value}</dd></div>)}
    </dl>
    <section className="panel mt-6 p-6">
      <h2>{records.length ? 'Continue your assessment work' : 'Start your first assessment'}</h2>
      <p className="mt-3 text-sm text-slate-500">Assess a borrower to see calibrated default probability and the factors behind the prediction.</p>
      <div className="mt-5 flex flex-wrap gap-3"><button className="action-button" onClick={() => onNavigate('assessment')}>New assessment</button><button className="secondary-button" onClick={() => onNavigate('history')}>View assessment history</button></div>
    </section>
    <p className="mt-6 text-xs text-slate-500">History is held in memory and clears when you refresh or close this page. History collection can be turned off in Settings.</p>
  </>
}
