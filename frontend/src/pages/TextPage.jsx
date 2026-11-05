import { useState } from 'react'
import { detectText, recommendMusic, saveHistory } from '../services/api'
import SongCard from '../components/SongCard'

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
  const [songs, setSongs] = useState([])
  const [loading, setLoading] = useState(false)
  const [recLoading, setRecLoading] = useState(false)
  const [error, setError] = useState('')
  const [language, setLanguage] = useState('Any')

  const fetchRecommendations = async (emotion) => {
    if (!emotion) return
    setRecLoading(true)
    try {
      const rec = await recommendMusic({
        emotion,
        language: language === 'Any' ? null : language,
        limit: 6,
        session_id: localStorage.getItem('emr_session') || 'text-session',
      })
      setSongs(Array.isArray(rec) ? rec : [])
    } catch (e) {
      console.warn('Recommend failed', e)
      setSongs([])
    } finally {
      setRecLoading(false)
    }
  }

  const analyse = async () => {
    if (!text.trim()) {
      setError('Please enter some text.')
      return
    }
    setLoading(true)
    setError('')
    setSongs([])
    try {
      const data = await detectText(text)
      setResult(data)
      if (data?.success && data.prediction?.emotion) {
        await fetchRecommendations(data.prediction.emotion)
        try {
          await saveHistory({
            session_id: localStorage.getItem('emr_session') || 'text-session',
            text_emotion: data.prediction.emotion,
            text_confidence: data.prediction.confidence,
            fused_emotion: data.prediction.emotion,
            fused_confidence: data.prediction.confidence,
            modalities_used: 'text',
          })
        } catch (_) { /* history optional */ }
      }
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="page-title">Text Emotion Recognition</h1>
      <p className="page-subtitle">
        Enter any text. Emotion is scored with a curated lexicon (English + emojis), then music is recommended automatically.
      </p>
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
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <select
              className="select"
              style={{ width: 160 }}
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              {['Any', 'English', 'Hindi', 'Telugu', 'Tamil', 'Kannada'].map((l) => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
            <button className="btn btn-primary" onClick={analyse} disabled={loading}>
              {loading ? 'Analysing…' : 'Detect Emotion & Recommend'}
            </button>
          </div>
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

      {(recLoading || songs.length > 0) && (
        <div style={{ marginTop: '1.5rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>
            Recommended for{' '}
            {result?.prediction?.emotion ? (
              <span className={`emotion-badge emotion-${result.prediction.emotion}`}>
                {result.prediction.emotion}
              </span>
            ) : (
              'your mood'
            )}
          </h2>
          {recLoading && <div className="loading">Finding songs…</div>}
          <div className="grid-3">
            {songs.map((s) => (
              <SongCard key={s.id} song={s} />
            ))}
          </div>
          {!recLoading && songs.length === 0 && (
            <p style={{ color: 'var(--text-muted)' }}>No matching songs found. Try another language or emotion.</p>
          )}
        </div>
      )}
    </div>
  )
}
