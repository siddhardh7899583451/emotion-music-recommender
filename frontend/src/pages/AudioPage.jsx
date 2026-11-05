import { useState, useRef } from 'react'
import { Mic, Upload, Square } from 'lucide-react'
import { detectAudio, recommendMusic, saveHistory } from '../services/api'
import SongCard from '../components/SongCard'

function EmotionBadge({ emotion, confidence }) {
  if (!emotion) return null
  return (
    <span className={`emotion-badge emotion-${emotion}`}>
      {emotion} {confidence != null && `(${(confidence * 100).toFixed(0)}%)`}
    </span>
  )
}

function pickRecorderMime() {
  const candidates = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
    'audio/mp4',
  ]
  if (typeof MediaRecorder === 'undefined') return ''
  for (const t of candidates) {
    if (MediaRecorder.isTypeSupported?.(t)) return t
  }
  return ''
}

export default function AudioPage() {
  const [result, setResult] = useState(null)
  const [songs, setSongs] = useState([])
  const [loading, setLoading] = useState(false)
  const [recLoading, setRecLoading] = useState(false)
  const [error, setError] = useState('')
  const [recording, setRecording] = useState(false)
  const [audioUrl, setAudioUrl] = useState(null)
  const [language, setLanguage] = useState('Any')
  const mediaRecorder = useRef(null)
  const chunks = useRef([])
  const streamRef = useRef(null)

  const fetchRecommendations = async (emotion) => {
    if (!emotion) return
    setRecLoading(true)
    try {
      const rec = await recommendMusic({
        emotion,
        language: language === 'Any' ? null : language,
        limit: 6,
        session_id: localStorage.getItem('emr_session') || 'audio-session',
      })
      setSongs(Array.isArray(rec) ? rec : [])
    } catch (e) {
      console.warn('Recommend failed', e)
      setSongs([])
    } finally {
      setRecLoading(false)
    }
  }

  const analyse = async (file) => {
    setLoading(true)
    setError('')
    setSongs([])
    try {
      const data = await detectAudio(file)
      setResult(data)
      if (data?.success && data.prediction?.emotion) {
        await fetchRecommendations(data.prediction.emotion)
        try {
          await saveHistory({
            session_id: localStorage.getItem('emr_session') || 'audio-session',
            audio_emotion: data.prediction.emotion,
            audio_confidence: data.prediction.confidence,
            fused_emotion: data.prediction.emotion,
            fused_confidence: data.prediction.confidence,
            modalities_used: 'audio',
          })
        } catch (_) { /* optional */ }
      } else if (data && !data.success) {
        setError(data.message || 'Audio analysis failed')
      }
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const startRecording = async () => {
    setError('')
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        setError('Microphone API not available. Use HTTPS/localhost or upload an audio file.')
        return
      }
      if (typeof MediaRecorder === 'undefined') {
        setError('MediaRecorder not supported in this browser. Upload a WAV/MP3 file instead.')
        return
      }
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          channelCount: 1,
        },
      })
      streamRef.current = stream
      const mime = pickRecorderMime()
      const options = mime ? { mimeType: mime } : undefined
      let mr
      try {
        mr = new MediaRecorder(stream, options)
      } catch {
        mr = new MediaRecorder(stream)
      }
      chunks.current = []
      mr.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) chunks.current.push(e.data)
      }
      mr.onerror = () => {
        setError('Recording error. Try uploading a file instead.')
        setRecording(false)
      }
      mr.onstop = async () => {
        const blobType = mr.mimeType || mime || 'audio/webm'
        const blob = new Blob(chunks.current, { type: blobType })
        if (blob.size < 1000) {
          setError('Recording too short or empty. Speak for at least 1–2 seconds.')
          stream.getTracks().forEach((t) => t.stop())
          streamRef.current = null
          return
        }
        setAudioUrl(URL.createObjectURL(blob))
        stream.getTracks().forEach((t) => t.stop())
        streamRef.current = null
        // Prefer .webm extension so backend ALLOWED_AUDIO_EXTENSIONS matches
        const ext = blobType.includes('ogg') ? 'ogg' : blobType.includes('mp4') ? 'm4a' : 'webm'
        const file = new File([blob], `recording.${ext}`, { type: blobType })
        await analyse(file)
      }
      mediaRecorder.current = mr
      mr.start(250) // timeslice helps some browsers flush data
      setRecording(true)
    } catch (e) {
      const name = e?.name || ''
      if (name === 'NotAllowedError' || name === 'PermissionDeniedError') {
        setError('Microphone permission denied. Allow mic access in browser / Windows Privacy settings.')
      } else if (name === 'NotFoundError') {
        setError('No microphone found. Connect a mic or upload an audio file.')
      } else {
        setError(`Microphone unavailable: ${e.message || name}. Use file upload instead.`)
      }
    }
  }

  const stopRecording = () => {
    if (mediaRecorder.current && recording) {
      try {
        if (mediaRecorder.current.state !== 'inactive') {
          mediaRecorder.current.stop()
        }
      } catch (_) { /* ignore */ }
      setRecording(false)
    }
  }

  const onFile = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      setAudioUrl(URL.createObjectURL(file))
      analyse(file)
    }
  }

  const recommendFromCurrent = async () => {
    const emotion = result?.prediction?.emotion
    if (!emotion) {
      setError('Analyse audio first.')
      return
    }
    await fetchRecommendations(emotion)
  }

  return (
    <div>
      <h1 className="page-title">Audio Emotion Recognition</h1>
      <p className="page-subtitle">
        Record from microphone or upload WAV / MP3 / WebM. Features extracted with Librosa; music recommended automatically.
      </p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="grid-2">
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Input</h3>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
            {!recording ? (
              <button className="btn btn-primary" onClick={startRecording}>
                <Mic size={18} /> Start Recording
              </button>
            ) : (
              <button className="btn btn-danger" onClick={stopRecording}>
                <Square size={18} /> Stop &amp; Analyse
              </button>
            )}
            <label className="btn btn-secondary">
              <Upload size={18} /> Upload Audio
              <input type="file" accept="audio/*,.wav,.mp3,.ogg,.flac,.webm,.m4a" hidden onChange={onFile} />
            </label>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '1rem', alignItems: 'center' }}>
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
            {result?.prediction?.emotion && (
              <button className="btn btn-secondary" onClick={recommendFromCurrent} disabled={recLoading}>
                {recLoading ? 'Loading…' : 'Refresh recommendations'}
              </button>
            )}
          </div>
          {recording && (
            <div className="alert alert-info">Recording… speak clearly for at least 2–3 seconds, then stop.</div>
          )}
          {audioUrl && <audio controls src={audioUrl} style={{ width: '100%', marginTop: '0.5rem' }} />}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Result</h3>
          {loading && <div className="loading">Extracting features &amp; classifying…</div>}
          {result?.success && result.prediction && (
            <>
              <EmotionBadge emotion={result.prediction.emotion} confidence={result.prediction.confidence} />
              {result.duration_sec != null && (
                <p style={{ marginTop: '0.75rem', color: 'var(--text-muted)' }}>Duration: {result.duration_sec}s</p>
              )}
              {result.prediction.scores && (
                <div style={{ marginTop: '1rem' }}>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>All scores</p>
                  {Object.entries(result.prediction.scores)
                    .sort((a, b) => b[1] - a[1])
                    .map(([k, v]) => (
                      <div key={k} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginBottom: 4 }}>
                        <span style={{ textTransform: 'capitalize' }}>{k}</span>
                        <span>{(v * 100).toFixed(1)}%</span>
                      </div>
                    ))}
                </div>
              )}
            </>
          )}
          {result && !result.success && <div className="alert alert-error">{result.message}</div>}
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
        </div>
      )}
    </div>
  )
}
