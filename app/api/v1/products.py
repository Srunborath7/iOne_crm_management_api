import json
from typing import Annotated, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile as StarletteUploadFile

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
)
SessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[Auths, Depends(get_current_user)]
ModelT = TypeVar("ModelT", bound=BaseModel)
AuthDep = Depends(get_current_user)

async def parse_product_input(
    request: Request, schema: type[ModelT]
) -> tuple[ModelT, StarletteUploadFile | None]:
    """Read JSON or multipart input, including JSON in a multipart `data` field."""
    content_type = request.headers.get("content-type", "")
    upload = None

    try:
        if "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
            form = await request.form()
            upload_value = form.get("image")
            if isinstance(upload_value, StarletteUploadFile):
                upload = upload_value

            raw_data = form.get("data")
            if isinstance(raw_data, str):
                payload = json.loads(raw_data)
            else:
                payload = {
                    key: value
                    for key, value in form.items()
                    if key != "image" and not isinstance(value, StarletteUploadFile)
                }
        elif "application/json" in content_type:
            payload = await request.json()
        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Send application/json or multipart/form-data.",
            )
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The multipart 'data' field must contain valid JSON.",
        ) from exc

    try:
        return schema.model_validate(payload), upload
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(include_input=False),
        ) from exc


@router.post(
    "/",
    response_model=ProductDetailResponse,
    status_code=status.HTTP_201_CREATED,dependencies=[AuthDep],
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": ProductCreate.model_json_schema(),
                },
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            **ProductCreate.model_json_schema()["properties"],
                            "image": {"type": "string", "format": "binary"},
                        },
                        "required": ProductCreate.model_json_schema().get("required", []),
                    },
                },
            },
        }
    },
)
async def create_product(
    request: Request,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> ProductDetailResponse:
    data, image = await parse_product_input(request, ProductCreate)
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


@router.patch(
    "/{product_id}",
    response_model=ProductDetailResponse,dependencies=[AuthDep],
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": ProductUpdate.model_json_schema(),
                },
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            **ProductUpdate.model_json_schema()["properties"],
                            "image": {"type": "string", "format": "binary"},
                        },
                    },
                },
            },
        }
    },
)
async def update_product(
    product_id: UUID,
    request: Request,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> ProductDetailResponse:
    data, image = await parse_product_input(request, ProductUpdate)
    product = await ProductService(session).update_product(
        product_id, data, current_user, image
    )
    return ProductDetailResponse(
        message="Product updated successfully",
        data=ProductResponse.model_validate(product),
    )


@router.delete("/{product_id}", status_code=status.HTTP_200_OK,dependencies=[AuthDep])
async def delete_product(product_id: UUID, session: SessionDep) -> Response:
    await ProductService(session).delete_product(product_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Product deleted successfully"},
    )
