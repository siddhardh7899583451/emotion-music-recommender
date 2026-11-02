import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login as apiLogin, register as apiRegister } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      let data
      if (mode === 'login') {
        data = await apiLogin({ username, password })
      } else {
        data = await apiRegister({ username, email, password })
      }
      login(data.access_token, { id: data.user_id, username: data.username })
      navigate('/settings')
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 420 }}>
      <h1 className="page-title">{mode === 'login' ? 'Login' : 'Create account'}</h1>
      <p className="page-subtitle">Optional local accounts for favourites, playlists and preferences.</p>
      {error && <div className="alert alert-error">{String(error)}</div>}
      <form className="card" onSubmit={submit}>
        <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Username</label>
        <input className="input" value={username} onChange={(e) => setUsername(e.target.value)} required style={{ marginBottom: 12 }} />
        {mode === 'register' && (
          <>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Email</label>
            <input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required style={{ marginBottom: 12 }} />
          </>
        )}
        <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Password</label>
        <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} style={{ marginBottom: 16 }} />
        <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%' }}>
          {loading ? 'Please wait…' : mode === 'login' ? 'Login' : 'Register'}
        </button>
        <button
          type="button"
          className="btn btn-secondary"
          style={{ width: '100%', marginTop: 10 }}
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
        >
          {mode === 'login' ? 'Need an account? Register' : 'Have an account? Login'}
        </button>
      </form>
    </div>
  )
}
