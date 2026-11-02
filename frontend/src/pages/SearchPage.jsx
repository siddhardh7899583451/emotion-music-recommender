import { useState, useEffect } from 'react'
import { searchMusic, getFilters } from '../services/api'
import SongCard from '../components/SongCard'

export default function SearchPage() {
  const [q, setQ] = useState('')
  const [language, setLanguage] = useState('')
  const [mood, setMood] = useState('')
  const [songs, setSongs] = useState([])
  const [filters, setFilters] = useState({ languages: [], moods: [] })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getFilters().then(setFilters).catch(() => {})
  }, [])

  const run = async () => {
    setLoading(true)
    try {
      const data = await searchMusic({
        q,
        language: language || undefined,
        mood: mood || undefined,
        limit: 24,
      })
      setSongs(data)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="page-title">Search Music</h1>
      <p className="page-subtitle">Search the catalogue. Play in-app, favourite, or add to a playlist.</p>

      <div className="card" style={{ marginBottom: '1.5rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
        <input className="input" style={{ flex: 1, minWidth: 200 }} placeholder="Search title or artist…" value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && run()} />
        <select className="select" style={{ width: 150 }} value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="">All languages</option>
          {filters.languages.map((l) => <option key={l} value={l}>{l}</option>)}
        </select>
        <select className="select" style={{ width: 140 }} value={mood} onChange={(e) => setMood(e.target.value)}>
          <option value="">All moods</option>
          {filters.moods.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
        <button className="btn btn-primary" onClick={run} disabled={loading}>Search</button>
      </div>

      <div className="grid-3">
        {songs.map((s) => <SongCard key={s.id} song={s} />)}
      </div>
    </div>
  )
}
