"""Favourite songs APIs."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.models import FavouriteSong, User
from app.database.session import get_db
from app.services.music_recommendation.engine import music_engine

router = APIRouter(prefix="/favourites", tags=["Favourites"])


class FavRequest(BaseModel):
    song_id: int


class FavOut(BaseModel):
    id: int
    song_id: int
    song: dict


@router.get("", response_model=List[FavOut])
async def list_favourites(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FavouriteSong).where(FavouriteSong.user_id == user.id).order_by(FavouriteSong.created_at.desc())
    )
    rows = result.scalars().all()
    out = []
    for row in rows:
        song = music_engine.get_by_id(row.song_id) or {"id": row.song_id, "title": "Unknown", "artist": ""}
        if song.get("youtube_id"):
            song = dict(song)
            song["youtube_url"] = f"https://www.youtube.com/watch?v={song['youtube_id']}"
        out.append(FavOut(id=row.id, song_id=row.song_id, song=song))
    return out


@router.post("", response_model=FavOut)
async def add_favourite(
    body: FavRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    song = music_engine.get_by_id(body.song_id)
    if not song:
        raise HTTPException(404, "Song not found in catalogue")
    existing = await db.execute(
        select(FavouriteSong).where(
            FavouriteSong.user_id == user.id, FavouriteSong.song_id == body.song_id
        )
    )
    row = existing.scalar_one_or_none()
    if row is None:
        row = FavouriteSong(user_id=user.id, song_id=body.song_id)
        db.add(row)
        await db.flush()
        await db.refresh(row)
    s = dict(song)
    if s.get("youtube_id"):
        s["youtube_url"] = f"https://www.youtube.com/watch?v={s['youtube_id']}"
    return FavOut(id=row.id, song_id=row.song_id, song=s)


@router.delete("/{song_id}")
async def remove_favourite(
    song_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        delete(FavouriteSong).where(
            FavouriteSong.user_id == user.id, FavouriteSong.song_id == song_id
        )
    )
    return {"success": True, "removed": song_id}
