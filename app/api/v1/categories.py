from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.domain.categories.schema import (
    CategoryCreate,
    CategoryDetailResponse,
    CategoryImageListResponse,
    CategoryListItem,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
    CategoryWithImageItem,
)
from app.services.category_service import CategoryService


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    dependencies=[Depends(get_current_user)],
)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


@router.post("/", response_model=CategoryDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_Category(
    session: SessionDep,
    name: Annotated[str, Form(min_length=1, max_length=50)],
    image: Annotated[UploadFile, File()],
    description: Annotated[str | None, Form()] = None,
) -> CategoryDetailResponse:
    data = CategoryCreate(name=name, description=description)
    Category = await CategoryService(session).create_Category(data, image)
    return CategoryDetailResponse(
        message="Category created successfully",
        data=CategoryResponse.model_validate(Category),
    )


@router.get("/", response_model=CategoryListResponse)
async def list_Categorys(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> CategoryListResponse:
    Category, total = await CategoryService(session).list_Categories(offset, limit)
    return CategoryListResponse(
        message="Categorys retrieved successfully",
        data=[CategoryListItem.model_validate(Category) for Category in Category],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/image", response_model=CategoryImageListResponse)
async def list_Categorys_with_image(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> CategoryImageListResponse:
    Category, total = await CategoryService(session).list_Categories(offset, limit)
    return CategoryImageListResponse(
        message="Categorys with images retrieved successfully",
        data=[CategoryWithImageItem.model_validate(Category) for Category in Category],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{category_id}", response_model=CategoryDetailResponse)
async def get_Category(Category_id: UUID, session: SessionDep) -> CategoryDetailResponse:
    Category = await CategoryService(session).get_Category(Category_id)
    return CategoryDetailResponse(
        message="Category retrieved successfully",
        data=CategoryResponse.model_validate(Category),
    )


@router.patch("/{category_id}", response_model=CategoryDetailResponse)
async def update_Category(
    Category_id: UUID,
    session: SessionDep,
    name: Annotated[str | None, Form(min_length=1, max_length=50)] = None,
    description: Annotated[str | None, Form()] = None,
    image: Annotated[UploadFile | None, File()] = None,
) -> CategoryDetailResponse:
    fields = {
        key: value
        for key, value in {"name": name, "description": description}.items()
        if value is not None
    }
    data = CategoryUpdate.model_validate(fields)
    Category = await CategoryService(session).update_Category(Category_id, data, image)
    return CategoryDetailResponse(
        message="Category updated successfully",
        data=CategoryResponse.model_validate(Category),
    )


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
async def delete_Category(Category_id: UUID, session: SessionDep) -> Response:
    await CategoryService(session).delete_Category(Category_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Category deleted successfully"},
    )
