import { useRef, useState, useEffect, useCallback } from 'react'
import { Camera, Upload, StopCircle } from 'lucide-react'
import { detectFace, detectFaceBase64 } from '../services/api'

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
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [preview, setPreview] = useState(null)
  const [liveMode, setLiveMode] = useState(false)
  const [liveBusy, setLiveBusy] = useState(false)

  const startWebcam = async () => {
    setError('')
    try {
      const s = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
      setStream(s)
      if (videoRef.current) videoRef.current.srcObject = s
    } catch {
      setError('Camera access denied or unavailable. Use file upload instead.')
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
  }

  const captureFrameBase64 = () => {
    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas || video.videoWidth === 0) return null
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)
    return canvas.toDataURL('image/jpeg', 0.8)
  }

  const captureAndDetect = async () => {
    const b64 = captureFrameBase64()
    if (!b64) return
    setLoading(true)
    setError('')
    try {
      setPreview(b64)
      const data = await detectFaceBase64(b64)
      setResult(data)
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

  useEffect(() => () => {
    if (liveTimer.current) clearInterval(liveTimer.current)
    if (stream) stream.getTracks().forEach((t) => t.stop())
  }, [stream])

  const onFile = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setError('')
    setPreview(URL.createObjectURL(file))
    try {
      setResult(await detectFace(file))
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="page-title">Facial Emotion Recognition</h1>
      <p className="page-subtitle">Snapshot, continuous live detection, or image upload.</p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="grid-2">
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Input</h3>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
            {!stream ? (
              <button className="btn btn-primary" onClick={startWebcam}><Camera size={18} /> Start Webcam</button>
            ) : (
              <>
                <button className="btn btn-primary" onClick={captureAndDetect} disabled={loading}>
                  {loading ? 'Analysing…' : 'Capture once'}
                </button>
                <button className={`btn ${liveMode ? 'btn-danger' : 'btn-secondary'}`} onClick={toggleLive}>
                  {liveMode ? 'Stop live' : 'Start live (2.5s)'}
                </button>
                <button className="btn btn-danger" onClick={stopWebcam}><StopCircle size={18} /> Stop camera</button>
              </>
            )}
            <label className="btn btn-secondary">
              <Upload size={18} /> Upload Image
              <input type="file" accept="image/*" hidden onChange={onFile} />
            </label>
          </div>
          {liveMode && <div className="alert alert-info">Live mode: analysing about every 2.5 seconds.</div>}
          {stream && (
            <video ref={videoRef} autoPlay playsInline muted className="video-preview" style={{ width: '100%', maxHeight: 360 }} />
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
              <p>Faces detected: <strong>{result.faces_detected}</strong></p>
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
    </div>
  )
}
