"""
Train audio-emotion sklearn classifier.

Feature vector length 35 matching audio detector:
  rms, zcr, centroid, bandwidth, rolloff, 12 chroma, 13 mfcc, 5 delta-mfcc

Usage:
  python ml/training/train_audio_model.py
  python ml/training/train_audio_model.py --from-csv data/audio_features.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

LABELS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
OUT = Path(__file__).resolve().parents[1] / "models" / "audio" / "emotion_model.joblib"
N_FEATURES = 35


def synth(n_per_class: int = 600) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(7)
    # first 5: rms, zcr, centroid, bandwidth, rolloff
    spectral = {
        "angry":    np.array([0.11, 0.16, 2600, 2050, 4100]),
        "happy":    np.array([0.085, 0.12, 2350, 1850, 3850]),
        "sad":      np.array([0.028, 0.055, 1350, 1150, 2400]),
        "neutral":  np.array([0.042, 0.07, 1750, 1480, 2950]),
        "fear":     np.array([0.075, 0.145, 2250, 1950, 3650]),
        "surprise": np.array([0.095, 0.135, 2700, 2150, 4300]),
        "disgust":  np.array([0.05, 0.09, 1550, 1380, 2750]),
    }
    X, y = [], []
    for label in LABELS:
        base = spectral[label]
        for _ in range(n_per_class):
            head = base * (1 + rng.normal(0, 0.07, size=5))
            chroma = rng.normal(0.3 if label in ("happy", "surprise") else 0.2, 0.08, size=12)
            mfcc = rng.normal(-5 if label == "sad" else 0, 8, size=13)
            delta = rng.normal(0, 2, size=5)
            vec = np.concatenate([head, chroma, mfcc, delta]).astype(np.float32)
            assert len(vec) == N_FEATURES
            X.append(vec)
            y.append(label)
    return np.asarray(X), np.asarray(y)


def load_csv(path: Path) -> tuple[np.ndarray, np.ndarray]:
    import csv
    rows, labels = [], []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            feats = [float(row[f"f{i}"]) for i in range(N_FEATURES)]
            rows.append(feats)
            labels.append(row["label"].strip().lower())
    return np.asarray(rows, np.float32), np.asarray(labels)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-csv", type=Path, default=None)
    ap.add_argument("--n", type=int, default=600)
    args = ap.parse_args()

    if args.from_csv and args.from_csv.exists():
        X, y = load_csv(args.from_csv)
        print(f"Loaded {len(X)} rows from {args.from_csv}")
    else:
        X, y = synth(args.n)
        print(f"Using synthetic training set: {len(X)} samples")

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    clf = Pipeline([
        ("scaler", StandardScaler()),
        ("gb", GradientBoostingClassifier(random_state=42)),
    ])
    clf.fit(Xtr, ytr)
    pred = clf.predict(Xte)
    print(classification_report(yte, pred, digits=3))
    print("accuracy:", round(accuracy_score(yte, pred), 4))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, OUT)
    print("Saved ->", OUT)


if __name__ == "__main__":
    main()
