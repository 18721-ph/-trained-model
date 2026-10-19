import { expect, test } from '@playwright/test'
import { applicant } from '../src/test/fixtures'
test('real local prediction and responsive workspace', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1100 })
  await page.goto('/')
  await expect(page.getByText('Ready when you are')).toBeVisible()
  for (const [name, value] of Object.entries(applicant)) {
    const control = page.locator(`[name="${name}"]`)
    if (typeof value === 'number') await control.fill(String(value))
    else await control.selectOption(value)
  }
  const responsePromise = page.waitForResponse(response => response.url().endsWith('/predict') && response.request().method() === 'POST')
  await page.getByRole('button', { name: 'Assess Default Risk' }).click()
  const response = await responsePromise
  expect(response.ok()).toBeTruthy()
  const result = await response.json()
  expect(result.default_probability).toBeGreaterThanOrEqual(0)
  expect(result.default_probability).toBeLessThanOrEqual(1)
  await expect(page.getByText(`${(result.default_probability * 100).toFixed(2)}%`, { exact: true })).toBeVisible()
  await expect(page.getByText(result.prediction, { exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Factors influencing the model prediction' })).toBeVisible()
  console.log('Real API result:', JSON.stringify({ probability: result.default_probability, prediction: result.prediction }))
  await page.screenshot({ path: 'test-results/assessment-desktop.png', fullPage: true })
  for (const width of [768, 390]) {
    await page.setViewportSize({ width, height: 1000 })
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBeTruthy()
    await page.screenshot({ path: `test-results/assessment-${width}.png`, fullPage: true })
  }
  await page.getByRole('button', { name: 'Model Information' }).click()
  await expect(page.getByRole('heading', { name: 'Prototype evaluation results on the held-out project test dataset' })).toBeVisible()
})
