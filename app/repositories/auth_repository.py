from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.auth.model import Auths


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: UUID) -> Auths | None:
        result = await self.session.execute(
            select(Auths).options(selectinload(Auths.role)).where(Auths.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Auths | None:
        result = await self.session.execute(
            select(Auths).options(selectinload(Auths.role)).where(Auths.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_password_reset_token(
        self, token_hash: str, now: datetime
    ) -> Auths | None:
        result = await self.session.execute(
            select(Auths).where(
                Auths.password_reset_token_hash == token_hash,
                Auths.password_reset_expires_at > now,
            )
        )
        return result.scalar_one_or_none()

    async def list(self, offset: int = 0, limit: int = 100) -> list[Auths]:
        result = await self.session.execute(
            select(Auths)
            .options(selectinload(Auths.role))
            .order_by(Auths.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def add(self, user: Auths) -> Auths:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user, attribute_names=["role"])
        return user

    async def delete(self, user: Auths) -> None:
        await self.session.delete(user)

