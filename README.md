# AI-Based Multimodal Emotion Recognition and Personalized Music Recommendation System

Detect emotion from **face**, **voice**, and **text**, fuse the results, and get **personalized music recommendations**.

**Repository:** https://github.com/siddhardh7899583451/emotion-music-recommender

Modern rebuild for **Windows 10/11**, CPU-only. Independent of the old Flask + TensorFlow 2.13 project.

---

## Features

| Module | Capability |
|--------|------------|
| **Facial emotion** | Webcam (snapshot + live ~2.5s), image upload, OpenCV + trained model, bounding boxes |
| **Audio emotion** | Microphone or WAV/MP3/WebM upload, Librosa features + trained model |
| **Text emotion** | Free-text lexicon scoring (English + emojis) |
| **Multimodal fusion** | Confidence-weighted voting; works with 1, 2, or 3 modalities |
| **Music recommendations** | Emotion + language + energy matching (English, Hindi, Telugu, Tamil, Kannada, …) |
| **Search** | Title / artist / mood / language search |
| **In-app playback** | Official YouTube embed / Spotify embed |
| **Favourites & playlists** | Save songs, create playlists, add from Search/Recommendations (login) |
| **Like / dislike feedback** | Session-aware recommendation refinement |
| **Auth & settings** | Register/login (JWT), modality weights, preferred language, dark/light theme |
| **Analytics** | Emotion history in SQLite, distribution charts |
| **API** | FastAPI with interactive docs at `/docs` |

All three emotion modules work **independently** and together.

---

## Technology stack

- **Backend:** Python **3.12**, FastAPI, Uvicorn, SQLAlchemy 2, SQLite, Pydantic v2
- **Frontend:** React 18, Vite 5, React Router, Recharts, Lucide icons
- **ML:** OpenCV (headless), Librosa, NumPy, scikit-learn
- **Models:** Bundled `ml/models/face/emotion_model.joblib` and `ml/models/audio/emotion_model.joblib`
- **No Docker, no CUDA, no paid APIs** required for core features

### Why FastAPI instead of Flask?

- Native async support and high performance
- Automatic OpenAPI docs (`/docs`)
- First-class Pydantic validation
- Clean modular routing

---

## Requirements

| Software | Version |
|----------|---------|
| **Python** | **3.12** (required for reliable installs; avoid 3.13+) |
| **Node.js** | 18+ (LTS or current) |
| **Git** | Optional |

---

## Project structure

```text
emotion-music-recommender/
├── backend/
│   ├── app/
│   │   ├── api/           # auth, emotion, music, history, favourites, playlists, feedback, settings
│   │   ├── core/          # config, security
│   │   ├── database/      # SQLAlchemy models & session
│   │   ├── schemas/
│   │   ├── services/      # face / audio / text / fusion / music
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/pages/
│   ├── src/components/    # SongCard, PlayerModal
│   ├── src/context/       # Auth + theme
│   └── package.json
├── data/music_catalogue/songs.json
├── ml/
│   ├── models/face/       # emotion_model.joblib
│   ├── models/audio/      # emotion_model.joblib
│   └── training/          # train + prepare feature scripts
├── scripts/
│   ├── start_all.bat      # ★ single switch: backend + frontend
│   ├── start_backend.bat
│   ├── start_frontend.bat
│   └── setup_windows.bat
├── README.md
└── START_HERE.md
```

---

## Windows installation

### 1. Clone

```bat
git clone https://github.com/siddhardh7899583451/emotion-music-recommender.git
cd emotion-music-recommender
```

### 2. Backend setup (Python 3.12)

```bat
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
cd ..
```

If `py -3.12` fails, install Python 3.12 from https://www.python.org and tick **Add to PATH**.

### 3. Frontend setup

```bat
cd frontend
npm install
cd ..
```

---

## Start the application

### Single switch (recommended)

```bat
scripts\start_all.bat
```

Opens backend + frontend in two windows.

- **App UI:** http://localhost:5173
- **API docs:** http://127.0.0.1:8000/docs

Stop: close those windows, or press `Ctrl+C` in each.

### Manual start (two terminals)

**Terminal 1 – Backend**

```bat
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 – Frontend**

```bat
cd frontend
npm run dev
```

---

## Models

Bundled trained classifiers (sklearn GradientBoosting pipelines):

- `ml/models/face/emotion_model.joblib`
- `ml/models/audio/emotion_model.joblib`

Loaded automatically at backend startup when present. Heuristics are used only as fallback.

### Retrain on your own FER / RAVDESS-style data

```bat
backend\venv\Scripts\activate

:: 1) Arrange label folders: angry/, happy/, sad/, ...
:: 2) Extract features
python ml\training\prepare_features_from_images.py C:\data\fer_images
python ml\training\prepare_features_from_audio.py C:\data\ravdess_wavs

:: 3) Train
python ml\training\train_face_model.py --from-csv ml\datasets\face_features.csv
python ml\training\train_audio_model.py --from-csv ml\datasets\audio_features.csv
```

Restart the backend after training.

---

## API overview

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Login → JWT |
| GET | `/api/v1/auth/me` | Current user |
| POST | `/api/v1/emotion/face` | Image → face emotions |
| POST | `/api/v1/emotion/audio` | Audio → emotion |
| POST | `/api/v1/emotion/text` | Text → emotion |
| POST | `/api/v1/emotion/multimodal` | Fuse modalities |
| POST | `/api/v1/music/recommend` | Emotion (+ language) → songs |
| GET | `/api/v1/music/search` | Search catalogue |
| GET | `/api/v1/music/filters` | Languages, genres, moods |
| GET/POST | `/api/v1/favourites` | List / add favourites |
| GET/POST | `/api/v1/playlists` | Playlists |
| POST | `/api/v1/feedback` | Like / dislike |
| GET/PUT | `/api/v1/settings` | User preferences |
| POST/GET | `/api/v1/history` | Emotion history |
| GET | `/api/v1/history/analytics` | Distribution stats |

Full interactive docs: http://127.0.0.1:8000/docs

---

## Tests

```bat
cd backend
venv\Scripts\activate
set PYTHONPATH=.
pytest tests -v
```

## Common Windows issues

| Problem | Solution |
|---------|----------|
| `numpy` build fails on 3.13 | Use **Python 3.12**: `py -3.12 -m venv venv` |
| `python` not found | Reinstall Python with “Add to PATH”, or use `py -3.12` |
| `npm` not found | Install Node.js LTS and open a **new** terminal |
| Camera / mic blocked | Windows Settings → Privacy → allow for browser |
| Port 8000 or 5173 in use | Close old server windows, or change ports |
| `librosa` / `soundfile` install fails | Install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) |

---

## Privacy

- Camera and microphone are used only when you start them and can be stopped anytime.
- Core processing is local.
- Playback uses official YouTube / Spotify embeds.
- Emotion history is stored in local SQLite when you save/fuse results.

---

## Disclaimer

Emotion labels are **predictions**, not clinical diagnoses.  
Respect music platform terms and dataset licenses when retraining.

---

## License

Educational / demonstration project, provided as-is for learning purposes.
