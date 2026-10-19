from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception import Conflict, NotFound
from app.core.upload import remove_image, save_image
from app.domain.brands.model import Brands
from app.domain.brands.schema import BrandCreate, BrandUpdate
from app.repositories.brand_repository import BrandRepository


class BrandService:
    """Business logic for brand CRUD and image uploads."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.brands = BrandRepository(session)

    async def create_brand(
        self, data: BrandCreate, upload: UploadFile | None = None
    ) -> Brands:
        if await self.brands.get_by_name(data.name):
            raise Conflict("A brand with this name already exists.")
        brand = Brands(**data.model_dump())
        stored_image = await save_image(upload, "brands")
        if stored_image is not None:
            brand.image_url, brand.image_path = stored_image
        try:
            await self.brands.add(brand)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            if stored_image is not None:
                await remove_image(stored_image[0])
            raise Conflict("A brand with this name already exists.") from exc
        except Exception:
            await self.session.rollback()
            if stored_image is not None:
                await remove_image(stored_image[0])
            raise
        await self.session.refresh(brand)
        return brand

    async def get_brand(self, brand_id: UUID) -> Brands:
        brand = await self.brands.get(brand_id)
        if brand is None:
            raise NotFound("Brand")
        return brand

    async def list_brands(
        self, offset: int = 0, limit: int = 100
    ) -> tuple[list[Brands], int]:
        return await self.brands.list(offset, limit), await self.brands.count()

    async def update_brand(
        self,
        brand_id: UUID,
        data: BrandUpdate,
        upload: UploadFile | None = None,
    ) -> Brands:
        brand = await self.get_brand(brand_id)
        changes = data.model_dump(exclude_unset=True)
        if changes.get("name") and changes["name"] != brand.name:
            existing = await self.brands.get_by_name(changes["name"])
            if existing is not None:
                raise Conflict("A brand with this name already exists.")
        stored_image = await save_image(upload, "brands") if upload else None
        previous_image_url = brand.image_url
        for field, value in changes.items():
            if field == "name" and value is None:
                continue
            setattr(brand, field, value)
        if stored_image is not None:
            brand.image_url, brand.image_path = stored_image
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            if stored_image is not None:
                await remove_image(stored_image[0])
            raise Conflict("A brand with this name already exists.") from exc
        except Exception:
            await self.session.rollback()
            if stored_image is not None:
                await remove_image(stored_image[0])
            raise
        if stored_image is not None and previous_image_url:
            await remove_image(previous_image_url)
        await self.session.refresh(brand)
        return brand

    async def delete_brand(self, brand_id: UUID) -> None:
        brand = await self.get_brand(brand_id)
        image_url = brand.image_url
        await self.brands.delete(brand)
        await self.session.commit()
        if image_url:
            await remove_image(image_url)
