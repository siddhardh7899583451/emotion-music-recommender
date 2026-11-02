import { useState } from 'react'
import { Heart, ThumbsUp, ThumbsDown, Play, ListPlus } from 'lucide-react'
import { addFavourite, removeFavourite, submitFeedback, listPlaylists, addSongToPlaylist } from '../services/api'
import { useAuth } from '../context/AuthContext'
import PlayerModal from './PlayerModal'

export default function SongCard({ song, showFav = true, onFeedback }) {
  const { isAuth } = useAuth()
  const [fav, setFav] = useState(false)
  const [msg, setMsg] = useState('')
  const [playing, setPlaying] = useState(false)
  const [playlists, setPlaylists] = useState(null)
  const [showPl, setShowPl] = useState(false)

  const doFav = async () => {
    if (!isAuth) {
      setMsg('Login to save favourites')
      return
    }
    try {
      if (fav) {
        await removeFavourite(song.id)
        setFav(false)
        setMsg('Removed from favourites')
      } else {
        await addFavourite(song.id)
        setFav(true)
        setMsg('Added to favourites')
      }
    } catch (e) {
      setMsg(e.response?.data?.detail || e.message)
    }
  }

  const doFeedback = async (type) => {
    try {
      await submitFeedback({
        song_id: song.id,
        feedback: type,
        session_id: localStorage.getItem('emr_session') || 'web-session',
      })
      setMsg(type === 'like' ? 'Thanks for the like' : 'We will avoid similar picks')
      onFeedback?.(song.id, type)
    } catch (e) {
      setMsg(e.response?.data?.detail || e.message)
    }
  }

  const openPlaylists = async () => {
    if (!isAuth) {
      setMsg('Login to add to a playlist')
      return
    }
    try {
      const data = await listPlaylists()
      setPlaylists(data)
      setShowPl(true)
    } catch (e) {
      setMsg(e.response?.data?.detail || e.message)
    }
  }

  const addToPl = async (playlistId) => {
    try {
      await addSongToPlaylist(playlistId, song.id)
      setMsg('Added to playlist')
      setShowPl(false)
    } catch (e) {
      setMsg(e.response?.data?.detail || e.message)
    }
  }

  const canPlay = !!(song.youtube_id || song.spotify_url)

  return (
    <div className="song-card">
      <div className="song-title">{song.title}</div>
      <div className="song-artist">{song.artist}{song.album ? ` · ${song.album}` : ''}</div>
      <div className="song-meta">
        {song.language && <span className="tag">{song.language}</span>}
        {song.mood && <span className="tag">{song.mood}</span>}
        {song.genre && <span className="tag">{song.genre}</span>}
        {song.energy != null && <span className="tag">⚡ {Math.round(song.energy * 100)}%</span>}
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap' }}>
        {canPlay && (
          <button className="btn btn-primary" style={{ fontSize: '0.8rem' }} onClick={() => setPlaying(true)}>
            <Play size={14} /> Play
          </button>
        )}
        {showFav && (
          <button className="btn btn-secondary" style={{ fontSize: '0.8rem' }} onClick={doFav}>
            <Heart size={14} fill={fav ? '#ff5c7a' : 'none'} /> Fav
          </button>
        )}
        <button className="btn btn-secondary" style={{ fontSize: '0.8rem' }} onClick={openPlaylists}>
          <ListPlus size={14} /> Playlist
        </button>
        <button className="btn btn-secondary" style={{ fontSize: '0.8rem' }} onClick={() => doFeedback('like')}>
          <ThumbsUp size={14} />
        </button>
        <button className="btn btn-secondary" style={{ fontSize: '0.8rem' }} onClick={() => doFeedback('dislike')}>
          <ThumbsDown size={14} />
        </button>
      </div>
      {showPl && playlists && (
        <div style={{ marginTop: 10, padding: 8, background: 'var(--bg)', borderRadius: 8 }}>
          <div style={{ fontSize: '0.85rem', marginBottom: 6, color: 'var(--text-muted)' }}>Add to playlist</div>
          {playlists.length === 0 && <div style={{ fontSize: '0.85rem' }}>No playlists — create one under Playlists.</div>}
          {playlists.map((pl) => (
            <button key={pl.id} className="btn btn-secondary" style={{ fontSize: '0.8rem', margin: 4 }} onClick={() => addToPl(pl.id)}>
              {pl.name}
            </button>
          ))}
          <button className="btn btn-secondary" style={{ fontSize: '0.8rem', margin: 4 }} onClick={() => setShowPl(false)}>Cancel</button>
        </div>
      )}
      {msg && <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 6 }}>{msg}</p>}
      {playing && <PlayerModal song={song} onClose={() => setPlaying(false)} />}
    </div>
  )
}
