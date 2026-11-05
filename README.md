# AI-Based Multimodal Emotion Recognition and Personalized Music Recommendation System

**Version 1.1.0**

Detect emotion from **face**, **voice**, and **text**, then **automatically receive personalized music recommendations**.

**Repository:** https://github.com/siddhardh7899583451/emotion-music-recommender

---

## What’s new in 1.1.0

| Fix / feature | Detail |
|---------------|--------|
| **Auto music after detection** | Text, Face, and Audio pages now call `/music/recommend` immediately after a successful emotion prediction and show song cards on the same page |
| **Camera reliability** | Explicit `video.play()`, better permission / not-found errors, ready-state check before capture |
| **Microphone reliability** | Preferred MediaRecorder MIME types, timeslice, minimum size check, clearer errors, correct `.webm` / `.ogg` extension for backend |
| **Language filter on detect pages** | Choose English / Hindi / Telugu / Tamil / Kannada before or after detection |
| **History on single-modality** | Optional history save after face / audio / text detection |

---

## Features

| Module | Capability |
|--------|------------|
| **Facial emotion** | Webcam (snapshot + live ~2.5s), image upload, OpenCV + trained model, bounding boxes → **auto music** |
| **Audio emotion** | Microphone or WAV/MP3/WebM upload, Librosa features + trained model → **auto music** |
| **Text emotion** | Free-text lexicon scoring (English + emojis) → **auto music** |
| **Multimodal fusion** | Confidence-weighted combination of any available modalities → recommend |
| **Music recommendations** | Emotion + language + energy matching (English, Hindi, Telugu, Tamil, Kannada, …) |
| **In-app playback** | Official YouTube / Spotify embed |
| **Favourites & playlists** | Save songs, create playlists (login required) |
| **Like / dislike feedback** | Improves session recommendations |
| **Auth & settings** | Register/login (JWT), modality weights, dark/light theme |
| **Analytics** | Emotion history charts (SQLite) |

---

## Tech stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, SQLite, OpenCV, Librosa, scikit-learn  
- **Frontend:** React 18, Vite, React Router, Recharts  
- **Models:** Bundled `ml/models/face/emotion_model.joblib` and `ml/models/audio/emotion_model.joblib`  
- **No Docker / no CUDA required** for core use  

---

## Requirements

| Software | Version |
|----------|---------|
| **Python** | **3.12** (recommended). Avoid 3.13+ for package wheels |
| **Node.js** | 18+ (LTS or current) |
| **Git** | Optional, for updates |

---

## Quick start (Windows)

### 1. Clone

```bat
git clone https://github.com/siddhardh7899583451/emotion-music-recommender.git
cd emotion-music-recommender
```

### 2. One-time setup

**Backend (use Python 3.12):**

```bat
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
cd ..
```

**Frontend:**

```bat
cd frontend
npm install
cd ..
```

### 3. Start the app (single switch)

```bat
scripts\start_all.bat
```

- Backend → http://127.0.0.1:8000  
- Frontend → http://localhost:5173  
- **API docs:** http://127.0.0.1:8000/docs  

To stop: close the two console windows, or press `Ctrl+C` in each.

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

## How the flow works (v1.1)

1. Open **Face**, **Audio**, or **Text** page.  
2. Capture / record / type → **Detect**.  
3. Emotion is shown **and** matching songs appear automatically below.  
4. Optionally change language and click **Refresh recommendations**.  
5. Or use **Multimodal** to fuse face + audio + text manually and recommend.  

---

## Project structure

```text
emotion-music-recommender/
├── backend/          # FastAPI app, APIs, services, tests
├── frontend/         # React + Vite UI
├── data/             # Music catalogue (songs.json)
├── ml/
│   ├── models/       # Trained face & audio joblib models
│   └── training/     # Train / prepare feature scripts
├── scripts/
│   ├── start_all.bat      # Single switch: start backend + frontend
│   ├── start_backend.bat
│   ├── start_frontend.bat
│   └── setup_windows.bat
├── README.md
└── START_HERE.md
```

---

## Optional: retrain models on your data

```bat
backend\venv\Scripts\activate

:: Arrange labeled folders: dataset/happy/*.jpg , dataset/sad/*.wav , etc.
python ml\training\prepare_features_from_images.py C:\path\to\image_dataset
python ml\training\prepare_features_from_audio.py C:\path\to\audio_dataset

python ml\training\train_face_model.py --from-csv ml\datasets\face_features.csv
python ml\training\train_audio_model.py --from-csv ml\datasets\audio_features.csv
```

Restart the backend after training.

---

## Tests

```bat
cd backend
venv\Scripts\activate
set PYTHONPATH=.
pytest tests -v
```

---

## Update this project on GitHub

After you change files:

```bat
cd C:\Projects\emotion-music-recommender
git add .
git status
git commit -m "v1.1.0: auto-recommend after text/face/audio + camera/mic fixes"
git push
```

Suggested commit message for this release:

```bat
git add frontend/src/pages/TextPage.jsx frontend/src/pages/FacePage.jsx frontend/src/pages/AudioPage.jsx README.md backend/app/core/config.py frontend/package.json
git commit -m "v1.1.0: auto music recommendations after emotion detection; improve camera and microphone reliability"
git push
```

---

## Common issues

| Problem | Fix |
|---------|-----|
| `numpy` / pip build fails | Use **Python 3.12** venv: `py -3.12 -m venv venv` (not 3.13) |
| `node` / `npm` not found | Install Node.js LTS and open a **new** terminal |
| Camera / mic blocked | Windows Privacy → Camera / Microphone → allow for your browser; click Allow when the site prompts |
| Camera black / no frame | Wait 1–2 s after “Start Webcam”, then Capture. Prefer Chrome/Edge. Use **localhost** (not a random IP) |
| Mic recording empty | Speak 2–3+ seconds before Stop. Prefer Chrome. Or upload a WAV/MP3 |
| Port in use | Close old backend/frontend windows, or change ports |
| Models not loading | Ensure `ml\models\face\emotion_model.joblib` and `audio\...` exist |
| Emotion detected but no songs | Catalogue is small (~40 tracks). Try language = **Any**, or another emotion (happy/sad/neutral) |

---

## Privacy & disclaimer

- Camera and microphone are used only when you start them.  
- Core processing is local; playback uses official YouTube/Spotify embeds.  
- Emotion labels are **predictions**, not clinical diagnoses.

---

## License

Educational / demonstration project. Respect third-party music platform terms and dataset licenses when retraining.
