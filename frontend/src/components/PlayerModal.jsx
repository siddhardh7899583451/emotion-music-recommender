import { X } from 'lucide-react'

/**
 * Official YouTube embed player (no scraping / no unofficial API).
 * Uses youtube-nocookie embed when youtube_id is present.
 */
export default function PlayerModal({ song, onClose }) {
  if (!song) return null
  const id = song.youtube_id
  return (
    <div
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.72)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 1000, padding: 16,
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{ width: 'min(900px, 100%)', padding: 16 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <div>
            <div style={{ fontWeight: 600 }}>{song.title}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{song.artist}</div>
          </div>
          <button className="btn btn-secondary" onClick={onClose}><X size={16} /></button>
        </div>
        {id ? (
          <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden', borderRadius: 10 }}>
            <iframe
              title={song.title}
              src={`https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`}
              style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0 }}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
        ) : song.spotify_url ? (
          <iframe
            title={song.title}
            src={song.spotify_url.replace('open.spotify.com/track/', 'open.spotify.com/embed/track/')}
            width="100%"
            height="152"
            frameBorder="0"
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
            style={{ borderRadius: 10 }}
          />
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>No embedded player available for this track.</p>
        )}
      </div>
    </div>
  )
}
