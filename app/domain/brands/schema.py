from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BrandCreate(BaseModel):
    """Brand text fields supplied alongside the image in the multipart form."""

    name: str = Field(min_length=1, max_length=50)
    description: str | None = None


class BrandUpdate(BaseModel):
    """Fields that may be changed on a brand."""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None


class BrandResponse(BaseModel):
    """Public brand representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime


class BrandListItem(BaseModel):
    """Compact representation returned by the brand list endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None


class BrandWithImageItem(BaseModel):
    """Brand list representation that includes the image URL."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None
    image_url: str | None = None


class BrandListResponse(BaseModel):
    message: str
    data: list[BrandListItem]
    total: int
    offset: int
    limit: int


class BrandImageListResponse(BaseModel):
    message: str
    data: list[BrandWithImageItem]
    total: int
    offset: int
    limit: int


class BrandDetailResponse(BaseModel):
    message: str
    data: BrandResponse


