import { expect, test } from '@playwright/test'

test('workspace pages use assessment results and remain usable on mobile', async ({ page }) => {
  await page.route('http://127.0.0.1:8001/**', async route => {
    await route.fulfill({ json: route.request().method() === 'POST' ? {
      default_probability: 0.6732, no_default_probability: 0.3268,
      decision_threshold: 0.56, prediction: 'DEFAULT',
      top_risk_factors: [{ feature: 'Loan-to-income ratio', impact: 0.3205 }],
      top_protective_factors: [{ feature: 'Customer age', impact: -0.0828 }],
    } : { message: 'Loan Default Prediction API is running' } })
  })
  await page.goto('/')
  const applicant = { customer_age: 45, customer_income: 50000, employment_duration: 20, cred_hist_length: 9, loan_amnt: 20000, loan_int_rate: 4, term_years: 1 }
  for (const [name, value] of Object.entries(applicant)) await page.locator(`#${name}`).fill(String(value))
  for (const [name, value] of Object.entries({ home_ownership: 'RENT', loan_intent: 'EDUCATION', loan_grade: 'B' })) await page.locator(`#${name}`).selectOption(value)
  await page.getByRole('button', { name: 'Assess Default Risk', exact: true }).click()
  await expect(page.getByText('67.32%', { exact: true })).toBeVisible()
  const nav = page.getByRole('navigation')
  await nav.getByRole('button', { name: 'Dashboard', exact: true }).click()
  await expect(page.getByLabel('Session statistics').getByText('67.32%', { exact: true })).toBeVisible()
  await page.screenshot({ path: test.info().outputPath('dashboard.png'), fullPage: true })
  await nav.getByRole('button', { name: 'Assessment History', exact: true }).click()
  await page.getByRole('button', { name: /View details/ }).click()
  await expect(page.getByRole('region', { name: 'Assessment details' })).toContainText('Loan-to-income ratio')
  await page.setViewportSize({ width: 390, height: 844 })
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
  await page.screenshot({ path: test.info().outputPath('history-mobile.png'), fullPage: true })
  await nav.getByRole('button', { name: 'Settings', exact: true }).click()
  await page.getByRole('button', { name: 'Check connection' }).click()
  await expect(page.getByRole('status')).toHaveText('Prediction service is available.')
  await page.getByRole('button', { name: 'Clear session history' }).click()
  await page.getByRole('button', { name: 'Confirm clear history' }).click()
  await expect(page.getByText('0 retained assessments')).toBeVisible()
  await page.screenshot({ path: test.info().outputPath('settings-mobile.png'), fullPage: true })
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
})
