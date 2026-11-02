# AI-Based Multimodal Emotion Recognition and Personalized Music Recommendation System

A **brand-new, clean, modern** rebuild of an academic emotion-based music recommendation project.

**Do not confuse this with the original broken Flask + TensorFlow 2.13 project.**  
This repository is independent, modular, and designed to install and run on **Windows 10/11** with CPU only.

---

## Features

| Module | Capability |
|--------|------------|
| **Facial emotion** | Webcam capture or image upload, OpenCV face detection, bounding boxes, confidence scores |
| **Audio emotion** | Microphone recording or WAV/MP3 upload, Librosa features (MFCC, chroma, ZCR, RMS…), classification |
| **Text emotion** | Free-text input, curated emotion lexicon + emoji handling (no large model download at runtime) |
| **Multimodal fusion** | Confidence-weighted voting across any subset of modalities; missing modalities handled correctly |
| **Music recommendations** | Emotion + language + energy matching from a curated local catalogue (English, Hindi, Telugu, Tamil, Kannada…) |
| **Search** | Title / artist / mood / language search |
| **Analytics** | Emotion history stored in SQLite, distribution charts |
| **API** | FastAPI with interactive docs at `/docs` |
| **UI** | Modern React + Vite dark theme, responsive layout |

All three emotion modules work **independently** and together. Core functionality does **not** require an internet connection (except optional YouTube links).

---

## Technology stack

- **Backend:** Python 3.10–3.12, FastAPI, Uvicorn, SQLAlchemy 2, SQLite, Pydantic v2  
- **Frontend:** React 18, Vite 5, React Router, Recharts, Lucide icons  
- **ML:** OpenCV (headless), Librosa, NumPy, scikit-learn, NLTK/TextBlob (lightweight)  
- **No Docker, no CUDA, no paid APIs required for core features**

### Why FastAPI instead of Flask?

- Native async support and high performance  
- Automatic OpenAPI docs (`/docs`)  
- First-class Pydantic validation  
- Cleaner modular routing for a multi-service architecture  

---

## Project structure

```
emotion-music-recommender/
├── backend/
│   ├── app/
│   │   ├── api/           # emotion, music, history routes
│   │   ├── core/          # config
│   │   ├── database/      # SQLAlchemy models & session
│   │   ├── schemas/       # Pydantic models
│   │   ├── services/      # face / audio / text / fusion / music
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/pages/ …
│   ├── src/services/api.js
│   └── package.json
├── data/music_catalogue/songs.json
├── ml/models/             # optional trained joblib models
├── scripts/               # Windows .bat helpers
├── docs/
├── README.md
└── START_HERE.md
```

---

## Windows 10/11 installation (exact steps)

### Prerequisites

1. **Python 3.10, 3.11 or 3.12** (recommended 3.12) from https://www.python.org  
   - During install, check **“Add Python to PATH”**.
2. **Node.js 18+** from https://nodejs.org (LTS).
3. Optional: Git.

### Option A – Automated setup

```bat
cd path\to\emotion-music-recommender
scripts\setup_windows.bat
```

### Option B – Manual commands (Command Prompt or PowerShell)

```bat
cd path\to\emotion-music-recommender

:: 1. Backend venv
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
cd ..

:: 2. Frontend
cd frontend
npm install
cd ..
```

### Start the application (two terminals)

**Terminal 1 – Backend**

```bat
cd path\to\emotion-music-recommender\backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Or double-click `scripts\start_backend.bat`.

**Terminal 2 – Frontend**

```bat
cd path\to\emotion-music-recommender\frontend
npm run dev
```

Or double-click `scripts\start_frontend.bat`.

Open **http://localhost:5173** in your browser.  
API documentation: **http://127.0.0.1:8000/docs**

---

## Running tests

```bat
cd backend
venv\Scripts\activate
pytest tests -v
```

---

## Model notes

| Modality | Default behaviour | Optional trained model |
|----------|-------------------|------------------------|
| Face | OpenCV Haar + statistical heuristic | Place `ml/models/face/emotion_model.joblib` (sklearn) |
| Audio | Librosa features + heuristic | Place `ml/models/audio/emotion_model.joblib` |
| Text | Built-in lexicon (no file needed) | — |

The original project’s `.h5` Keras models (TF 2.13 / Keras 2.x) are **not** loaded by default because of known compatibility and architecture issues with modern TensorFlow/Keras.  
Heuristic modes are deterministic, provide confidence scores, and keep the app fully usable out of the box. Training scripts can be added under `ml/training/` if you wish to replace the heuristics with your own classifiers.

---

## API overview

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/emotion/face` | Image file or base64 → face emotions |
| POST | `/api/v1/emotion/audio` | Audio file → emotion |
| POST | `/api/v1/emotion/text` | `{ "text": "..." }` → emotion |
| POST | `/api/v1/emotion/multimodal` | Fuse any combination of modality results |
| POST | `/api/v1/music/recommend` | Emotion (+ language) → songs |
| GET | `/api/v1/music/search` | Search catalogue |
| GET | `/api/v1/music/filters` | Languages, genres, moods |
| POST/GET | `/api/v1/history` | Save / list emotion history |
| GET | `/api/v1/history/analytics` | Distribution stats |

---

## Common Windows issues

| Problem | Solution |
|---------|----------|
| `python` not found | Reinstall Python and tick “Add to PATH”, or use `py -3.12` |
| `npm` not found | Install Node.js LTS and restart the terminal |
| Camera / mic permission | Allow access in Windows Settings → Privacy |
| Port 8000 or 5173 in use | Change port in the start command (`--port 8001`) |
| `librosa` / `soundfile` install fails | Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) |
| Antivirus blocks venv | Add project folder to exclusions |

---

## Privacy

- Camera and microphone are used only when you start them and can be stopped at any time.  
- Uploaded files are processed in memory / temporary files and cleaned up.  
- Emotion history is stored only in the local SQLite database if you use the multimodal “Fuse” action.  
- No audio or video is sent to external servers by the core application.

---

## Disclaimer

Emotion labels produced by this system are **predictions**, not clinical or psychological diagnoses.  
Music links open official platforms (YouTube). No copyrighted audio files are redistributed.

---



## New features (v1.1)

- **Auth:** register / login / JWT (`/api/v1/auth/*`)
- **Favourites:** save/remove songs (requires login)
- **Playlists:** create, list, delete, add songs
- **Feedback:** like/dislike recommendations (session or user)
- **Settings:** modality weights, preferred language, dark/light theme toggle
- **Continuous webcam:** Face page live mode (~2.5s interval)
- **Training scripts:** `ml/training/train_face_model.py`, `train_audio_model.py`



## Models (v1.2)

Bundled trained classifiers (sklearn GradientBoosting pipelines):

- `ml/models/face/emotion_model.joblib`
- `ml/models/audio/emotion_model.joblib`

They load automatically at backend startup when present.

To retrain on **your own FER / RAVDESS-style data**:

```bat
:: 1) Arrange images/audio under label folders (angry, happy, ...)
:: 2) Extract features
python ml\training\prepare_features_from_images.py C:\data\fer_images
python ml\training\prepare_features_from_audio.py C:\data\ravdess_wavs

:: 3) Train
python ml\training\train_face_model.py --from-csv ml\datasets\face_features.csv
python ml\training\train_audio_model.py --from-csv ml\datasets\audio_features.csv
```

In-app music playback uses the **official YouTube embed** (`youtube-nocookie.com`) or Spotify embed when a Spotify URL exists — no unofficial scraping.

## License

This educational project is provided as-is for learning and demonstration purposes.
