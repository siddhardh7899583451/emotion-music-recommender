import { useState } from 'react'
import { recommendMusic } from '../services/api'
import SongCard from '../components/SongCard'

const EMOTIONS = ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral', 'energetic', 'calm', 'motivational']
const LANGUAGES = ['Any', 'English', 'Hindi', 'Telugu', 'Tamil', 'Kannada', 'Instrumental']

export default function MusicPage() {
  const [emotion, setEmotion] = useState('happy')
  const [language, setLanguage] = useState('Any')
  const [songs, setSongs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await recommendMusic({
        emotion,
        language: language === 'Any' ? null : language,
        limit: 9,
        session_id: localStorage.getItem('emr_session') || 'music-page',
      })
      setSongs(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="page-title">Music Recommendations</h1>
      <p className="page-subtitle">Emotion and language aware recommendations. Use 👍/👎 to refine.</p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card" style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
        <div>
          <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Emotion / Mood</label>
          <select className="select" value={emotion} onChange={(e) => setEmotion(e.target.value)} style={{ width: 180 }}>
            {EMOTIONS.map((e) => <option key={e} value={e}>{e}</option>)}
          </select>
        </div>
        <div>
          <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Language</label>
          <select className="select" value={language} onChange={(e) => setLanguage(e.target.value)} style={{ width: 160 }}>
            {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
        <button className="btn btn-primary" onClick={run} disabled={loading}>
          {loading ? 'Loading…' : 'Get Recommendations'}
        </button>
      </div>

      <div className="grid-3">
        {songs.map((s) => <SongCard key={s.id} song={s} />)}
      </div>
      {songs.length === 0 && !loading && (
        <p style={{ color: 'var(--text-muted)' }}>Choose an emotion and click Get Recommendations.</p>
      )}
    </div>
  )
}
