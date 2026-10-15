from __future__ import annotations

from datetime import datetime
from uuid import UUID
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):
    """Fields required to create a customer."""

    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=10, le=99)
    gender: Literal["male", "female", "other"] = "other"
    phone: str | None = Field(default=None, max_length=15)
    email: EmailStr | None = Field(default=None, max_length=50)
    address: str | None = None
    is_active: bool = True
    note: str | None = None


class CustomerUpdate(BaseModel):
    """Fields that may be changed on a customer."""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    age: int | None = Field(default=None, ge=10, le=99)
    gender: Literal["male", "female", "other"] | None = None
    phone: str | None = Field(default=None, max_length=15)
    email: EmailStr | None = Field(default=None, max_length=50)
    address: str | None = None
    is_active: bool | None = None
    note: str | None = None


class CustomerResponse(BaseModel):
    """Public customer representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    age: int
    gender: str
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    is_active: bool
    note: str | None = None
    created_at: datetime
    updated_at: datetime


class CustomerListResponse(BaseModel):
    """Envelope for paginated customer lists."""

    message: str
    data: list[CustomerResponse]
    total: int
    offset: int
    limit: int


class CustomerDetailResponse(BaseModel):
    """Envelope for a single customer."""

    message: str
    data: CustomerResponse