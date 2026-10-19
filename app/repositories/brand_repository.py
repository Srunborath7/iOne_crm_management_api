from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.brands.model import Brands


class BrandRepository:
    """Data access for brand records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, brand_id: UUID) -> Brands | None:
        result = await self.session.execute(select(Brands).where(Brands.id == brand_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Brands | None:
        result = await self.session.execute(select(Brands).where(Brands.name == name))
        return result.scalar_one_or_none()

    async def list(self, offset: int = 0, limit: int = 100) -> list[Brands]:
        result = await self.session.execute(
            select(Brands)
            .order_by(Brands.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Brands))
        return result.scalar_one()

    async def add(self, brand: Brands) -> Brands:
        self.session.add(brand)
        await self.session.flush()
        return brand

    async def delete(self, brand: Brands) -> None:
        await self.session.delete(brand)
