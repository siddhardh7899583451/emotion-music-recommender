import { useRef, useState, useEffect, useCallback } from 'react'
import { Camera, Upload, StopCircle } from 'lucide-react'
import { detectFace, detectFaceBase64, recommendMusic, saveHistory } from '../services/api'
import SongCard from '../components/SongCard'

function EmotionBadge({ emotion, confidence }) {
  if (!emotion) return null
  return (
    <span className={`emotion-badge emotion-${emotion}`}>
      {emotion} {confidence != null && `(${(confidence * 100).toFixed(0)}%)`}
    </span>
  )
}

export default function FacePage() {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const liveTimer = useRef(null)
  const [stream, setStream] = useState(null)
  const [result, setResult] = useState(null)
  const [songs, setSongs] = useState([])
  const [loading, setLoading] = useState(false)
  const [recLoading, setRecLoading] = useState(false)
  const [error, setError] = useState('')
  const [preview, setPreview] = useState(null)
  const [liveMode, setLiveMode] = useState(false)
  const [liveBusy, setLiveBusy] = useState(false)
  const [language, setLanguage] = useState('Any')

  const fetchRecommendations = async (emotion) => {
    if (!emotion) return
    setRecLoading(true)
    try {
      const rec = await recommendMusic({
        emotion,
        language: language === 'Any' ? null : language,
        limit: 6,
        session_id: localStorage.getItem('emr_session') || 'face-session',
      })
      setSongs(Array.isArray(rec) ? rec : [])
    } catch (e) {
      console.warn('Recommend failed', e)
      setSongs([])
    } finally {
      setRecLoading(false)
    }
  }

  const startWebcam = async () => {
    setError('')
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        setError('Camera API not available. Use HTTPS or localhost, or upload an image instead.')
        return
      }
      const s = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      })
      setStream(s)
      if (videoRef.current) {
        videoRef.current.srcObject = s
        // Critical: some browsers need an explicit play() after srcObject is set
        try {
          await videoRef.current.play()
        } catch (_) {
          /* autoplay policy — user gesture already occurred via button */
        }
      }
    } catch (err) {
      const name = err?.name || ''
      if (name === 'NotAllowedError' || name === 'PermissionDeniedError') {
        setError('Camera permission denied. Allow camera access in browser / Windows Privacy settings, then retry.')
      } else if (name === 'NotFoundError' || name === 'DevicesNotFoundError') {
        setError('No camera found. Connect a webcam or use image upload.')
      } else {
        setError(`Camera unavailable: ${err.message || name || 'unknown error'}. Use file upload instead.`)
      }
    }
  }

  const stopWebcam = () => {
    if (liveTimer.current) {
      clearInterval(liveTimer.current)
      liveTimer.current = null
    }
    setLiveMode(false)
    if (stream) {
      stream.getTracks().forEach((t) => t.stop())
      setStream(null)
    }
    if (videoRef.current) videoRef.current.srcObject = null
  }

  const captureFrameBase64 = () => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas) return null
    if (video.videoWidth === 0 || video.readyState < 2) return null
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0)
    return canvas.toDataURL('image/jpeg', 0.85)
  }

  const applyResult = async (data, autoRecommend = true) => {
    setResult(data)
    if (autoRecommend && data?.success && data.primary_emotion) {
      await fetchRecommendations(data.primary_emotion)
      try {
        await saveHistory({
          session_id: localStorage.getItem('emr_session') || 'face-session',
          face_emotion: data.primary_emotion,
          face_confidence: data.primary_confidence,
          fused_emotion: data.primary_emotion,
          fused_confidence: data.primary_confidence,
          modalities_used: 'face',
        })
      } catch (_) { /* optional */ }
    }
  }

  const captureAndDetect = async () => {
    const b64 = captureFrameBase64()
    if (!b64) {
      setError('Camera not ready yet. Wait a second after starting the webcam, then try again.')
      return
    }
    setLoading(true)
    setError('')
    setSongs([])
    try {
      setPreview(b64)
      const data = await detectFaceBase64(b64)
      await applyResult(data, true)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Detection failed')
    } finally {
      setLoading(false)
    }
  }

  const liveTick = useCallback(async () => {
    if (liveBusy) return
    const b64 = captureFrameBase64()
    if (!b64) return
    setLiveBusy(true)
    try {
      const data = await detectFaceBase64(b64)
      // Live mode: update emotion badge only; do not spam recommendations every tick
      setResult(data)
    } catch {
      /* ignore transient live errors */
    } finally {
      setLiveBusy(false)
    }
  }, [liveBusy])

  const toggleLive = () => {
    if (liveMode) {
      if (liveTimer.current) clearInterval(liveTimer.current)
      liveTimer.current = null
      setLiveMode(false)
      return
    }
    setLiveMode(true)
    liveTimer.current = setInterval(liveTick, 2500)
  }

  useEffect(() => {
    return () => {
      if (liveTimer.current) clearInterval(liveTimer.current)
      if (stream) stream.getTracks().forEach((t) => t.stop())
    }
  }, [stream])

  // Ensure video element picks up stream when ref mounts after setStream
  useEffect(() => {
    if (stream && videoRef.current && videoRef.current.srcObject !== stream) {
      videoRef.current.srcObject = stream
      videoRef.current.play().catch(() => {})
    }
  }, [stream])

  const onFile = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setError('')
    setSongs([])
    setPreview(URL.createObjectURL(file))
    try {
      const data = await detectFace(file)
      await applyResult(data, true)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const recommendFromCurrent = async () => {
    const emotion = result?.primary_emotion
    if (!emotion) {
      setError('Detect an emotion first (capture or upload).')
      return
    }
    await fetchRecommendations(emotion)
  }

  return (
    <div>
      <h1 className="page-title">Facial Emotion Recognition</h1>
      <p className="page-subtitle">
        Snapshot, continuous live detection, or image upload. After detection, music is recommended automatically.
      </p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="grid-2">
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Input</h3>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
            {!stream ? (
              <button className="btn btn-primary" onClick={startWebcam}>
                <Camera size={18} /> Start Webcam
              </button>
            ) : (
              <>
                <button className="btn btn-primary" onClick={captureAndDetect} disabled={loading}>
                  {loading ? 'Analysing…' : 'Capture & Recommend'}
                </button>
                <button className={`btn ${liveMode ? 'btn-danger' : 'btn-secondary'}`} onClick={toggleLive}>
                  {liveMode ? 'Stop live' : 'Start live (2.5s)'}
                </button>
                <button className="btn btn-danger" onClick={stopWebcam}>
                  <StopCircle size={18} /> Stop camera
                </button>
              </>
            )}
            <label className="btn btn-secondary">
              <Upload size={18} /> Upload Image
              <input type="file" accept="image/*" hidden onChange={onFile} />
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
            {result?.primary_emotion && (
              <button className="btn btn-secondary" onClick={recommendFromCurrent} disabled={recLoading}>
                {recLoading ? 'Loading…' : 'Refresh recommendations'}
              </button>
            )}
          </div>
          {liveMode && (
            <div className="alert alert-info">
              Live mode: analysing about every 2.5 seconds. Click &quot;Capture &amp; Recommend&quot; for music.
            </div>
          )}
          {stream && (
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="video-preview"
              style={{ width: '100%', maxHeight: 360, background: '#111', borderRadius: 8 }}
            />
          )}
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          {preview && !stream && (
            <img src={preview} alt="preview" className="image-preview" style={{ maxHeight: 360 }} />
          )}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Result</h3>
          {loading && <div className="loading">Processing…</div>}
          {result && (
            <>
              <p style={{ marginBottom: '0.75rem' }}>{result.message}</p>
              <p>
                Faces detected: <strong>{result.faces_detected}</strong>
              </p>
              {result.primary_emotion && (
                <div style={{ margin: '1rem 0' }}>
                  Primary: <EmotionBadge emotion={result.primary_emotion} confidence={result.primary_confidence} />
                </div>
              )}
              {result.annotated_image_base64 && (
                <img
                  src={`data:image/jpeg;base64,${result.annotated_image_base64}`}
                  alt="annotated"
                  className="image-preview"
                  style={{ marginTop: '1rem', maxHeight: 320 }}
                />
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
            {result?.primary_emotion ? (
              <span className={`emotion-badge emotion-${result.primary_emotion}`}>{result.primary_emotion}</span>
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
