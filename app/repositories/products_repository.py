from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.products.model import Products


class ProductRepository:
    """Data access for product records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, product_id: UUID) -> Products | None:
        result = await self.session.execute(select(Products).where(Products.id == product_id))
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str) -> Products | None:
        result = await self.session.execute(select(Products).where(Products.sku == sku))
        return result.scalar_one_or_none()

    async def get_by_barcode(self, barcode: str) -> Products | None:
        result = await self.session.execute(
            select(Products).where(Products.barcode == barcode)
        )
        return result.scalar_one_or_none()

    async def list(self, offset: int = 0, limit: int = 100) -> list[Products]:
        result = await self.session.execute(
            select(Products)
            .order_by(Products.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Products))
        return result.scalar_one()

    async def add(self, product: Products) -> Products:
        self.session.add(product)
        await self.session.flush()
        return product

    async def delete(self, product: Products) -> None:
        await self.session.delete(product)
