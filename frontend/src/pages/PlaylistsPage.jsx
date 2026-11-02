import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listPlaylists, createPlaylist, deletePlaylist } from '../services/api'
import { useAuth } from '../context/AuthContext'
import SongCard from '../components/SongCard'

export default function PlaylistsPage() {
  const { isAuth } = useAuth()
  const [items, setItems] = useState([])
  const [name, setName] = useState('')
  const [mood, setMood] = useState('')
  const [error, setError] = useState('')

  const load = () => {
    if (!isAuth) return
    listPlaylists()
      .then(setItems)
      .catch((e) => setError(e.response?.data?.detail || e.message))
  }

  useEffect(load, [isAuth])

  const create = async (e) => {
    e.preventDefault()
    try {
      await createPlaylist({ name, mood: mood || null })
      setName('')
      setMood('')
      load()
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    }
  }

  if (!isAuth) {
    return (
      <div>
        <h1 className="page-title">Playlists</h1>
        <div className="alert alert-info">
          Please <Link to="/login">login</Link> to create playlists.
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="page-title">Playlists</h1>
      <p className="page-subtitle">Create mood-based playlists from the catalogue.</p>
      {error && <div className="alert alert-error">{error}</div>}

      <form className="card" onSubmit={create} style={{ marginBottom: 24, display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'end' }}>
        <div style={{ flex: 1, minWidth: 160 }}>
          <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Name</label>
          <input className="input" value={name} onChange={(e) => setName(e.target.value)} required />
        </div>
        <div style={{ width: 160 }}>
          <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Mood (optional)</label>
          <input className="input" value={mood} onChange={(e) => setMood(e.target.value)} placeholder="happy, calm…" />
        </div>
        <button className="btn btn-primary" type="submit">Create</button>
      </form>

      {items.map((pl) => (
        <div key={pl.id} className="card" style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <div>
              <h3>{pl.name}</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                {pl.mood || 'No mood'} · {pl.song_count} songs
              </p>
            </div>
            <button className="btn btn-danger" onClick={async () => { await deletePlaylist(pl.id); load() }}>Delete</button>
          </div>
          <div className="grid-3">
            {pl.songs.map((s) => <SongCard key={s.id} song={s} />)}
          </div>
          {pl.songs.length === 0 && (
            <p style={{ color: 'var(--text-muted)' }}>Empty — add songs from Music / Search after selecting a playlist in a future update, or use API.</p>
          )}
        </div>
      ))}
    </div>
  )
}
