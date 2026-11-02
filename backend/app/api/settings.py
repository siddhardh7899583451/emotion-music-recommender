"""User preference / settings APIs."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.models import User, UserPreference
from app.database.session import get_db

router = APIRouter(prefix="/settings", tags=["Settings"])


class PreferencesOut(BaseModel):
    face_weight: float
    audio_weight: float
    text_weight: float
    dark_mode: bool
    auto_recommend: bool
    preferred_language: Optional[str] = "Any"
    preferred_languages: Optional[str] = None
    preferred_genres: Optional[str] = None


class PreferencesUpdate(BaseModel):
    face_weight: Optional[float] = Field(None, ge=0, le=1)
    audio_weight: Optional[float] = Field(None, ge=0, le=1)
    text_weight: Optional[float] = Field(None, ge=0, le=1)
    dark_mode: Optional[bool] = None
    auto_recommend: Optional[bool] = None
    preferred_language: Optional[str] = None
    preferred_languages: Optional[str] = None
    preferred_genres: Optional[str] = None


@router.get("", response_model=PreferencesOut)
async def get_settings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    pref = result.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=user.id)
        db.add(pref)
        await db.flush()
    return PreferencesOut(
        face_weight=pref.face_weight,
        audio_weight=pref.audio_weight,
        text_weight=pref.text_weight,
        dark_mode=pref.dark_mode,
        auto_recommend=pref.auto_recommend,
        preferred_language=pref.preferred_language,
        preferred_languages=user.preferred_languages,
        preferred_genres=user.preferred_genres,
    )


@router.put("", response_model=PreferencesOut)
async def update_settings(
    body: PreferencesUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    pref = result.scalar_one_or_none()
    if not pref:
        pref = UserPreference(user_id=user.id)
        db.add(pref)
        await db.flush()
    for field in ("face_weight", "audio_weight", "text_weight", "dark_mode", "auto_recommend", "preferred_language"):
        val = getattr(body, field)
        if val is not None:
            setattr(pref, field, val)
    if body.preferred_languages is not None:
        user.preferred_languages = body.preferred_languages
    if body.preferred_genres is not None:
        user.preferred_genres = body.preferred_genres
    await db.flush()
    return await get_settings(user, db)
