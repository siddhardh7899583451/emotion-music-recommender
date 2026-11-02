"""
Extract audio features from a folder of wav files for real-model training.

Expected layout (RAVDESS / CREMA style):
  dataset/
    angry/*.wav
    happy/*.wav
    ...

Writes: ml/datasets/audio_features.csv (f0..f34,label)

Then:
  python ml/training/train_audio_model.py --from-csv ml/datasets/audio_features.csv

Download RAVDESS / CREMA-D yourself (respect licenses). This script only extracts features locally.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import librosa
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datasets" / "audio_features.csv"
LABELS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
N = 35


def extract(path: Path) -> np.ndarray:
    y, sr = librosa.load(str(path), sr=None, mono=True, duration=30)
    if len(y) < sr * 0.5:
        raise ValueError("too short")
    feats = [
        float(np.mean(librosa.feature.rms(y=y))),
        float(np.mean(librosa.feature.zero_crossing_rate(y))),
        float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
        float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))),
        float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))),
    ]
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    feats.extend(float(np.mean(c)) for c in chroma)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    feats.extend(float(np.mean(m)) for m in mfcc)
    delta = librosa.feature.delta(mfcc)
    feats.extend(float(np.mean(d)) for d in delta[:5])
    arr = np.asarray(feats, dtype=np.float32)
    if len(arr) < N:
        arr = np.pad(arr, (0, N - len(arr)))
    return arr[:N]


def main(dataset_dir: Path) -> None:
    rows = []
    for label in LABELS:
        folder = dataset_dir / label
        if not folder.is_dir():
            print("skip", folder)
            continue
        for wav in list(folder.glob("*.wav")) + list(folder.glob("*.mp3")):
            try:
                feats = extract(wav)
                rows.append(list(feats) + [label])
            except Exception as e:
                print("skip", wav, e)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([f"f{i}" for i in range(N)] + ["label"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prepare_features_from_audio.py /path/to/dataset_root")
        raise SystemExit(1)
    main(Path(sys.argv[1]))
