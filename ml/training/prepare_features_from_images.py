"""
Extract face features from a folder of images for real-model training.

Expected layout (FER-style):
  dataset/
    angry/*.jpg
    disgust/*.jpg
    fear/*.jpg
    happy/*.jpg
    neutral/*.jpg
    sad/*.jpg
    surprise/*.jpg

Writes CSV: ml/datasets/face_features.csv  (columns f0..f7,label)

Then train with:
  python ml/training/train_face_model.py --from-csv ml/datasets/face_features.csv

Public datasets you can download yourself:
  - FER2013 (Kaggle)
  - AffectNet (license restricted)
  - RAF-DB
Place images into the folder structure above; this script does not scrape copyrighted sets.
"""
from __future__ import annotations

import csv
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datasets" / "face_features.csv"
LABELS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]


def features_from_gray(face_48: np.ndarray) -> list[float]:
    f = face_48.astype("float32") / 255.0
    mean = float(np.mean(f))
    std = float(np.std(f))
    forehead = float(np.mean(f[0:12, :]))
    eyes = float(np.mean(f[12:24, :]))
    mouth = float(np.mean(f[32:48, :]))
    left = float(np.mean(f[:, 0:24]))
    right = float(np.mean(f[:, 24:48]))
    edges = cv2.Canny((f * 255).astype(np.uint8), 50, 150)
    edge_density = float(np.mean(edges) / 255.0)
    return [mean, std, forehead, eyes, mouth, left, right, edge_density]


def main(dataset_dir: Path) -> None:
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    rows = []
    for label in LABELS:
        folder = dataset_dir / label
        if not folder.is_dir():
            print("skip missing", folder)
            continue
        for img_path in list(folder.glob("*.jpg")) + list(folder.glob("*.png")):
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=(48, 48))
            if len(faces) == 0:
                roi = cv2.resize(gray, (48, 48))
            else:
                x, y, w, h = max(faces, key=lambda b: b[2] * b[3])
                roi = cv2.resize(gray[y : y + h, x : x + w], (48, 48))
            rows.append(features_from_gray(roi) + [label])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([f"f{i}" for i in range(8)] + ["label"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python prepare_features_from_images.py /path/to/dataset_root")
        raise SystemExit(1)
    main(Path(sys.argv[1]))
