from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    """Category text fields supplied alongside the image in the multipart form."""

    name: str = Field(min_length=1, max_length=50)
    description: str | None = None


class CategoryUpdate(BaseModel):
    """Fields that may be changed on a Category."""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None


class CategoryResponse(BaseModel):
    """Public Category representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime


class CategoryListItem(BaseModel):
    """Compact representation returned by the Category list endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None


class CategoryWithImageItem(BaseModel):
    """Category list representation that includes the image URL."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    image_url: str | None = None


class CategoryListResponse(BaseModel):
    message: str
    data: list[CategoryListItem]
    total: int
    offset: int
    limit: int


class CategoryImageListResponse(BaseModel):
    message: str
    data: list[CategoryWithImageItem]
    total: int
    offset: int
    limit: int


class CategoryDetailResponse(BaseModel):
    message: str
    data: CategoryResponse


