from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception import Conflict, NotFound
from app.core.upload import remove_image, save_image
from app.domain.auth.model import Auths
from app.domain.products.model import Products
from app.domain.products.schema import ProductCreate, ProductUpdate
from app.repositories.products_repository import ProductRepository


class ProductService:
    """Business logic for product CRUD and image uploads."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.products = ProductRepository(session)

    async def create_product(
        self,
        data: ProductCreate,
        created_by: Auths,
        upload: UploadFile | None = None,
    ) -> Products:
        if await self.products.get_by_sku(data.sku):
            raise Conflict("A product with this SKU already exists.")
        if data.barcode and await self.products.get_by_barcode(data.barcode):
            raise Conflict("A product with this barcode already exists.")

        product = Products(**data.model_dump(exclude={"image_url"}))
        product.creator = created_by
        product.updater = created_by
        stored_image = await save_image(upload, "products") if upload else None
        if stored_image is not None:
            product.image_url = stored_image[0]
        elif data.image_url:
            product.image_url = data.image_url

        try:
            await self.products.add(product)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            if stored_image is not None:
                await remove_image(stored_image[0])
            raise Conflict("Duplicate SKU or barcode, or invalid brand/category.") from exc
        except Exception:
            await self.session.rollback()
            if stored_image is not None:
                await remove_image(stored_image[0])
            raise
        await self.session.refresh(product)
        return product

    async def get_product(self, product_id: UUID) -> Products:
        product = await self.products.get(product_id)
        if product is None:
            raise NotFound("Product")
        return product

    async def list_products(
        self, offset: int = 0, limit: int = 100
    ) -> tuple[list[Products], int]:
        return await self.products.list(offset, limit), await self.products.count()

    async def update_product(
        self,
        product_id: UUID,
        data: ProductUpdate,
        updated_by: Auths,
        upload: UploadFile | None = None,
    ) -> Products:
        product = await self.get_product(product_id)
        changes = data.model_dump(exclude_unset=True)
        new_sku = changes.get("sku")
        if new_sku and new_sku != product.sku:
            existing = await self.products.get_by_sku(new_sku)
            if existing is not None:
                raise Conflict("A product with this SKU already exists.")
        new_barcode = changes.get("barcode")
        if new_barcode and new_barcode != product.barcode:
            existing = await self.products.get_by_barcode(new_barcode)
            if existing is not None:
                raise Conflict("A product with this barcode already exists.")

        stored_image = await save_image(upload, "products") if upload else None
        previous_image_url = product.image_url
        for field, value in changes.items():
            setattr(product, field, value)
        product.updater = updated_by
        if stored_image is not None:
            product.image_url = stored_image[0]

        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            if stored_image is not None:
                await remove_image(stored_image[0])
            raise Conflict("Duplicate SKU or barcode, or invalid brand/category.") from exc
        except Exception:
            await self.session.rollback()
            if stored_image is not None:
                await remove_image(stored_image[0])
            raise
        if stored_image is not None and previous_image_url:
            await remove_image(previous_image_url)
        await self.session.refresh(product)
        return product

    async def delete_product(self, product_id: UUID) -> None:
        product = await self.get_product(product_id)
        image_url = product.image_url
        await self.products.delete(product)
        await self.session.commit()
        if image_url:
            await remove_image(image_url)
