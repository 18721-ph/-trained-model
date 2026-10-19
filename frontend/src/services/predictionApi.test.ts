import { afterEach, expect, it, vi } from 'vitest'
import { predictApplicant } from './predictionApi'
import { applicant, prediction } from '../test/fixtures'
afterEach(() => vi.unstubAllGlobals())
it('posts the API contract and returns validated data', async () => {
  const fetchMock = vi.fn().mockResolvedValue(Response.json(prediction))
  vi.stubGlobal('fetch', fetchMock)
  expect(await predictApplicant(applicant)).toEqual(prediction)
  expect(fetchMock).toHaveBeenCalledWith('http://127.0.0.1:8001/predict', expect.objectContaining({ method: 'POST', body: JSON.stringify(applicant) }))
})
it('extracts FastAPI validation details', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json({ detail: [{ loc: ['body'], msg: 'Value error, Employment duration is not realistic.' }] }, { status: 422 })))
  await expect(predictApplicant(applicant)).rejects.toThrow('Employment duration is not realistic.')
})
it('handles network failure', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
  await expect(predictApplicant(applicant)).rejects.toThrow('Unable to reach')
})
it('hides unexpected server details', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json({ detail: 'private traceback' }, { status: 500 })))
  await expect(predictApplicant(applicant)).rejects.toThrow('could not complete')
})
it.each([{}, { ...prediction, default_probability: 2 }, { ...prediction, top_risk_factors: [{}] }, { ...prediction, no_default_probability: 0.9 }])('rejects malformed result %j', async value => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(Response.json(value)))
  await expect(predictApplicant(applicant)).rejects.toThrow('invalid result')
})
it('handles non-JSON responses', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('<html>error</html>')))
  await expect(predictApplicant(applicant)).rejects.toThrow('unreadable response')
})
