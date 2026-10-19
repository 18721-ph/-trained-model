import { useState } from 'react'
import type { FormEvent } from 'react'
import type { ApplicantRequest } from '../../types/prediction'
type Field = { name: keyof ApplicantRequest; label: string; min?: number; max?: number; step?: string; options?: string[] }
const borrower: Field[] = [
  { name: 'customer_age', label: 'Customer Age (years)', min: 18, max: 100 },
  { name: 'customer_income', label: 'Annual Customer Income', min: 0, step: 'any' },
  { name: 'home_ownership', label: 'Home Ownership', options: ['RENT', 'OWN', 'MORTGAGE', 'OTHER'] },
  { name: 'employment_duration', label: 'Employment Duration (years)', min: 0, max: 70, step: 'any' },
  { name: 'cred_hist_length', label: 'Credit History Length (years)', min: 0, max: 80 },
]
const loan: Field[] = [
  { name: 'loan_intent', label: 'Loan Purpose', options: ['EDUCATION', 'MEDICAL', 'VENTURE', 'PERSONAL', 'DEBTCONSOLIDATION', 'HOMEIMPROVEMENT'] },
  { name: 'loan_grade', label: 'Loan Grade', options: ['A', 'B', 'C', 'D', 'E'] },
  { name: 'loan_amnt', label: 'Loan Amount', min: 0, step: 'any' },
  { name: 'loan_int_rate', label: 'Interest Rate (%)', min: 0, max: 50, step: 'any' },
  { name: 'term_years', label: 'Loan Term (years)', min: 1, max: 30 },
]
const optionLabel = (value: string) => ({ DEBTCONSOLIDATION: 'Debt consolidation', HOMEIMPROVEMENT: 'Home improvement' }[value] || (value.length === 1 ? value : value[0] + value.slice(1).toLowerCase()))
export function ApplicantForm({ loading, onSubmit, onEdit }: { loading: boolean; onSubmit: (value: ApplicantRequest) => void; onEdit: () => void }) {
  const [error, setError] = useState('')
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const entries = new FormData(event.currentTarget)
    const data = Object.fromEntries([...borrower, ...loan].map(field => [field.name, field.options ? entries.get(field.name) : Number(entries.get(field.name))])) as unknown as ApplicantRequest
    let message = ''
    if (data.customer_income <= 0 || data.loan_amnt <= 0) message = 'Income and loan amount must be greater than zero.'
    else if (data.employment_duration > data.customer_age - 14) message = "Employment duration is not realistic for the applicant's age."
    else if (data.cred_hist_length > data.customer_age) message = 'Credit history length cannot exceed customer age.'
    setError(message)
    if (!message) onSubmit(data)
  }
  return <form className="panel" onSubmit={submit} onChange={() => { setError(''); onEdit() }}>
    <div className="border-b border-slate-200 px-6 py-5"><h2>Applicant details</h2><p className="mt-1 text-sm text-slate-500">Complete all fields to assess default risk.</p></div>
    <fieldset disabled={loading} className="p-6">
      {[{ title: 'Borrower Information', fields: borrower }, { title: 'Loan Information', fields: loan }].map((section, index) => <section key={section.title} className={index ? 'mt-7 border-t border-slate-200 pt-6' : ''}>
        <h3 className="mb-5 flex items-center gap-3 text-sm font-semibold"><span className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-500">0{index + 1}</span>{section.title}</h3>
        <div className="grid gap-x-5 gap-y-4 sm:grid-cols-2">{section.fields.map(field => <div key={field.name}><label htmlFor={field.name} className="mb-2 block text-xs font-semibold text-slate-600">{field.label}</label>
          {field.options ? <select id={field.name} name={field.name} required defaultValue=""><option value="" disabled>Select an option</option>{field.options.map(option => <option key={option} value={option}>{optionLabel(option)}</option>)}</select> : <input id={field.name} name={field.name} type="number" required min={field.min} max={field.max} step={field.step || '1'} placeholder="Enter value" />}
        </div>)}</div>
      </section>)}
      <p className="mt-5 text-xs leading-5 text-slate-500">Use the same monetary unit for income and loan amount, consistent with the project dataset.</p>
      {error && <p role="alert" className="mt-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-900">{error}</p>}
      <button type="submit" className="mt-6 flex w-full items-center justify-center gap-3 rounded-lg bg-teal-800 px-4 py-3 text-sm font-semibold text-white hover:bg-teal-900 disabled:opacity-60">{loading && <span className="spinner" aria-hidden="true" />}{loading ? 'Assessing default risk…' : 'Assess Default Risk'}<span aria-hidden="true">→</span></button>
    </fieldset>
  </form>
}
