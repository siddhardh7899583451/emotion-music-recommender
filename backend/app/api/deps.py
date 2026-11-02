"""Shared FastAPI dependencies."""
from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database.models import User
from app.database.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not creds:
        return None
    data = decode_access_token(creds.credentials)
    if not data or "sub" not in data:
        return None
    result = await db.execute(select(User).where(User.id == int(data["sub"])))
    return result.scalar_one_or_none()


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
