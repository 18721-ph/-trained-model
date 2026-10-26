import { useState } from 'react'
import type { FormEvent } from 'react'
import type { CurrentUser } from '../services/authApi'

export function ChangePasswordPage({ onChange }: { onChange: (currentPassword: string, newPassword: string) => Promise<CurrentUser> }) {
  const [currentPassword, setCurrentPassword] = useState(''); const [newPassword, setNewPassword] = useState(''); const [confirmPassword, setConfirmPassword] = useState(''); const [message, setMessage] = useState(''); const [error, setError] = useState(''); const [saving, setSaving] = useState(false)
  async function submit(event: FormEvent) {
    event.preventDefault(); setError(''); setMessage('')
    if (newPassword !== confirmPassword) { setError('The new password and confirmation do not match.'); return }
    setSaving(true)
    try { await onChange(currentPassword, newPassword); setCurrentPassword(''); setNewPassword(''); setConfirmPassword(''); setMessage('Password changed. Other signed-in sessions have been signed out.') }
    catch (err) { setError(err instanceof Error ? err.message : 'Unable to change your password.') }
    finally { setSaving(false) }
  }
  return <><p className="eyebrow">ACCOUNT SECURITY</p><h1 className="mt-3 text-3xl font-semibold">Change password</h1><p className="mb-7 mt-3 max-w-2xl text-sm text-slate-500">Confirm your current password, then choose a new password with at least 12 characters, upper-case and lower-case letters, and a number.</p><section className="panel max-w-xl p-6"><form className="space-y-5" onSubmit={submit}><label className="block text-sm font-medium">Current password<input type="password" autoComplete="current-password" required value={currentPassword} onChange={event => setCurrentPassword(event.target.value)} /></label><label className="block text-sm font-medium">New password<input type="password" autoComplete="new-password" required value={newPassword} onChange={event => setNewPassword(event.target.value)} /></label><label className="block text-sm font-medium">Confirm new password<input type="password" autoComplete="new-password" required value={confirmPassword} onChange={event => setConfirmPassword(event.target.value)} /></label>{error && <p role="alert" className="text-sm text-red-700">{error}</p>}{message && <p role="status" className="text-sm text-teal-800">{message}</p>}<button className="action-button" disabled={saving}>{saving ? 'Changing password…' : 'Change password'}</button></form></section></>
}
