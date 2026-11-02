"""Audio / voice emotion recognition using Librosa features + sklearn."""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple

import librosa
import numpy as np
import soundfile as sf

from app.core.config import settings
from app.schemas.emotion import AudioEmotionResponse, EmotionPrediction

logger = logging.getLogger(__name__)

# Unified emotion labels (mapped from gender-specific if needed)
AUDIO_EMOTIONS = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]


class AudioEmotionService:
    def __init__(self) -> None:
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        path = settings.AUDIO_MODEL_PATH
        if path.exists():
            try:
                import joblib
                self.model = joblib.load(path)
                logger.info("Loaded audio emotion model from %s", path)
            except Exception as exc:
                logger.warning("Audio model load failed: %s", exc)
                self.model = None
        else:
            logger.info("No trained audio model. Using feature-based heuristic.")

    def extract_features(self, y: np.ndarray, sr: int) -> np.ndarray:
        """Extract a compact feature vector suitable for classification."""
        # Ensure mono
        if y.ndim > 1:
            y = np.mean(y, axis=1)

        # Limit duration
        max_samples = sr * 30
        if len(y) > max_samples:
            y = y[:max_samples]
        if len(y) < sr * 0.5:  # < 0.5 s
            raise ValueError("Audio too short (minimum 0.5 seconds).")

        features = []
        # Spectral / energy
        features.append(float(np.mean(librosa.feature.rms(y=y))))
        features.append(float(np.mean(librosa.feature.zero_crossing_rate(y))))
        features.append(float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))))
        features.append(float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))))
        features.append(float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))))
        # Chroma
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        features.extend(float(np.mean(c)) for c in chroma)
        # MFCC (13)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        features.extend(float(np.mean(m)) for m in mfcc)
        # Delta MFCC (first 5)
        delta = librosa.feature.delta(mfcc)
        features.extend(float(np.mean(d)) for d in delta[:5])

        return np.array(features, dtype=np.float32)

    def _heuristic_predict(self, features: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        rms, zcr, centroid, bandwidth, rolloff = features[0:5]
        scores = {e: 0.08 for e in AUDIO_EMOTIONS}

        # High energy + high ZCR → angry / surprise
        if rms > 0.08 and zcr > 0.12:
            scores["angry"] += 0.40
            scores["surprise"] += 0.20
        # Low energy + low centroid → sad / neutral
        if rms < 0.04:
            scores["sad"] += 0.35
            scores["neutral"] += 0.20
        # High centroid → happy / fear
        if centroid > 2200:
            scores["happy"] += 0.30
            scores["fear"] += 0.15
        if bandwidth > 1800 and rms > 0.06:
            scores["surprise"] += 0.25
        if rms < 0.03 and zcr < 0.08:
            scores["neutral"] += 0.30
            scores["disgust"] += 0.10

        total = sum(scores.values())
        scores = {k: v / total for k, v in scores.items()}
        emotion = max(scores, key=scores.get)
        return emotion, scores[emotion], scores

    def predict_from_array(self, y: np.ndarray, sr: int) -> EmotionPrediction:
        features = self.extract_features(y, sr)

        if self.model is not None:
            try:
                # Pad / truncate to expected length if needed
                expected = getattr(self.model, "n_features_in_", len(features))
                if len(features) < expected:
                    features = np.pad(features, (0, expected - len(features)))
                elif len(features) > expected:
                    features = features[:expected]
                proba = self.model.predict_proba(features.reshape(1, -1))[0]
                labels = [str(c) for c in list(getattr(self.model, "classes_", AUDIO_EMOTIONS))]
                scores = {labels[i]: float(proba[i]) for i in range(len(labels))}
                emotion = labels[int(np.argmax(proba))]
                conf = float(np.max(proba))
                return EmotionPrediction(
                    emotion=emotion,
                    confidence=round(conf, 4),
                    scores={k: round(v, 4) for k, v in scores.items()},
                    modality="audio",
                )
            except Exception as exc:
                logger.warning("Audio model predict failed: %s", exc)

        emotion, conf, scores = self._heuristic_predict(features)
        return EmotionPrediction(
            emotion=emotion,
            confidence=round(conf, 4),
            scores={k: round(v, 4) for k, v in scores.items()},
            modality="audio",
        )

    def detect_from_file(self, file_path: Path) -> AudioEmotionResponse:
        try:
            y, sr = librosa.load(str(file_path), sr=None, mono=True, duration=30)
            duration = len(y) / float(sr)
            pred = self.predict_from_array(y, sr)
            return AudioEmotionResponse(
                success=True,
                prediction=pred,
                duration_sec=round(duration, 2),
                message="Audio analysed successfully.",
            )
        except ValueError as ve:
            return AudioEmotionResponse(success=False, message=str(ve))
        except Exception as exc:
            logger.exception("Audio detection error")
            return AudioEmotionResponse(success=False, message=f"Could not process audio: {exc}")

    def detect_from_bytes(self, data: bytes, suffix: str = ".wav") -> AudioEmotionResponse:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
        try:
            return self.detect_from_file(tmp_path)
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass


audio_service = AudioEmotionService()
