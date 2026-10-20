from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.domain.brands.schema import (
    BrandCreate,
    BrandDetailResponse,
    BrandImageListResponse,
    BrandListItem,
    BrandListResponse,
    BrandResponse,
    BrandUpdate,
    BrandWithImageItem,
)
from app.services.brand_service import BrandService


router = APIRouter(
    prefix="/brands",
    tags=["brands"],
)
SessionDep = Annotated[AsyncSession, Depends(get_db)]
AuthDep = Depends(get_current_user)

@router.post("/", response_model=BrandDetailResponse, status_code=status.HTTP_201_CREATED, dependencies=[AuthDep])
async def create_brand(
    session: SessionDep,
    name: Annotated[str, Form(min_length=1, max_length=50)],
    image: Annotated[UploadFile, File()],
    description: Annotated[str | None, Form()] = None,
) -> BrandDetailResponse:
    data = BrandCreate(name=name, description=description)
    brand = await BrandService(session).create_brand(data, image)
    return BrandDetailResponse(
        message="Brand created successfully",
        data=BrandResponse.model_validate(brand),
    )


@router.get("/", response_model=BrandListResponse)
async def list_brands(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> BrandListResponse:
    brands, total = await BrandService(session).list_brands(offset, limit)
    return BrandListResponse(
        message="Brands retrieved successfully",
        data=[BrandListItem.model_validate(brand) for brand in brands],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/image", response_model=BrandImageListResponse)
async def list_brands_with_image(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> BrandImageListResponse:
    brands, total = await BrandService(session).list_brands(offset, limit)
    return BrandImageListResponse(
        message="Brands with images retrieved successfully",
        data=[BrandWithImageItem.model_validate(brand) for brand in brands],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{brand_id}", response_model=BrandDetailResponse)
async def get_brand(brand_id: UUID, session: SessionDep) -> BrandDetailResponse:
    brand = await BrandService(session).get_brand(brand_id)
    return BrandDetailResponse(
        message="Brand retrieved successfully",
        data=BrandResponse.model_validate(brand),
    )


@router.patch("/{brand_id}", response_model=BrandDetailResponse, dependencies=[AuthDep])
async def update_brand(
    brand_id: UUID,
    session: SessionDep,
    name: Annotated[str | None, Form(min_length=1, max_length=50)] = None,
    description: Annotated[str | None, Form()] = None,
    image: Annotated[UploadFile | None, File()] = None,
) -> BrandDetailResponse:
    fields = {
        key: value
        for key, value in {"name": name, "description": description}.items()
        if value is not None
    }
    data = BrandUpdate.model_validate(fields)
    brand = await BrandService(session).update_brand(brand_id, data, image)
    return BrandDetailResponse(
        message="Brand updated successfully",
        data=BrandResponse.model_validate(brand),
    )


@router.delete("/{brand_id}", status_code=status.HTTP_200_OK, dependencies=[AuthDep])
async def delete_brand(brand_id: UUID, session: SessionDep) -> Response:
    await BrandService(session).delete_brand(brand_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Brand deleted successfully"},
    )
