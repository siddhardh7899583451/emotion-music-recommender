"""Playlist management APIs."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database.models import Playlist, PlaylistItem, User
from app.database.session import get_db
from app.services.music_recommendation.engine import music_engine

router = APIRouter(prefix="/playlists", tags=["Playlists"])


class PlaylistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = None
    mood: Optional[str] = None


class PlaylistAddSong(BaseModel):
    song_id: int


class PlaylistOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    mood: Optional[str]
    song_count: int
    songs: List[dict] = []


@router.get("", response_model=List[PlaylistOut])
async def list_playlists(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Playlist)
        .where(Playlist.user_id == user.id)
        .options(selectinload(Playlist.items))
        .order_by(Playlist.created_at.desc())
    )
    playlists = result.scalars().all()
    out = []
    for pl in playlists:
        songs = []
        for item in sorted(pl.items, key=lambda i: i.position):
            s = music_engine.get_by_id(item.song_id)
            if s:
                s = dict(s)
                if s.get("youtube_id"):
                    s["youtube_url"] = f"https://www.youtube.com/watch?v={s['youtube_id']}"
                songs.append(s)
        out.append(
            PlaylistOut(
                id=pl.id,
                name=pl.name,
                description=pl.description,
                mood=pl.mood,
                song_count=len(songs),
                songs=songs,
            )
        )
    return out


@router.post("", response_model=PlaylistOut)
async def create_playlist(
    body: PlaylistCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pl = Playlist(
        user_id=user.id,
        name=body.name.strip(),
        description=body.description,
        mood=body.mood,
    )
    db.add(pl)
    await db.flush()
    await db.refresh(pl)
    return PlaylistOut(
        id=pl.id, name=pl.name, description=pl.description, mood=pl.mood, song_count=0, songs=[]
    )


@router.post("/{playlist_id}/songs", response_model=PlaylistOut)
async def add_song(
    playlist_id: int,
    body: PlaylistAddSong,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Playlist)
        .where(Playlist.id == playlist_id, Playlist.user_id == user.id)
        .options(selectinload(Playlist.items))
    )
    pl = result.scalar_one_or_none()
    if not pl:
        raise HTTPException(404, "Playlist not found")
    if not music_engine.get_by_id(body.song_id):
        raise HTTPException(404, "Song not found")
    if any(i.song_id == body.song_id for i in pl.items):
        raise HTTPException(400, "Song already in playlist")
    item = PlaylistItem(playlist_id=pl.id, song_id=body.song_id, position=len(pl.items))
    db.add(item)
    await db.flush()
    await db.refresh(pl)
    songs = []
    for i in sorted(pl.items, key=lambda x: x.position):
        s = music_engine.get_by_id(i.song_id)
        if s:
            s = dict(s)
            if s.get("youtube_id"):
                s["youtube_url"] = f"https://www.youtube.com/watch?v={s['youtube_id']}"
            songs.append(s)
    return PlaylistOut(
        id=pl.id, name=pl.name, description=pl.description, mood=pl.mood, song_count=len(songs), songs=songs
    )


@router.delete("/{playlist_id}")
async def delete_playlist(
    playlist_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Playlist).where(Playlist.id == playlist_id, Playlist.user_id == user.id)
    )
    pl = result.scalar_one_or_none()
    if not pl:
        raise HTTPException(404, "Playlist not found")
    await db.delete(pl)
    return {"success": True}
