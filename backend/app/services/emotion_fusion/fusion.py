"""Multimodal emotion fusion with confidence-aware weighted voting."""
from __future__ import annotations

from typing import Dict, List, Optional

from app.core.config import settings
from app.schemas.emotion import EmotionPrediction, MultimodalRequest, MultimodalResponse

# Canonical emotion set used across the system
CANONICAL = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

# Mapping from any modality label to canonical
LABEL_MAP = {
    "angry": "angry", "anger": "angry", "mad": "angry",
    "disgust": "disgust", "disgusted": "disgust",
    "fear": "fear", "fearful": "fear", "scared": "fear",
    "happy": "happy", "joy": "happy", "joyful": "happy",
    "neutral": "neutral", "calm": "neutral",
    "sad": "sad", "sadness": "sad",
    "surprise": "surprise", "surprised": "surprise",
    # gender-prefixed from old audio model
    "male_angry": "angry", "female_angry": "angry",
    "male_happy": "happy", "female_happy": "happy",
    "male_sad": "sad", "female_sad": "sad",
    "male_fear": "fear", "female_fear": "fear",
    "male_surprise": "surprise", "female_surprise": "surprise",
    "male_disgust": "disgust", "female_disgust": "disgust",
    "male_neutral": "neutral", "female_neutral": "neutral",
}


def normalise_label(label: Optional[str]) -> Optional[str]:
    if not label:
        return None
    return LABEL_MAP.get(label.lower().strip(), label.lower().strip())


class EmotionFusionService:
    def fuse(self, req: MultimodalRequest) -> MultimodalResponse:
        face_w = req.face_weight if req.face_weight is not None else settings.FACE_WEIGHT
        audio_w = req.audio_weight if req.audio_weight is not None else settings.AUDIO_WEIGHT
        text_w = req.text_weight if req.text_weight is not None else settings.TEXT_WEIGHT

        # Collect available modalities
        contributions: List[tuple] = []  # (emotion, conf, weight, name)
        individual: Dict[str, Optional[EmotionPrediction]] = {
            "face": None,
            "audio": None,
            "text": None,
        }

        if req.face_emotion and req.face_confidence is not None:
            emo = normalise_label(req.face_emotion)
            if emo:
                conf = max(0.0, min(1.0, float(req.face_confidence)))
                contributions.append((emo, conf, face_w, "face"))
                individual["face"] = EmotionPrediction(
                    emotion=emo, confidence=conf, modality="face"
                )

        if req.audio_emotion and req.audio_confidence is not None:
            emo = normalise_label(req.audio_emotion)
            if emo:
                conf = max(0.0, min(1.0, float(req.audio_confidence)))
                contributions.append((emo, conf, audio_w, "audio"))
                individual["audio"] = EmotionPrediction(
                    emotion=emo, confidence=conf, modality="audio"
                )

        if req.text_emotion and req.text_confidence is not None:
            emo = normalise_label(req.text_emotion)
            if emo:
                conf = max(0.0, min(1.0, float(req.text_confidence)))
                contributions.append((emo, conf, text_w, "text"))
                individual["text"] = EmotionPrediction(
                    emotion=emo, confidence=conf, modality="text"
                )

        if not contributions:
            return MultimodalResponse(
                success=False,
                fused_emotion="neutral",
                fused_confidence=0.0,
                modalities_used=[],
                individual=individual,
                explanation="No valid modality predictions provided.",
                message="At least one modality result is required.",
            )

        # Weighted score aggregation (confidence * modality weight)
        aggregate: Dict[str, float] = {e: 0.0 for e in CANONICAL}
        weight_sum = 0.0
        modalities_used = []

        for emo, conf, weight, name in contributions:
            # Down-weight low-confidence predictions
            effective_w = weight * conf
            if emo in aggregate:
                aggregate[emo] += effective_w
            else:
                aggregate[emo] = effective_w
            weight_sum += effective_w
            modalities_used.append(name)

        if weight_sum <= 0:
            fused = "neutral"
            fused_conf = 0.0
        else:
            for k in aggregate:
                aggregate[k] /= weight_sum
            fused = max(aggregate, key=aggregate.get)
            fused_conf = aggregate[fused]

        # Build explanation
        parts = []
        for emo, conf, weight, name in contributions:
            parts.append(f"{name}={emo}({conf:.0%}, w={weight:.2f})")
        explanation = (
            f"Fused from {', '.join(parts)}. "
            f"Final emotion '{fused}' with confidence {fused_conf:.1%}."
        )
        if len(set(c[0] for c in contributions)) > 1:
            explanation += " Conflicting modalities were resolved by confidence-weighted voting."

        return MultimodalResponse(
            success=True,
            fused_emotion=fused,
            fused_confidence=round(float(fused_conf), 4),
            modalities_used=modalities_used,
            individual=individual,
            explanation=explanation,
            message="Fusion completed successfully.",
        )


fusion_service = EmotionFusionService()
