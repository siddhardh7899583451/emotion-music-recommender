"""Emotion history and analytics APIs."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.database.models import EmotionHistory

router = APIRouter(prefix="/history", tags=["History & Analytics"])


class HistoryCreate(BaseModel):
    session_id: Optional[str] = None
    face_emotion: Optional[str] = None
    face_confidence: Optional[float] = None
    audio_emotion: Optional[str] = None
    audio_confidence: Optional[float] = None
    text_emotion: Optional[str] = None
    text_confidence: Optional[float] = None
    fused_emotion: str
    fused_confidence: float
    modalities_used: str
    details: Optional[dict] = None


class HistoryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    fused_emotion: str
    fused_confidence: float
    modalities_used: str
    face_emotion: Optional[str]
    audio_emotion: Optional[str]
    text_emotion: Optional[str]
    created_at: datetime


@router.post("", response_model=HistoryOut)
async def save_history(body: HistoryCreate, db: AsyncSession = Depends(get_db)):
    row = EmotionHistory(
        session_id=body.session_id,
        face_emotion=body.face_emotion,
        face_confidence=body.face_confidence,
        audio_emotion=body.audio_emotion,
        audio_confidence=body.audio_confidence,
        text_emotion=body.text_emotion,
        text_confidence=body.text_confidence,
        fused_emotion=body.fused_emotion,
        fused_confidence=body.fused_confidence,
        modalities_used=body.modalities_used,
        details=body.details,
    )
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


@router.get("", response_model=List[HistoryOut])
async def list_history(
    session_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(EmotionHistory).order_by(EmotionHistory.created_at.desc()).limit(limit)
    if session_id:
        q = q.where(EmotionHistory.session_id == session_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/analytics")
async def analytics(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(days=days)
    q = (
        select(EmotionHistory.fused_emotion, func.count())
        .where(EmotionHistory.created_at >= since)
        .group_by(EmotionHistory.fused_emotion)
    )
    result = await db.execute(q)
    distribution = {row[0]: row[1] for row in result.all()}

    total_q = select(func.count()).select_from(EmotionHistory).where(EmotionHistory.created_at >= since)
    total = (await db.execute(total_q)).scalar() or 0

    return {
        "period_days": days,
        "total_detections": total,
        "emotion_distribution": distribution,
    }
