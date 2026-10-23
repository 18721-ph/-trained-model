import type { ReactNode } from 'react'
import type { Page } from '../../types/workspace'
export function Shell({ children, page, onNavigate }: { children: ReactNode; page: Page; onNavigate: (page: Page) => void }) {
  return <div className="min-h-screen lg:grid lg:grid-cols-[240px_1fr]">
    <a className="skip-link" href="#workspace">Skip to workspace</a>
    <aside className="flex flex-col bg-slate-900 px-5 py-7 text-slate-200 lg:sticky lg:top-0 lg:h-screen">
      <div className="mb-7 flex items-center gap-3">
        <img
          src="/ldrp-mark.png"
          alt="LDRP — Loan Default Risk Prediction"
          width={48}
          height={48}
          className="block size-12 shrink-0 rounded-lg bg-white object-contain p-1"
        />
        <div>
          <p className="text-base font-semibold tracking-wide text-white">LDRP</p>
          <p className="mt-1 text-xs text-slate-400">Credit assessment workspace</p>
        </div>
      </div>
      <p className="mb-3 text-[10px] font-bold tracking-[.18em] text-slate-400">WORKSPACE</p>
      <nav aria-label="Main navigation" className="flex flex-wrap gap-2 lg:flex-col">
        <button className="nav-item" aria-current={page === 'dashboard' ? 'page' : undefined} onClick={() => onNavigate('dashboard')}>Dashboard</button>
        <button className="nav-item" aria-current={page === 'assessment' ? 'page' : undefined} onClick={() => onNavigate('assessment')}>New Risk Assessment</button>
        <button className="nav-item" aria-current={page === 'history' ? 'page' : undefined} onClick={() => onNavigate('history')}>Assessment History</button>
        <button className="nav-item" aria-current={page === 'model' ? 'page' : undefined} onClick={() => onNavigate('model')}>Model Information</button>
        <button className="nav-item" aria-current={page === 'settings' ? 'page' : undefined} onClick={() => onNavigate('settings')}>Settings</button>
      </nav>
      <div className="mt-auto hidden border-t border-slate-700 pt-5 text-xs leading-6 text-slate-400 lg:block">Academic prototype<p className="text-slate-300">Local assessment environment</p><p>Session history clears on refresh.</p></div>
    </aside>
    <div className="min-w-0"><header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-white px-6 py-5 lg:px-9"><span className="text-sm font-medium">Loan Default Risk Assessment</span><span className="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-600">Prototype · Model v1.0</span></header><main id="workspace" className="mx-auto max-w-[1500px] px-5 py-8 lg:px-9">{children}</main></div>
  </div>
}
