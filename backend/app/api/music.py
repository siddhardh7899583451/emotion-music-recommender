"""Music recommendation and catalogue APIs."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.music_recommendation.engine import music_engine

router = APIRouter(prefix="/music", tags=["Music"])


class RecommendRequest(BaseModel):
    emotion: str = Field(..., examples=["happy", "sad"])
    language: Optional[str] = Field(None, examples=["English", "Hindi", "Telugu"])
    genre: Optional[str] = None
    limit: int = Field(8, ge=1, le=30)
    session_id: Optional[str] = None


class SongOut(BaseModel):
    id: int
    title: str
    artist: str
    album: Optional[str] = None
    language: str
    genre: str
    mood: str
    energy: float
    tempo: Optional[float] = None
    popularity: float
    youtube_id: Optional[str] = None
    spotify_url: Optional[str] = None
    artwork_url: Optional[str] = None
    tags: Optional[str] = None
    youtube_url: Optional[str] = None


def _enrich(song: dict) -> dict:
    s = dict(song)
    if s.get("youtube_id"):
        s["youtube_url"] = f"https://www.youtube.com/watch?v={s['youtube_id']}"
    return s


@router.post("/recommend", response_model=List[SongOut])
async def recommend(body: RecommendRequest):
    songs = music_engine.recommend(
        emotion=body.emotion,
        language=body.language,
        genre=body.genre,
        limit=body.limit,
        session_id=body.session_id,
    )
    return [_enrich(s) for s in songs]


@router.get("/search", response_model=List[SongOut])
async def search(
    q: str = Query("", max_length=100),
    language: Optional[str] = None,
    mood: Optional[str] = None,
    limit: int = Query(20, ge=1, le=50),
):
    songs = music_engine.search(query=q, language=language, mood=mood, limit=limit)
    return [_enrich(s) for s in songs]


@router.get("/filters")
async def filters():
    return {
        "languages": music_engine.all_languages(),
        "genres": music_engine.all_genres(),
        "moods": music_engine.all_moods(),
    }


@router.get("/song/{song_id}", response_model=SongOut)
async def get_song(song_id: int):
    song = music_engine.get_by_id(song_id)
    if not song:
        from fastapi import HTTPException
        raise HTTPException(404, "Song not found")
    return _enrich(song)
