import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getSettings, updateSettings } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function SettingsPage() {
  const { isAuth, theme, toggleTheme, logout, user } = useAuth()
  const [prefs, setPrefs] = useState(null)
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!isAuth) return
    getSettings()
      .then(setPrefs)
      .catch((e) => setError(e.response?.data?.detail || e.message))
  }, [isAuth])

  const save = async () => {
    try {
      const updated = await updateSettings(prefs)
      setPrefs(updated)
      setMsg('Preferences saved')
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    }
  }

  return (
    <div>
      <h1 className="page-title">Settings</h1>
      <p className="page-subtitle">Theme, modality weights and account preferences.</p>
      {error && <div className="alert alert-error">{error}</div>}
      {msg && <div className="alert alert-success">{msg}</div>}

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ marginBottom: 12 }}>Appearance</h3>
        <button className="btn btn-secondary" onClick={toggleTheme}>
          Switch to {theme === 'dark' ? 'light' : 'dark'} mode
        </button>
        <p style={{ marginTop: 8, color: 'var(--text-muted)', fontSize: '0.9rem' }}>Current: {theme}</p>
      </div>

      {!isAuth ? (
        <div className="alert alert-info">
          <Link to="/login">Login</Link> to sync modality weights and language preferences to your account.
        </div>
      ) : (
        <>
          <div className="card" style={{ marginBottom: 16 }}>
            <h3 style={{ marginBottom: 8 }}>Account</h3>
            <p style={{ color: 'var(--text-muted)' }}>Signed in as <strong>{user?.username}</strong></p>
            <button className="btn btn-danger" style={{ marginTop: 12 }} onClick={logout}>Logout</button>
          </div>

          {prefs && (
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>Fusion weights</h3>
              {['face_weight', 'audio_weight', 'text_weight'].map((key) => (
                <div key={key} style={{ marginBottom: 12 }}>
                  <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    {key.replace('_', ' ')}: {Number(prefs[key]).toFixed(2)}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={prefs[key]}
                    onChange={(e) => setPrefs({ ...prefs, [key]: Number(e.target.value) })}
                    style={{ width: '100%' }}
                  />
                </div>
              ))}
              <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Preferred language</label>
              <select
                className="select"
                value={prefs.preferred_language || 'Any'}
                onChange={(e) => setPrefs({ ...prefs, preferred_language: e.target.value })}
                style={{ marginBottom: 16 }}
              >
                {['Any', 'English', 'Hindi', 'Telugu', 'Tamil', 'Kannada'].map((l) => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
                <input
                  type="checkbox"
                  checked={!!prefs.auto_recommend}
                  onChange={(e) => setPrefs({ ...prefs, auto_recommend: e.target.checked })}
                />
                Auto-recommend after multimodal fusion
              </label>
              <button className="btn btn-primary" onClick={save}>Save preferences</button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
