export default function AboutPage() {
  return (
    <div>
      <h1 className="page-title">About this Project</h1>
      <p className="page-subtitle">AI-Based Multimodal Emotion Recognition and Personalized Music Recommendation System</p>

      <div className="card" style={{ marginBottom: '1.5rem', lineHeight: 1.7 }}>
        <h3 style={{ marginBottom: '0.75rem' }}>Purpose</h3>
        <p style={{ color: 'var(--text-muted)' }}>
          This application estimates a user's emotional state from facial expression, voice tone and written text,
          then recommends music that matches the detected mood and preferred language.
          It is a fully rebuilt, modern version of an earlier academic emotion-music project.
        </p>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem', lineHeight: 1.7 }}>
        <h3 style={{ marginBottom: '0.75rem' }}>Technology</h3>
        <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.25rem' }}>
          <li><strong>Backend:</strong> FastAPI, SQLAlchemy, SQLite, Pydantic</li>
          <li><strong>Frontend:</strong> React 18, Vite, React Router, Recharts</li>
          <li><strong>Face:</strong> OpenCV Haar cascades + feature heuristics / optional sklearn model</li>
          <li><strong>Audio:</strong> Librosa features + optional sklearn classifier</li>
          <li><strong>Text:</strong> Curated emotion lexicon (no large model download at runtime)</li>
          <li><strong>Fusion:</strong> Confidence-weighted multimodal voting</li>
          <li><strong>Music:</strong> Local curated catalogue with YouTube links</li>
        </ul>
      </div>

      <div className="card" style={{ lineHeight: 1.7 }}>
        <h3 style={{ marginBottom: '0.75rem' }}>Important disclaimer</h3>
        <p style={{ color: 'var(--text-muted)' }}>
          Emotion recognition is an imperfect prediction and should not be treated as a definitive measurement
          of a person's actual emotional state. Camera and microphone data are processed locally and are not
          stored unless you explicitly save history. Music links point to official platforms; no copyrighted
          audio is redistributed by this application.
        </p>
      </div>
    </div>
  )
}
