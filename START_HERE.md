# START HERE — Emotion Music Recommender v1.1.0

## 1. Install (once)

```bat
cd backend
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
cd ..\frontend
npm install
cd ..
```

Or run: `scripts\setup_windows.bat`

## 2. Run

```bat
scripts\start_all.bat
```

Open **http://localhost:5173**

## 3. Quick test (v1.1 auto-recommend)

1. **Text** → type “I am so happy today” → **Detect Emotion & Recommend** → songs appear below.  
2. **Face** → Start Webcam → **Capture & Recommend**.  
3. **Audio** → Start Recording → speak 3 seconds → **Stop & Analyse**.  

If camera/mic is blocked: Windows Privacy settings → allow for the browser.

## 4. Push updates to GitHub

```bat
git add .
git commit -m "v1.1.0: auto-recommend after emotion detection; camera and mic fixes"
git push
```

Full docs → **README.md**
