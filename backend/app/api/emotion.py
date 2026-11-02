"""Emotion detection API routes."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.schemas.emotion import (
    FaceEmotionResponse,
    AudioEmotionResponse,
    TextEmotionRequest,
    TextEmotionResponse,
    MultimodalRequest,
    MultimodalResponse,
)
from app.services.face_emotion.detector import face_service
from app.services.audio_emotion.detector import audio_service
from app.services.text_emotion.detector import text_service
from app.services.emotion_fusion.fusion import fusion_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/emotion", tags=["Emotion Detection"])


def _check_extension(filename: str, allowed: list) -> bool:
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    return ext in allowed


@router.post("/face", response_model=FaceEmotionResponse)
async def detect_face_emotion(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
):
    """Detect emotion from an uploaded image or base64 string."""
    if file is None and not image_base64:
        raise HTTPException(400, "Provide either an image file or image_base64.")

    if file is not None:
        if not file.filename or not _check_extension(file.filename, settings.ALLOWED_IMAGE_EXTENSIONS):
            raise HTTPException(400, f"Unsupported image type. Allowed: {settings.ALLOWED_IMAGE_EXTENSIONS}")
        data = await file.read()
        if len(data) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(400, f"File too large (max {settings.MAX_UPLOAD_SIZE_MB} MB).")
        return face_service.detect_from_image_bytes(data)

    return face_service.detect_from_base64(image_base64)


@router.post("/audio", response_model=AudioEmotionResponse)
async def detect_audio_emotion(file: UploadFile = File(...)):
    """Detect emotion from an uploaded audio file (wav/mp3/ogg/flac)."""
    if not file.filename or not _check_extension(file.filename, settings.ALLOWED_AUDIO_EXTENSIONS):
        raise HTTPException(400, f"Unsupported audio type. Allowed: {settings.ALLOWED_AUDIO_EXTENSIONS}")
    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"File too large (max {settings.MAX_UPLOAD_SIZE_MB} MB).")
    suffix = "." + file.filename.rsplit(".", 1)[-1].lower()
    return audio_service.detect_from_bytes(data, suffix=suffix)


@router.post("/text", response_model=TextEmotionResponse)
async def detect_text_emotion(body: TextEmotionRequest):
    """Detect emotion from free-form text."""
    return text_service.detect(body.text)


@router.post("/multimodal", response_model=MultimodalResponse)
async def fuse_emotions(body: MultimodalRequest):
    """Fuse predictions from one or more modalities."""
    return fusion_service.fuse(body)
