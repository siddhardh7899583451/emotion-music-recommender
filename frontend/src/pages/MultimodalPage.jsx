import { useState } from 'react'
import { fuseEmotions, recommendMusic, saveHistory } from '../services/api'
import { Link } from 'react-router-dom'
import SongCard from '../components/SongCard'

const EMOTIONS = ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']

function EmotionBadge({ emotion, confidence }) {
  if (!emotion) return null
  return (
    <span className={`emotion-badge emotion-${emotion}`}>
      {emotion} {confidence != null && `(${(confidence * 100).toFixed(0)}%)`}
    </span>
  )
}

export default function MultimodalPage() {
  const [face, setFace] = useState({ emotion: '', confidence: 0.8 })
  const [audio, setAudio] = useState({ emotion: '', confidence: 0.7 })
  const [text, setText] = useState({ emotion: '', confidence: 0.75 })
  const [fusion, setFusion] = useState(null)
  const [songs, setSongs] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [language, setLanguage] = useState('Any')

  const run = async () => {
    setLoading(true)
    setError('')
    setSongs([])
    try {
      const payload = {}
      if (face.emotion) {
        payload.face_emotion = face.emotion
        payload.face_confidence = Number(face.confidence)
      }
      if (audio.emotion) {
        payload.audio_emotion = audio.emotion
        payload.audio_confidence = Number(audio.confidence)
      }
      if (text.emotion) {
        payload.text_emotion = text.emotion
        payload.text_confidence = Number(text.confidence)
      }
      if (!payload.face_emotion && !payload.audio_emotion && !payload.text_emotion) {
        setError('Select at least one modality emotion.')
        setLoading(false)
        return
      }
      const res = await fuseEmotions(payload)
      setFusion(res)
      if (res.success) {
        const rec = await recommendMusic({
          emotion: res.fused_emotion,
          language: language === 'Any' ? null : language,
          limit: 6,
          session_id: 'demo-session',
        })
        setSongs(rec)
        try {
          await saveHistory({
            session_id: 'demo-session',
            face_emotion: payload.face_emotion,
            face_confidence: payload.face_confidence,
            audio_emotion: payload.audio_emotion,
            audio_confidence: payload.audio_confidence,
            text_emotion: payload.text_emotion,
            text_confidence: payload.text_confidence,
            fused_emotion: res.fused_emotion,
            fused_confidence: res.fused_confidence,
            modalities_used: res.modalities_used.join(','),
          })
        } catch (_) { /* history optional */ }
      }
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  const ModalityCard = ({ title, state, setState }) => (
    <div className="card">
      <h3 style={{ marginBottom: '0.75rem' }}>{title}</h3>
      <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Emotion</label>
      <select
        className="select"
        value={state.emotion}
        onChange={(e) => setState({ ...state, emotion: e.target.value })}
        style={{ marginBottom: '0.75rem' }}
      >
        <option value="">— Skip —</option>
        {EMOTIONS.map(e => <option key={e} value={e}>{e}</option>)}
      </select>
      <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Confidence: {(state.confidence * 100).toFixed(0)}%</label>
      <input
        type="range" min="0.1" max="1" step="0.05"
        value={state.confidence}
        onChange={(e) => setState({ ...state, confidence: Number(e.target.value) })}
        style={{ width: '100%' }}
      />
    </div>
  )

  return (
    <div>
      <h1 className="page-title">Multimodal Emotion Fusion</h1>
      <p className="page-subtitle">
        Combine face, audio and text predictions. You can also paste results from the individual pages or choose values manually.
      </p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
        <ModalityCard title="Face" state={face} setState={setFace} />
        <ModalityCard title="Audio" state={audio} setState={setAudio} />
        <ModalityCard title="Text" state={text} setState={setText} />
      </div>

      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <select className="select" style={{ width: 180 }} value={language} onChange={e => setLanguage(e.target.value)}>
          {['Any', 'English', 'Hindi', 'Telugu', 'Tamil', 'Kannada'].map(l => (
            <option key={l} value={l}>{l}</option>
          ))}
        </select>
        <button className="btn btn-primary" onClick={run} disabled={loading}>
          {loading ? 'Fusing…' : 'Fuse & Recommend Music'}
        </button>
        <Link to="/face" className="btn btn-secondary">Run face first</Link>
        <Link to="/audio" className="btn btn-secondary">Run audio first</Link>
        <Link to="/text" className="btn btn-secondary">Run text first</Link>
      </div>

      {fusion?.success && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ marginBottom: '0.75rem' }}>Fused Result</h3>
          <EmotionBadge emotion={fusion.fused_emotion} confidence={fusion.fused_confidence} />
          <p style={{ marginTop: '0.75rem', color: 'var(--text-muted)', fontSize: '0.95rem' }}>{fusion.explanation}</p>
          <p style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>
            Modalities used: {fusion.modalities_used.join(', ')}
          </p>
        </div>
      )}

      {songs.length > 0 && (
        <div>
          <h3 style={{ marginBottom: '1rem' }}>Recommended Songs</h3>
          <div className="grid-3">
            {songs.map(s => (
              <SongCard key={s.id} song={s} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
