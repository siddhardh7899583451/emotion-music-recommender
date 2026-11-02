"""Song recommendation feedback (like/dislike)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_optional
from app.database.models import SongFeedback, User
from app.database.session import get_db
from app.services.music_recommendation.engine import music_engine

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    song_id: int
    feedback: str = Field(..., pattern="^(like|dislike)$")
    emotion: Optional[str] = None
    session_id: Optional[str] = None


@router.post("")
async def submit_feedback(
    body: FeedbackRequest,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    if not music_engine.get_by_id(body.song_id):
        from fastapi import HTTPException
        raise HTTPException(404, "Song not found")

    # Upsert-like: remove prior for same key then insert
    q = select(SongFeedback).where(SongFeedback.song_id == body.song_id)
    if user:
        q = q.where(SongFeedback.user_id == user.id)
    elif body.session_id:
        q = q.where(SongFeedback.session_id == body.session_id)
    else:
        q = q.where(SongFeedback.session_id.is_(None), SongFeedback.user_id.is_(None))

    existing = (await db.execute(q)).scalar_one_or_none()
    if existing:
        existing.feedback = body.feedback
        existing.emotion = body.emotion
    else:
        db.add(
            SongFeedback(
                user_id=user.id if user else None,
                session_id=body.session_id,
                song_id=body.song_id,
                feedback=body.feedback,
                emotion=body.emotion,
            )
        )
    # Tell engine to avoid disliked songs in this session
    if body.feedback == "dislike" and body.session_id:
        music_engine.mark_disliked(body.session_id, body.song_id)
    return {"success": True, "song_id": body.song_id, "feedback": body.feedback}
