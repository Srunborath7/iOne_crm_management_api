from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.categories.model import Categories


class CategoryRepository:
    """Data access for brand records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, brand_id: UUID) -> Categories | None:
        result = await self.session.execute(select(Categories).where(Categories.id == brand_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Categories | None:
        result = await self.session.execute(select(Categories).where(Categories.name == name))
        return result.scalar_one_or_none()

    async def list(self, offset: int = 0, limit: int = 100) -> list[Categories]:
        result = await self.session.execute(
            select(Categories)
            .order_by(Categories.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Categories))
        return result.scalar_one()

    async def add(self, brand: Categories) -> Categories:
        self.session.add(brand)
        await self.session.flush()
        return brand

    async def delete(self, brand: Categories) -> None:
        await self.session.delete(brand)
