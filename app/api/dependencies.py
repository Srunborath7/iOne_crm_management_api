from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exception import Unauthorized
from app.core.security import decode_access_token
from app.repositories.auth_repository import AuthRepository


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    if credentials is None:
        raise Unauthorized("Bearer token required")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError):
        raise Unauthorized("Invalid or expired access token") from None

    user = await AuthRepository(session).get(user_id)
    if user is None:
        raise Unauthorized("User for this access token no longer exists")
    return user
