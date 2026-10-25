const baseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001').replace(/\/$/, '')
export type CurrentUser = { username: string; display_name: string; role: string }
let csrfToken: string | null = null
async function json(response: Response): Promise<unknown> { try { return await response.json() } catch { return null } }
export async function login(username: string, password: string): Promise<CurrentUser> {
  const response = await fetch(`${baseUrl}/auth/login`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username, password }) })
  if (!response.ok) { if (response.status === 401) throw new Error('Invalid username or password.'); if (response.status === 429) throw new Error('Too many login attempts. Please try again later.'); throw new Error('Unable to sign in. Please try again.') }
  csrfToken = null; return await json(response) as CurrentUser
}
export async function getCurrentUser(): Promise<CurrentUser | null> { const response = await fetch(`${baseUrl}/auth/me`, { credentials: 'include' }); if (response.status === 401) return null; if (!response.ok) throw new Error('Unable to check your session.'); return await json(response) as CurrentUser }
export async function getCsrfToken(): Promise<string> { if (csrfToken) return csrfToken; const response = await fetch(`${baseUrl}/auth/csrf`, { credentials: 'include' }); const data = await json(response); if (!response.ok || !data || typeof (data as { csrf_token?: unknown }).csrf_token !== 'string') throw new Error('Your session has expired. Please sign in again.'); csrfToken = (data as { csrf_token: string }).csrf_token; return csrfToken }
export async function logout(): Promise<void> { const token = await getCsrfToken(); await fetch(`${baseUrl}/auth/logout`, { method: 'POST', credentials: 'include', headers: { 'X-CSRF-Token': token } }); csrfToken = null }
