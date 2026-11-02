import { useState, useRef } from 'react'
import { Mic, Upload, Square } from 'lucide-react'
import { detectAudio } from '../services/api'

function EmotionBadge({ emotion, confidence }) {
  if (!emotion) return null
  return (
    <span className={`emotion-badge emotion-${emotion}`}>
      {emotion} {confidence != null && `(${(confidence * 100).toFixed(0)}%)`}
    </span>
  )
}

export default function AudioPage() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [recording, setRecording] = useState(false)
  const [audioUrl, setAudioUrl] = useState(null)
  const mediaRecorder = useRef(null)
  const chunks = useRef([])

  const startRecording = async () => {
    setError('')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mr = new MediaRecorder(stream)
      chunks.current = []
      mr.ondataavailable = (e) => chunks.current.push(e.data)
      mr.onstop = async () => {
        const blob = new Blob(chunks.current, { type: 'audio/webm' })
        setAudioUrl(URL.createObjectURL(blob))
        stream.getTracks().forEach(t => t.stop())
        // Convert to wav-ish by sending as webm; backend accepts via librosa
        const file = new File([blob], 'recording.webm', { type: 'audio/webm' })
        await analyse(file)
      }
      mediaRecorder.current = mr
      mr.start()
      setRecording(true)
    } catch (e) {
      setError('Microphone access denied or unavailable.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorder.current && recording) {
      mediaRecorder.current.stop()
      setRecording(false)
    }
  }

  const analyse = async (file) => {
    setLoading(true)
    setError('')
    try {
      const data = await detectAudio(file)
      setResult(data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const onFile = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      setAudioUrl(URL.createObjectURL(file))
      analyse(file)
    }
  }

  return (
    <div>
      <h1 className="page-title">Audio Emotion Recognition</h1>
      <p className="page-subtitle">Record from microphone or upload WAV / MP3. Features extracted with Librosa.</p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="grid-2">
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Input</h3>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
            {!recording ? (
              <button className="btn btn-primary" onClick={startRecording}><Mic size={18} /> Start Recording</button>
            ) : (
              <button className="btn btn-danger" onClick={stopRecording}><Square size={18} /> Stop & Analyse</button>
            )}
            <label className="btn btn-secondary">
              <Upload size={18} /> Upload Audio
              <input type="file" accept="audio/*,.wav,.mp3,.ogg,.flac" hidden onChange={onFile} />
            </label>
          </div>
          {recording && <div className="alert alert-info">Recording… speak clearly for a few seconds.</div>}
          {audioUrl && <audio controls src={audioUrl} style={{ width: '100%', marginTop: '0.5rem' }} />}
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Result</h3>
          {loading && <div className="loading">Extracting features & classifying…</div>}
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
    </div>
  )
}
