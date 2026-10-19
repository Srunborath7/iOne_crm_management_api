from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.domain.auth.model import Auths
from app.domain.products.schema import (
    ProductCreate,
    ProductDetailResponse,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services.products_service import ProductService


router = APIRouter(
    prefix="/products",
    tags=["products"],
    dependencies=[Depends(get_current_user)],
)
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[Auths, Depends(get_current_user)]


@router.post("/", response_model=ProductDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    session: SessionDep,
    current_user: CurrentUserDep,
    data: Annotated[ProductCreate, Form()],
    image: Annotated[UploadFile | None, File()] = None,
) -> ProductDetailResponse:
    product = await ProductService(session).create_product(data, current_user, image)
    return ProductDetailResponse(
        message="Product created successfully",
        data=ProductResponse.model_validate(product),
    )


@router.get("/", response_model=ProductListResponse)
async def list_products(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> ProductListResponse:
    products, total = await ProductService(session).list_products(offset, limit)
    return ProductListResponse(
        message="Products retrieved successfully",
        data=[ProductResponse.model_validate(product) for product in products],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(product_id: UUID, session: SessionDep) -> ProductDetailResponse:
    product = await ProductService(session).get_product(product_id)
    return ProductDetailResponse(
        message="Product retrieved successfully",
        data=ProductResponse.model_validate(product),
    )


@router.patch("/{product_id}", response_model=ProductDetailResponse)
async def update_product(
    product_id: UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
    data: Annotated[ProductUpdate, Form()],
    image: Annotated[UploadFile | None, File()] = None,
) -> ProductDetailResponse:
    product = await ProductService(session).update_product(
        product_id, data, current_user, image
    )
    return ProductDetailResponse(
        message="Product updated successfully",
        data=ProductResponse.model_validate(product),
    )


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(product_id: UUID, session: SessionDep) -> Response:
    await ProductService(session).delete_product(product_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Product deleted successfully"},
    )
