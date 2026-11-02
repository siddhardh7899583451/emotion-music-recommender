"""Pydantic schemas for emotion detection and fusion."""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class EmotionPrediction(BaseModel):
    emotion: str
    confidence: float = Field(ge=0.0, le=1.0)
    scores: Dict[str, float] = Field(default_factory=dict)
    modality: str
    message: Optional[str] = None


class FaceEmotionRequest(BaseModel):
    # Used when base64 image is sent
    image_base64: Optional[str] = None


class FaceEmotionResponse(BaseModel):
    success: bool
    predictions: List[EmotionPrediction] = Field(default_factory=list)
    faces_detected: int = 0
    primary_emotion: Optional[str] = None
    primary_confidence: Optional[float] = None
    annotated_image_base64: Optional[str] = None
    message: str = ""


class AudioEmotionResponse(BaseModel):
    success: bool
    prediction: Optional[EmotionPrediction] = None
    duration_sec: Optional[float] = None
    message: str = ""


class TextEmotionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class TextEmotionResponse(BaseModel):
    success: bool
    prediction: Optional[EmotionPrediction] = None
    message: str = ""


class MultimodalRequest(BaseModel):
    face_emotion: Optional[str] = None
    face_confidence: Optional[float] = None
    audio_emotion: Optional[str] = None
    audio_confidence: Optional[float] = None
    text_emotion: Optional[str] = None
    text_confidence: Optional[float] = None
    face_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    audio_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    text_weight: Optional[float] = Field(None, ge=0.0, le=1.0)


class MultimodalResponse(BaseModel):
    success: bool
    fused_emotion: str
    fused_confidence: float
    modalities_used: List[str]
    individual: Dict[str, Optional[EmotionPrediction]]
    explanation: str
    message: str = ""


class EmotionHistoryItem(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    fused_emotion: str
    fused_confidence: float
    modalities_used: str
    face_emotion: Optional[str]
    audio_emotion: Optional[str]
    text_emotion: Optional[str]
    created_at: str
