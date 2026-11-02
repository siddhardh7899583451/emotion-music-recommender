import { useState, useEffect } from 'react'
import { getAnalytics, getHistory } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null)
  const [history, setHistory] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([getAnalytics(30), getHistory({ limit: 20 })])
      .then(([a, h]) => {
        setAnalytics(a)
        setHistory(h)
      })
      .catch(e => setError('Could not load analytics. Is the backend running?'))
  }, [])

  const chartData = analytics
    ? Object.entries(analytics.emotion_distribution || {}).map(([name, count]) => ({ name, count }))
    : []

  return (
    <div>
      <h1 className="page-title">Emotion Analytics</h1>
      <p className="page-subtitle">History of fused emotions stored in the local SQLite database.</p>
      {error && <div className="alert alert-error">{error}</div>}

      {analytics && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>Last {analytics.period_days} days</h3>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Total detections: <strong>{analytics.total_detections}</strong>
          </p>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2e2e42" />
                <XAxis dataKey="name" stroke="#9898b0" />
                <YAxis stroke="#9898b0" allowDecimals={false} />
                <Tooltip contentStyle={{ background: '#1a1a24', border: '1px solid #2e2e42' }} />
                <Bar dataKey="count" fill="#7c5cfc" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: 'var(--text-muted)' }}>No data yet. Run multimodal fusion to record history.</p>
          )}
        </div>
      )}

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>Recent detections</h3>
        {history.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No history yet.</p>}
        {history.map(h => (
          <div key={h.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: '1px solid var(--border)', fontSize: '0.95rem' }}>
            <span className={`emotion-badge emotion-${h.fused_emotion}`}>{h.fused_emotion}</span>
            <span style={{ color: 'var(--text-muted)' }}>{h.modalities_used}</span>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              {new Date(h.created_at).toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
