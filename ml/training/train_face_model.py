"""
Train face-emotion sklearn classifier.

Default: rich synthetic features matching the live feature extractor.
Optional: --from-csv path/to/features.csv with columns f0..f7,label

Usage:
  python ml/training/train_face_model.py
  python ml/training/train_face_model.py --from-csv data/face_features.csv
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
OUT = Path(__file__).resolve().parents[1] / "models" / "face" / "emotion_model.joblib"


def synth_features(n_per_class: int = 800) -> tuple[np.ndarray, np.ndarray]:
    """Features: mean,std,forehead,eyes,mouth,left,right,edge_density (same as detector)."""
    rng = np.random.default_rng(42)
    # (mean, std, forehead, eyes, mouth, left, right, edge)
    centers = {
        "happy":    np.array([0.58, 0.17, 0.52, 0.48, 0.66, 0.50, 0.50, 0.09]),
        "sad":      np.array([0.34, 0.13, 0.38, 0.36, 0.28, 0.49, 0.49, 0.07]),
        "angry":    np.array([0.40, 0.23, 0.46, 0.40, 0.36, 0.56, 0.44, 0.17]),
        "fear":     np.array([0.37, 0.25, 0.42, 0.52, 0.40, 0.50, 0.50, 0.19]),
        "surprise": np.array([0.52, 0.26, 0.50, 0.58, 0.57, 0.50, 0.50, 0.21]),
        "disgust":  np.array([0.36, 0.20, 0.43, 0.39, 0.33, 0.47, 0.53, 0.15]),
        "neutral":  np.array([0.46, 0.11, 0.48, 0.45, 0.45, 0.50, 0.50, 0.06]),
    }
    spreads = {
        "happy": 0.045, "sad": 0.04, "angry": 0.05, "fear": 0.055,
        "surprise": 0.05, "disgust": 0.045, "neutral": 0.035,
    }
    X, y = [], []
    for label in LABELS:
        c = centers[label]
        s = spreads[label]
        for _ in range(n_per_class):
            v = c + rng.normal(0, s, size=8)
            # mild correlations
            if label == "happy":
                v[4] = max(v[4], v[0] * 0.9)
            if label == "sad":
                v[4] = min(v[4], 0.35)
            X.append(np.clip(v, 0.0, 1.0))
            y.append(label)
    return np.asarray(X, np.float32), np.asarray(y)


def load_csv(path: Path) -> tuple[np.ndarray, np.ndarray]:
    import csv
    rows, labels = [], []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            feats = [float(row[f"f{i}"]) for i in range(8)]
            rows.append(feats)
            labels.append(row["label"].strip().lower())
    return np.asarray(rows, np.float32), np.asarray(labels)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-csv", type=Path, default=None)
    ap.add_argument("--n", type=int, default=800)
    args = ap.parse_args()

    if args.from_csv and args.from_csv.exists():
        X, y = load_csv(args.from_csv)
        print(f"Loaded {len(X)} rows from {args.from_csv}")
    else:
        X, y = synth_features(args.n)
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
