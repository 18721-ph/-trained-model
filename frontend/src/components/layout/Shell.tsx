import type { ReactNode } from 'react'
export function Shell({ children, page, onNavigate }: { children: ReactNode; page: 'assessment' | 'model'; onNavigate: (page: 'assessment' | 'model') => void }) {
  return <div className="min-h-screen lg:grid lg:grid-cols-[240px_1fr]">
    <a className="skip-link" href="#workspace">Skip to workspace</a>
    <aside className="flex flex-col bg-slate-900 px-5 py-7 text-slate-200 lg:sticky lg:top-0 lg:h-screen">
      <div className="mb-9 flex items-center gap-3"><span className="grid size-10 place-items-center rounded-lg bg-teal-700 text-xl font-bold text-white" aria-hidden="true">L</span><div className="font-semibold tracking-wide text-white">LEND / INSIGHT<p className="mt-1 text-xs font-normal text-slate-400">Credit assessment workspace</p></div></div>
      <p className="mb-3 text-[10px] font-bold tracking-[.18em] text-slate-400">WORKSPACE</p>
      <nav aria-label="Main navigation" className="flex flex-wrap gap-2 lg:flex-col">
        <button className="nav-item" disabled>Dashboard <span className="text-xs">Planned</span></button>
        <button className="nav-item" aria-current={page === 'assessment' ? 'page' : undefined} onClick={() => onNavigate('assessment')}>New Risk Assessment</button>
        <button className="nav-item" disabled>Assessment History <span className="text-xs">Planned</span></button>
        <button className="nav-item" aria-current={page === 'model' ? 'page' : undefined} onClick={() => onNavigate('model')}>Model Information</button>
        <button className="nav-item" disabled>Settings <span className="text-xs">Planned</span></button>
      </nav>
      <div className="mt-auto hidden border-t border-slate-700 pt-5 text-xs leading-6 text-slate-400 lg:block">Academic prototype<p className="text-slate-300">Local assessment environment</p><p>No applicant records are saved.</p></div>
    </aside>
    <div className="min-w-0"><header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-white px-6 py-5 lg:px-9"><span className="text-sm font-medium">Loan Default Risk Assessment</span><span className="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-600">Prototype · Model v1.0</span></header><main id="workspace" className="mx-auto max-w-[1500px] px-5 py-8 lg:px-9">{children}</main></div>
  </div>
}
