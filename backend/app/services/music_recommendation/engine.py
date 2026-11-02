"""Intelligent music recommendation engine."""
from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Set

from app.core.config import settings

logger = logging.getLogger(__name__)

# Emotion → preferred moods (ordered)
EMOTION_TO_MOODS: Dict[str, List[str]] = {
    "happy": ["happy", "energetic", "motivational"],
    "sad": ["sad", "calm", "neutral"],
    "angry": ["energetic", "motivational", "happy"],
    "fear": ["calm", "neutral", "happy"],
    "surprise": ["energetic", "happy", "motivational"],
    "disgust": ["calm", "neutral", "happy"],
    "neutral": ["neutral", "calm", "happy"],
}

MOOD_ENERGY_RANGE = {
    "happy": (0.55, 1.0),
    "sad": (0.0, 0.45),
    "angry": (0.6, 1.0),
    "fear": (0.0, 0.5),
    "surprise": (0.5, 1.0),
    "disgust": (0.0, 0.5),
    "neutral": (0.3, 0.7),
    "calm": (0.0, 0.4),
    "energetic": (0.7, 1.0),
    "motivational": (0.65, 1.0),
    "relaxing": (0.0, 0.35),
}


class MusicRecommendationEngine:
    def __init__(self) -> None:
        self.songs: List[dict] = []
        self._load_catalogue()
        self._recent_ids: Dict[str, List[int]] = {}  # session → recent song ids
        self._disliked: Dict[str, set] = {}  # session → disliked song ids

    def _load_catalogue(self) -> None:
        path = settings.MUSIC_CATALOGUE_PATH
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self.songs = json.load(f)
            logger.info("Loaded %d songs from catalogue", len(self.songs))
        else:
            logger.warning("Music catalogue not found at %s", path)
            self.songs = []

    def recommend(
        self,
        emotion: str,
        language: Optional[str] = None,
        genre: Optional[str] = None,
        limit: int = 8,
        session_id: Optional[str] = None,
        exclude_ids: Optional[Set[int]] = None,
    ) -> List[dict]:
        emotion = (emotion or "neutral").lower()
        preferred_moods = EMOTION_TO_MOODS.get(emotion, ["neutral", "happy"])
        energy_range = MOOD_ENERGY_RANGE.get(emotion, (0.2, 0.8))

        candidates = list(self.songs)

        # Language filter
        if language and language.lower() not in ("any", "all", ""):
            lang = language.lower()
            filtered = [s for s in candidates if s.get("language", "").lower() == lang]
            if filtered:
                candidates = filtered

        # Genre filter
        if genre and genre.lower() not in ("any", "all", ""):
            g = genre.lower()
            filtered = [s for s in candidates if g in s.get("genre", "").lower()]
            if filtered:
                candidates = filtered

        # Exclude recently recommended
        exclude = set(exclude_ids or [])
        if session_id and session_id in self._recent_ids:
            exclude.update(self._recent_ids[session_id])
        if session_id and session_id in self._disliked:
            exclude.update(self._disliked[session_id])

        candidates = [s for s in candidates if s["id"] not in exclude]

        # Score each song
        scored = []
        for s in candidates:
            score = 0.0
            mood = (s.get("mood") or "").lower()
            energy = float(s.get("energy") or 0.5)
            pop = float(s.get("popularity") or 0.5)

            # Mood match
            if mood in preferred_moods:
                score += 3.0 * (1.0 - preferred_moods.index(mood) * 0.25)
            elif mood == emotion:
                score += 2.5

            # Energy match
            lo, hi = energy_range
            if lo <= energy <= hi:
                score += 1.5
            else:
                score += max(0, 1.0 - abs(energy - (lo + hi) / 2) * 2)

            score += pop * 0.8  # slight popularity bias
            score += random.uniform(0, 0.4)  # diversity noise

            scored.append((score, s))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [s for _, s in scored[:limit]]

        # Track recent
        if session_id and results:
            recent = self._recent_ids.setdefault(session_id, [])
            recent.extend(s["id"] for s in results)
            self._recent_ids[session_id] = recent[-30:]  # keep last 30

        return results

    def search(
        self,
        query: str = "",
        language: Optional[str] = None,
        mood: Optional[str] = None,
        limit: int = 20,
    ) -> List[dict]:
        q = (query or "").lower().strip()
        results = self.songs
        if q:
            results = [
                s for s in results
                if q in s.get("title", "").lower()
                or q in s.get("artist", "").lower()
                or q in (s.get("tags") or "").lower()
            ]
        if language and language.lower() not in ("any", "all"):
            results = [s for s in results if s.get("language", "").lower() == language.lower()]
        if mood and mood.lower() not in ("any", "all"):
            results = [s for s in results if s.get("mood", "").lower() == mood.lower()]
        return results[:limit]

    def get_by_id(self, song_id: int) -> Optional[dict]:
        for s in self.songs:
            if s["id"] == song_id:
                return s
        return None


    def mark_disliked(self, session_id: str, song_id: int) -> None:
        self._disliked.setdefault(session_id, set()).add(song_id)

    def all_languages(self) -> List[str]:
        return sorted({s.get("language", "Unknown") for s in self.songs})

    def all_genres(self) -> List[str]:
        return sorted({s.get("genre", "Unknown") for s in self.songs})

    def all_moods(self) -> List[str]:
        return sorted({s.get("mood", "Unknown") for s in self.songs})


music_engine = MusicRecommendationEngine()
