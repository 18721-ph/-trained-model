import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, expect, it, vi } from 'vitest'
import { RiskAssessmentPage } from './RiskAssessmentPage'
import { predictApplicant } from '../services/predictionApi'
import { applicant, prediction } from '../test/fixtures'
vi.mock('../services/predictionApi', () => ({ predictApplicant: vi.fn() }))
beforeEach(() => vi.resetAllMocks())
function fill() {
  for (const [name, value] of Object.entries(applicant)) fireEvent.change(document.getElementById(name)!, { target: { value: String(value) } })
}
it('renders a blank form and allows input changes', async () => {
  render(<RiskAssessmentPage />)
  expect(screen.getAllByRole('spinbutton')).toHaveLength(7)
  expect(screen.getAllByRole('combobox')).toHaveLength(3)
  expect(screen.getByText('Ready when you are')).toBeInTheDocument()
  await userEvent.type(screen.getByLabelText('Customer Age (years)'), '45')
  await userEvent.selectOptions(screen.getByLabelText('Home Ownership'), 'RENT')
  expect(screen.getByLabelText('Customer Age (years)')).toHaveValue(45)
  expect(screen.getByLabelText('Home Ownership')).toHaveValue('RENT')
})
it.each(['DEFAULT', 'NO DEFAULT'] as const)('submits numeric data and displays %s with explanations', async label => {
  vi.mocked(predictApplicant).mockResolvedValue({ ...prediction, prediction: label, default_probability: label === 'DEFAULT' ? 0.6732 : 0.2, no_default_probability: label === 'DEFAULT' ? 0.3268 : 0.8 })
  render(<RiskAssessmentPage />); fill()
  await userEvent.click(screen.getByRole('button', { name: 'Assess Default Risk' }))
  expect(predictApplicant).toHaveBeenCalledWith(applicant)
  expect(await screen.findByText(label)).toBeInTheDocument()
  expect(screen.getByText(label === 'DEFAULT' ? '67.32%' : '20.00%')).toBeInTheDocument()
  expect(screen.getByText('56.00%')).toBeInTheDocument()
  expect(screen.getByText('Loan-to-income ratio')).toBeInTheDocument()
  expect(screen.getByText('Impact: +0.3205')).toBeInTheDocument()
  expect(screen.getByText('Impact: -0.0828')).toBeInTheDocument()
  fireEvent.change(screen.getByLabelText('Loan Amount'), { target: { value: '25000' } })
  expect(screen.queryByText(label)).not.toBeInTheDocument()
})
it('disables submission and shows loading until the request completes', async () => {
  let complete!: (value: typeof prediction) => void
  vi.mocked(predictApplicant).mockImplementation(() => new Promise(resolve => { complete = resolve }))
  render(<RiskAssessmentPage />); fill()
  await userEvent.click(screen.getByRole('button', { name: 'Assess Default Risk' }))
  expect(screen.getByRole('status')).toHaveTextContent('Assessment in progress')
  expect(screen.getByRole('button', { name: /Assessing default risk/ })).toBeDisabled()
  complete(prediction)
  await waitFor(() => expect(screen.getByRole('button', { name: 'Assess Default Risk' })).toBeEnabled())
})
it('displays service errors and permits retry', async () => {
  vi.mocked(predictApplicant).mockRejectedValue(new Error('Employment duration is not realistic for the applicant’s age.'))
  render(<RiskAssessmentPage />); fill()
  await userEvent.click(screen.getByRole('button', { name: 'Assess Default Risk' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Employment duration is not realistic')
  expect(screen.getByRole('button', { name: 'Assess Default Risk' })).toBeEnabled()
})
it.each([['employment_duration', '40', 'Employment duration'], ['cred_hist_length', '50', 'Credit history'], ['customer_income', '0', 'greater than zero']])('rejects invalid relationship or positive amount: %s', async (name, value, message) => {
  render(<RiskAssessmentPage />); fill()
  fireEvent.change(document.getElementById(name)!, { target: { value } })
  await userEvent.click(screen.getByRole('button', { name: 'Assess Default Risk' }))
  expect(screen.getByRole('alert')).toHaveTextContent(message)
  expect(predictApplicant).not.toHaveBeenCalled()
})
