import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listFavourites, removeFavourite } from '../services/api'
import { useAuth } from '../context/AuthContext'
import SongCard from '../components/SongCard'

export default function FavouritesPage() {
  const { isAuth } = useAuth()
  const [items, setItems] = useState([])
  const [error, setError] = useState('')

  const load = () => {
    if (!isAuth) return
    listFavourites()
      .then((data) => setItems(data))
      .catch((e) => setError(e.response?.data?.detail || e.message))
  }

  useEffect(load, [isAuth])

  if (!isAuth) {
    return (
      <div>
        <h1 className="page-title">Favourites</h1>
        <div className="alert alert-info">
          Please <Link to="/login">login</Link> to manage favourite songs.
        </div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="page-title">Favourite Songs</h1>
      <p className="page-subtitle">Songs you saved for later.</p>
      {error && <div className="alert alert-error">{error}</div>}
      {items.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No favourites yet. Use the heart button on recommendations.</p>}
      <div className="grid-3">
        {items.map((f) => (
          <div key={f.id}>
            <SongCard song={f.song} showFav={false} />
            <button
              className="btn btn-danger"
              style={{ marginTop: 8, fontSize: '0.85rem' }}
              onClick={async () => {
                await removeFavourite(f.song_id)
                load()
              }}
            >
              Remove
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
