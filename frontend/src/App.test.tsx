import { fireEvent, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, expect, it, vi } from 'vitest'
import App from './App'
import { checkApiConnection, predictApplicant } from './services/predictionApi'
import { applicant, prediction } from './test/fixtures'
import { getCurrentUser } from './services/authApi'

vi.mock('./services/predictionApi', () => ({ predictApplicant: vi.fn(), checkApiConnection: vi.fn() }))
vi.mock('./services/authApi', () => ({ getCurrentUser: vi.fn(), login: vi.fn(), logout: vi.fn() }))
beforeEach(() => { vi.resetAllMocks(); vi.mocked(getCurrentUser).mockResolvedValue({ username: 'test', display_name: 'Test Analyst', role: 'analyst' }) })
async function navigate(name: string) {
  await userEvent.click(within(await screen.findByRole('navigation')).getByRole('button', { name }))
}
async function assess() {
  await screen.findByRole('button', { name: 'Assess Default Risk' })
  for (const [name, value] of Object.entries(applicant)) fireEvent.change(document.getElementById(name)!, { target: { value: String(value) } })
  await userEvent.click(await screen.findByRole('button', { name: 'Assess Default Risk' }))
}

it('opens every page and shows honest empty states', async () => {
  render(<App />)
  for (const name of ['Dashboard', 'Assessment History', 'Settings', 'Model Information', 'New Risk Assessment']) {
    await navigate(name)
    expect(screen.getByRole('heading', { level: 1, name })).toBeVisible()
  }
  await navigate('Assessment History')
  expect(screen.getByText('No assessments recorded yet')).toBeVisible()
  expect(screen.queryByText('Planned')).not.toBeInTheDocument()
})

it('records a successful prediction, filters history, reviews inputs and explanations, and clears records', async () => {
  vi.mocked(predictApplicant).mockResolvedValue(prediction)
  render(<App />)
  await assess()
  expect(await screen.findByText('DEFAULT')).toBeVisible()
  await navigate('Dashboard')
  expect(within(screen.getByLabelText('Session statistics')).getByText('67.32%')).toBeVisible()
  await navigate('Assessment History')
  await userEvent.selectOptions(screen.getByLabelText('Filter by prediction'), 'NO DEFAULT')
  expect(screen.getByText('No assessments match this filter.')).toBeVisible()
  await userEvent.selectOptions(screen.getByLabelText('Filter by prediction'), 'DEFAULT')
  await userEvent.click(screen.getByRole('button', { name: /View details/ }))
  const details = within(screen.getByRole('region', { name: 'Assessment details' }))
  expect(details.getByText('50000')).toBeVisible()
  expect(details.getByText('Loan-to-income ratio')).toBeVisible()
  await navigate('Settings')
  await userEvent.click(screen.getByRole('button', { name: 'Clear session history' }))
  await userEvent.click(screen.getByRole('button', { name: 'Cancel' }))
  expect(screen.getByText('1 retained assessment')).toBeVisible()
  await userEvent.click(screen.getByRole('button', { name: 'Clear session history' }))
  await userEvent.click(screen.getByRole('button', { name: 'Confirm clear history' }))
  await navigate('Assessment History')
  expect(screen.getByText('No assessments recorded yet')).toBeVisible()
})

it('does not record failed assessments and does not persist records across app mounts', async () => {
  vi.mocked(predictApplicant).mockRejectedValueOnce(new Error('Service unavailable')).mockResolvedValue(prediction)
  const view = render(<App />)
  await assess()
  expect(await screen.findByRole('alert')).toHaveTextContent('Service unavailable')
  await navigate('Assessment History')
  expect(screen.getByText('No assessments recorded yet')).toBeVisible()
  await navigate('New Risk Assessment')
  await assess()
  expect(await screen.findByText('DEFAULT')).toBeVisible()
  view.unmount()
  render(<App />)
  await navigate('Assessment History')
  expect(screen.getByText('No assessments recorded yet')).toBeVisible()
})

it('respects disabling history while an assessment is in flight', async () => {
  let complete!: (value: typeof prediction) => void
  vi.mocked(predictApplicant).mockImplementation(() => new Promise(resolve => { complete = resolve }))
  render(<App />)
  await assess()
  await navigate('Settings')
  await userEvent.click(screen.getByRole('checkbox', { name: 'Keep completed assessments in session history' }))
  complete(prediction)
  await navigate('New Risk Assessment')
  expect(await screen.findByText('DEFAULT')).toBeVisible()
  await navigate('Assessment History')
  expect(screen.getByText('No assessments recorded yet')).toBeVisible()
})

it('checks API availability and allows retry after a connection failure', async () => {
  vi.mocked(checkApiConnection).mockRejectedValueOnce(new Error('Offline')).mockResolvedValue(undefined)
  render(<App />)
  await navigate('Settings')
  await userEvent.click(screen.getByRole('button', { name: 'Check connection' }))
  expect(await screen.findByRole('status')).toHaveTextContent('Could not reach')
  await userEvent.click(screen.getByRole('button', { name: 'Check connection' }))
  expect(await screen.findByRole('status')).toHaveTextContent('Prediction service is available.')
})
