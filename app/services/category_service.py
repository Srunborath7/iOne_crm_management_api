from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception import Conflict, NotFound
from app.core.upload import remove_image, save_image
from app.domain.categories.model import Categories
from app.domain.categories.schema import CategoryCreate, CategoryUpdate
from app.repositories.categories_repository import CategoryRepository


class CategoryService:
    """Business logic for Category CRUD and image uploads."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.Categories = CategoryRepository(session)

    async def create_Category(
        self, data: CategoryCreate, upload: UploadFile | None = None
    ) -> Categories:
        if await self.Categories.get_by_name(data.name):
            raise Conflict("A Category with this name already exists.")
        Category = Categories(**data.model_dump())
        stored_image = await save_image(upload, "categories")
        if stored_image is not None:
            Category.image_url, Category.image_path = stored_image
        try:
            await self.Categories.add(Category)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            if stored_image is not None:
                await remove_image(stored_image[0])
            raise Conflict("A Category with this name already exists.") from exc
        except Exception:
            await self.session.rollback()
            if stored_image is not None:
                await remove_image(stored_image[0])
            raise
        await self.session.refresh(Category)
        return Category

    async def get_Category(self, Category_id: UUID) -> Categories:
        Category = await self.Categories.get(Category_id)
        if Category is None:
            raise NotFound("Category")
        return Category

    async def list_Categories(
        self, offset: int = 0, limit: int = 100
    ) -> tuple[list[Categories], int]:
        return await self.Categories.list(offset, limit), await self.Categories.count()

    async def update_Category(
        self,
        Category_id: UUID,
        data: CategoryUpdate,
        upload: UploadFile | None = None,
    ) -> Categories:
        Category = await self.get_Category(Category_id)
        changes = data.model_dump(exclude_unset=True)
        if changes.get("name") and changes["name"] != Category.name:
            existing = await self.Categories.get_by_name(changes["name"])
            if existing is not None:
                raise Conflict("A Category with this name already exists.")
        stored_image = await save_image(upload, "categories") if upload else None
        previous_image_url = Category.image_url
        for field, value in changes.items():
            if field == "name" and value is None:
                continue
            setattr(Category, field, value)
        if stored_image is not None:
            Category.image_url, Category.image_path = stored_image
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            if stored_image is not None:
                await remove_image(stored_image[0])
            raise Conflict("A Category with this name already exists.") from exc
        except Exception:
            await self.session.rollback()
            if stored_image is not None:
                await remove_image(stored_image[0])
            raise
        if stored_image is not None and previous_image_url:
            await remove_image(previous_image_url)
        await self.session.refresh(Category)
        return Category

    async def delete_Category(self, Category_id: UUID) -> None:
        Category = await self.get_Category(Category_id)
        image_url = Category.image_url
        await self.Categories.delete(Category)
        await self.session.commit()
        if image_url:
            await remove_image(image_url)
