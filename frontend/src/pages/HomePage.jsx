import { Link } from 'react-router-dom'
import { Camera, Mic, Type, Layers, Music } from 'lucide-react'

export default function HomePage() {
  return (
    <div>
      <h1 className="page-title">AI Multimodal Emotion Music</h1>
      <p className="page-subtitle">
        Detect emotion from face, voice and text — then get personalised music recommendations.
      </p>

      <div className="card" style={{ marginBottom: '1.5rem', background: 'linear-gradient(135deg,#1a1530,#222244)' }}>
        <h2 style={{ marginBottom: '0.75rem' }}>How it works</h2>
        <ol style={{ color: 'var(--text-muted)', lineHeight: 1.8, paddingLeft: '1.25rem' }}>
          <li>Capture your face with a webcam or upload an image — music is recommended automatically</li>
          <li>Record or upload a short voice clip — music is recommended automatically</li>
          <li>Type how you feel (or any text) — music is recommended automatically</li>
          <li>Or fuse face + voice + text on the Multimodal page for a combined emotion</li>
          <li>Play songs in-app via YouTube / Spotify embeds; save favourites when logged in</li>
        </ol>
        <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          All processing runs locally. No paid APIs required for core features.
        </p>
      </div>

      <div className="grid-3">
        {[
          { to: '/face', icon: Camera, title: 'Face Emotion', desc: 'Webcam or image upload with bounding boxes' },
          { to: '/audio', icon: Mic, title: 'Audio Emotion', desc: 'WAV / MP3 analysis with Librosa features' },
          { to: '/text', icon: Type, title: 'Text Emotion', desc: 'Lexicon-based emotion from free text' },
          { to: '/multimodal', icon: Layers, title: 'Multimodal Fusion', desc: 'Confidence-weighted combination of all inputs' },
          { to: '/music', icon: Music, title: 'Recommendations', desc: 'Mood, language and energy-aware song suggestions' },
        ].map(({ to, icon: Icon, title, desc }) => (
          <Link key={to} to={to} className="card" style={{ display: 'block', transition: 'border-color 0.15s' }}>
            <Icon size={28} color="#7c5cfc" style={{ marginBottom: '0.75rem' }} />
            <h3 style={{ marginBottom: '0.4rem' }}>{title}</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{desc}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
