"""Authentication APIs: register, login, me."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.database.models import User, UserPreference
from app.database.session import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: str = Field(..., min_length=5, max_length=128)
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str


class UserOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    username: str
    email: str
    preferred_languages: Optional[str] = None
    preferred_genres: Optional[str] = None


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(User).where((User.username == body.username) | (User.email == body.email))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or email already registered")
    user = User(
        username=body.username.strip(),
        email=body.email.strip().lower(),
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.flush()
    db.add(UserPreference(user_id=user.id))
    await db.flush()
    token = create_access_token(user.id, extra={"username": user.username})
    return TokenResponse(access_token=token, user_id=user.id, username=user.username)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    token = create_access_token(user.id, extra={"username": user.username})
    return TokenResponse(access_token=token, user_id=user.id, username=user.username)


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user
