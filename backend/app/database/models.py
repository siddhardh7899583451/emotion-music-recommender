"""SQLAlchemy ORM models."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(256))
    preferred_languages: Mapped[Optional[str]] = mapped_column(
        String(256), default="English,Hindi,Telugu"
    )
    preferred_genres: Mapped[Optional[str]] = mapped_column(String(256), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    emotion_history = relationship("EmotionHistory", back_populates="user")
    favourites = relationship("FavouriteSong", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    playlists = relationship("Playlist", back_populates="user")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    face_weight: Mapped[float] = mapped_column(Float, default=0.40)
    audio_weight: Mapped[float] = mapped_column(Float, default=0.35)
    text_weight: Mapped[float] = mapped_column(Float, default=0.25)
    dark_mode: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_recommend: Mapped[bool] = mapped_column(Boolean, default=True)
    preferred_language: Mapped[Optional[str]] = mapped_column(String(64), default="Any")

    user = relationship("User", back_populates="preferences")


class EmotionHistory(Base):
    __tablename__ = "emotion_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    face_emotion: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    face_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    audio_emotion: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    audio_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    text_emotion: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    text_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fused_emotion: Mapped[str] = mapped_column(String(32))
    fused_confidence: Mapped[float] = mapped_column(Float)
    modalities_used: Mapped[str] = mapped_column(String(64))
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="emotion_history")


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(256), index=True)
    artist: Mapped[str] = mapped_column(String(256), index=True)
    album: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    language: Mapped[str] = mapped_column(String(64), index=True, default="English")
    genre: Mapped[str] = mapped_column(String(64), index=True, default="Pop")
    mood: Mapped[str] = mapped_column(String(64), index=True)
    energy: Mapped[float] = mapped_column(Float, default=0.5)
    tempo: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    popularity: Mapped[float] = mapped_column(Float, default=0.5)
    youtube_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    spotify_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    artwork_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class FavouriteSong(Base):
    __tablename__ = "favourite_songs"
    __table_args__ = (UniqueConstraint("user_id", "song_id", name="uq_user_song_fav"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    song_id: Mapped[int] = mapped_column(Integer, index=True)  # catalogue id (JSON catalogue)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favourites")


class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    emotion: Mapped[str] = mapped_column(String(32))
    song_ids: Mapped[str] = mapped_column(Text)
    feedback: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SongFeedback(Base):
    """Per-song like/dislike from a user or anonymous session."""
    __tablename__ = "song_feedback"
    __table_args__ = (UniqueConstraint("user_id", "session_id", "song_id", name="uq_feedback"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    song_id: Mapped[int] = mapped_column(Integer, index=True)
    feedback: Mapped[str] = mapped_column(String(16))  # like | dislike
    emotion: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    mood: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="playlists")
    items = relationship("PlaylistItem", back_populates="playlist", cascade="all, delete-orphan")


class PlaylistItem(Base):
    __tablename__ = "playlist_items"
    __table_args__ = (UniqueConstraint("playlist_id", "song_id", name="uq_playlist_song"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id"), index=True)
    song_id: Mapped[int] = mapped_column(Integer, index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    playlist = relationship("Playlist", back_populates="items")
