import { useState } from 'react'
import { detectText } from '../services/api'

function EmotionBadge({ emotion, confidence }) {
  if (!emotion) return null
  return (
    <span className={`emotion-badge emotion-${emotion}`}>
      {emotion} {confidence != null && `(${(confidence * 100).toFixed(0)}%)`}
    </span>
  )
}

export default function TextPage() {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const analyse = async () => {
    if (!text.trim()) {
      setError('Please enter some text.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const data = await detectText(text)
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="page-title">Text Emotion Recognition</h1>
      <p className="page-subtitle">Enter any text. Emotion is scored with a curated lexicon (English + emojis).</p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="grid-2">
        <div className="card">
          <textarea
            className="input"
            rows={8}
            placeholder="How are you feeling today? Type anything…"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={analyse} disabled={loading}>
            {loading ? 'Analysing…' : 'Detect Emotion'}
          </button>
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Result</h3>
          {result?.success && result.prediction && (
            <>
              <EmotionBadge emotion={result.prediction.emotion} confidence={result.prediction.confidence} />
              {result.prediction.scores && (
                <div style={{ marginTop: '1.25rem' }}>
                  {Object.entries(result.prediction.scores)
                    .sort((a, b) => b[1] - a[1])
                    .map(([k, v]) => (
                      <div key={k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                        <span style={{ textTransform: 'capitalize' }}>{k}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, width: '60%' }}>
                          <div style={{ flex: 1, height: 6, background: 'var(--bg)', borderRadius: 3 }}>
                            <div style={{ width: `${v * 100}%`, height: '100%', background: 'var(--primary)', borderRadius: 3 }} />
                          </div>
                          <span style={{ fontSize: '0.85rem', width: 42 }}>{(v * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </>
          )}
          {!result && !loading && <p style={{ color: 'var(--text-muted)' }}>Results will appear here.</p>}
        </div>
      </div>
    </div>
  )
}
