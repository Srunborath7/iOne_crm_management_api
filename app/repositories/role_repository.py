from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.auth.model import RoleUser


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, role_id: UUID) -> RoleUser | None:
        result = await self.session.execute(
            select(RoleUser).where(RoleUser.id == role_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> RoleUser | None:
        result = await self.session.execute(
            select(RoleUser).where(RoleUser.name == name)
        )
        return result.scalar_one_or_none()

    async def list(self) -> list[RoleUser]:
        result = await self.session.execute(select(RoleUser).order_by(RoleUser.name))
        return list(result.scalars().all())

    async def add(self, role: RoleUser) -> RoleUser:
        self.session.add(role)
        await self.session.flush()
        return role

    async def delete(self, role: RoleUser) -> None:
        await self.session.delete(role)
