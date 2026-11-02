"""FastAPI application entry point."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.database.session import init_db
from app.api import emotion, music, history, auth, favourites, playlists, feedback, settings as settings_api

logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    (settings.ML_MODELS_DIR / "face").mkdir(parents=True, exist_ok=True)
    (settings.ML_MODELS_DIR / "audio").mkdir(parents=True, exist_ok=True)
    (settings.ML_MODELS_DIR / "text").mkdir(parents=True, exist_ok=True)
    await init_db()
    logger.info("%s v%s started", settings.APP_NAME, settings.APP_VERSION)
    yield
    # Shutdown
    logger.info("Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-Based Multimodal Emotion Recognition and Personalized Music Recommendation System. "
        "Supports facial, audio and text emotion detection with intelligent fusion and music recommendations."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"] if settings.DEBUG else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(emotion.router, prefix=settings.API_PREFIX)
app.include_router(music.router, prefix=settings.API_PREFIX)
app.include_router(history.router, prefix=settings.API_PREFIX)
app.include_router(favourites.router, prefix=settings.API_PREFIX)
app.include_router(playlists.router, prefix=settings.API_PREFIX)
app.include_router(feedback.router, prefix=settings.API_PREFIX)
app.include_router(settings_api.router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "api": settings.API_PREFIX,
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error", "detail": str(exc) if settings.DEBUG else None},
    )
