"""Application configuration using pydantic-settings."""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "AI Multimodal Emotion Music Recommender"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR.parent / "data"
    ML_MODELS_DIR: Path = BASE_DIR.parent / "ml" / "models"
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MUSIC_CATALOGUE_PATH: Path = DATA_DIR / "music_catalogue" / "songs.json"

    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'emotion_music.db'}"

    # Security
    SECRET_KEY: str = "change-this-to-a-long-random-secret-in-production-please"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Uploads
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".wav", ".mp3", ".ogg", ".flac", ".m4a", ".webm"]

    # Emotion fusion default weights
    FACE_WEIGHT: float = 0.40
    AUDIO_WEIGHT: float = 0.35
    TEXT_WEIGHT: float = 0.25
    CONFIDENCE_THRESHOLD: float = 0.35

    # Models
    FACE_MODEL_PATH: Path = ML_MODELS_DIR / "face" / "emotion_model.joblib"
    AUDIO_MODEL_PATH: Path = ML_MODELS_DIR / "audio" / "emotion_model.joblib"
    TEXT_LEXICON_PATH: Path = ML_MODELS_DIR / "text" / "emotion_lexicon.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
