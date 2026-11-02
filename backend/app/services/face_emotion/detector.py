"""Facial emotion recognition service.

Uses OpenCV Haar cascade for face detection and a lightweight
appearance-based classifier. When a trained joblib model is present
it is used; otherwise a deterministic heuristic based on facial
region statistics provides demo-quality predictions with confidence.
"""
from __future__ import annotations

import base64
import logging
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from app.core.config import settings
from app.schemas.emotion import EmotionPrediction, FaceEmotionResponse

logger = logging.getLogger(__name__)

EMOTION_LABELS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]


class FaceEmotionService:
    def __init__(self) -> None:
        self.face_cascade = None
        self.model = None
        self._init_cascade()
        self._load_model()

    def _init_cascade(self) -> None:
        """Load Haar cascade with fallbacks for different OpenCV builds."""
        candidates = []
        try:
            if hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
                candidates.append(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        except Exception:
            pass
        # Common system paths (Linux/Windows installs)
        candidates.extend([
            "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
            "/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
            str(Path(__file__).resolve().parents[4] / "ml" / "models" / "face" / "haarcascade_frontalface_default.xml"),
        ])
        cascade_cls = getattr(cv2, "CascadeClassifier", None)
        if cascade_cls is None:
            logger.error("This OpenCV build has no CascadeClassifier. Face detection disabled.")
            return
        for path in candidates:
            try:
                if path and Path(path).exists():
                    cascade = cascade_cls(path)
                    if cascade is not None and not cascade.empty():
                        self.face_cascade = cascade
                        logger.info("Loaded face cascade from %s", path)
                        return
            except Exception as exc:
                logger.debug("Cascade candidate failed %s: %s", path, exc)
        # Last attempt: let OpenCV resolve relative name
        try:
            cascade = cascade_cls("haarcascade_frontalface_default.xml")
            if cascade is not None and not cascade.empty():
                self.face_cascade = cascade
                logger.info("Loaded face cascade by name")
                return
        except Exception:
            pass
        logger.warning("No Haar cascade loaded. Face detection will report zero faces.")

    def _load_model(self) -> None:
        model_path = settings.FACE_MODEL_PATH
        if model_path.exists():
            try:
                import joblib
                self.model = joblib.load(model_path)
                logger.info("Loaded face emotion model from %s", model_path)
            except Exception as exc:
                logger.warning("Could not load face model: %s. Using heuristic.", exc)
                self.model = None
        else:
            logger.info("No trained face model found. Using deterministic heuristic.")

    def _preprocess_face(self, gray_face: np.ndarray) -> np.ndarray:
        face = cv2.resize(gray_face, (48, 48))
        face = face.astype("float32") / 255.0
        return face

    def _extract_simple_features(self, face_48: np.ndarray) -> np.ndarray:
        """Simple statistical features used by heuristic / sklearn model."""
        f = face_48.flatten()
        mean = float(np.mean(f))
        std = float(np.std(f))
        # Region averages (eyes, mouth, forehead)
        forehead = float(np.mean(face_48[0:12, :]))
        eyes = float(np.mean(face_48[12:24, :]))
        mouth = float(np.mean(face_48[32:48, :]))
        left = float(np.mean(face_48[:, 0:24]))
        right = float(np.mean(face_48[:, 24:48]))
        # Edge density proxy
        edges = cv2.Canny((face_48 * 255).astype(np.uint8), 50, 150)
        edge_density = float(np.mean(edges) / 255.0)
        return np.array([mean, std, forehead, eyes, mouth, left, right, edge_density], dtype=np.float32)

    def _heuristic_predict(self, features: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        """Deterministic but varied heuristic for demo when no model is present."""
        mean, std, forehead, eyes, mouth, left, right, edge = features
        scores = {e: 0.05 for e in EMOTION_LABELS}

        # Brighter faces / higher mouth region → happier
        if mouth > 0.55 and mean > 0.45:
            scores["happy"] += 0.55
        if mouth < 0.35 and mean < 0.40:
            scores["sad"] += 0.45
        if std > 0.22 and edge > 0.12:
            scores["surprise"] += 0.35
            scores["fear"] += 0.20
        if forehead > mouth + 0.08 and std < 0.18:
            scores["neutral"] += 0.40
        if left - right > 0.05 or right - left > 0.05:
            scores["angry"] += 0.25
        if edge > 0.18 and mean < 0.42:
            scores["disgust"] += 0.20
            scores["angry"] += 0.15

        # Softmax-like normalisation
        total = sum(scores.values())
        scores = {k: v / total for k, v in scores.items()}
        emotion = max(scores, key=scores.get)
        confidence = scores[emotion]
        return emotion, confidence, scores

    def _predict_face(self, gray_face: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
        face_48 = self._preprocess_face(gray_face)
        features = self._extract_simple_features(face_48)

        if self.model is not None:
            try:
                proba = self.model.predict_proba(features.reshape(1, -1))[0]
                labels = [str(c) for c in list(getattr(self.model, "classes_", EMOTION_LABELS))]
                scores = {labels[i]: float(proba[i]) for i in range(len(labels))}
                emotion = labels[int(np.argmax(proba))]
                confidence = float(np.max(proba))
                return emotion, confidence, scores
            except Exception as exc:
                logger.warning("Model prediction failed: %s", exc)

        return self._heuristic_predict(features)

    def detect_from_image_bytes(self, image_bytes: bytes) -> FaceEmotionResponse:
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return FaceEmotionResponse(success=False, message="Could not decode image.")
            return self._process_frame(img)
        except Exception as exc:
            logger.exception("Face detection error")
            return FaceEmotionResponse(success=False, message=str(exc))

    def detect_from_base64(self, b64: str) -> FaceEmotionResponse:
        try:
            if "," in b64:
                b64 = b64.split(",", 1)[1]
            data = base64.b64decode(b64)
            return self.detect_from_image_bytes(data)
        except Exception as exc:
            return FaceEmotionResponse(success=False, message=f"Invalid base64 image: {exc}")

    def _process_frame(self, frame: np.ndarray) -> FaceEmotionResponse:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.face_cascade is None:
            return FaceEmotionResponse(
                success=False,
                message="Face detector unavailable (OpenCV cascade not loaded). Reinstall opencv-python-headless==4.10.0.84.",
            )
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48)
        )

        predictions: List[EmotionPrediction] = []
        annotated = frame.copy()

        for (x, y, w, h) in faces:
            roi = gray[y : y + h, x : x + w]
            emotion, conf, scores = self._predict_face(roi)
            predictions.append(
                EmotionPrediction(
                    emotion=emotion,
                    confidence=round(conf, 4),
                    scores={k: round(v, 4) for k, v in scores.items()},
                    modality="face",
                )
            )
            color = (0, 255, 0) if conf > 0.45 else (0, 165, 255)
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
            label = f"{emotion} ({conf:.0%})"
            cv2.putText(
                annotated, label, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
            )

        # Encode annotated image
        _, buf = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        annotated_b64 = base64.b64encode(buf).decode("utf-8")

        primary = None
        primary_conf = None
        if predictions:
            # Highest confidence face
            best = max(predictions, key=lambda p: p.confidence)
            primary = best.emotion
            primary_conf = best.confidence

        return FaceEmotionResponse(
            success=True,
            predictions=predictions,
            faces_detected=len(faces),
            primary_emotion=primary,
            primary_confidence=primary_conf,
            annotated_image_base64=annotated_b64,
            message="No face detected." if len(faces) == 0 else f"Detected {len(faces)} face(s).",
        )


# Singleton
face_service = FaceEmotionService()
