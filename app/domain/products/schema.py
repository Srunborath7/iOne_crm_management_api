from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class ProductCreate(BaseModel):
    """Fields required to create a product."""

    name: str = Field(min_length=1, max_length=100)
    sku: str = Field(min_length=1, max_length=50)
    model: str | None = Field(default=None, max_length=100)
    description: str | None = None
    brand_id: UUID | None = None
    category_id: UUID | None = None
    condition: Literal["new", "used", "refurbished"] = "new"
    storage: str | None = Field(default=None, max_length=30)
    ram: str | None = Field(default=None, max_length=30)
    color: str | None = Field(default=None, max_length=50)
    operating_system: str | None = Field(default=None, max_length=50)
    screen_size: str | None = Field(default=None, max_length=30)
    battery_capacity: str | None = Field(default=None, max_length=30)
    connectivity: str | None = Field(default=None, max_length=50)
    cost_price: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2)
    selling_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    discount_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0)
    min_stock: int = Field(default=5, ge=0)
    warranty_months: int = Field(default=12, ge=0)
    image_url: str | None = Field(default=None, max_length=500)
    barcode: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    is_active: bool = True

    @model_validator(mode="before")
    @classmethod
    def unwrap_data_envelope(cls, values):
        if isinstance(values, dict) and set(values) == {"data"}:
            return values["data"]
        return values


class ProductUpdate(BaseModel):
    """Fields that may be changed on a product."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    sku: str | None = Field(default=None, min_length=1, max_length=50)
    model: str | None = Field(default=None, max_length=100)
    description: str | None = None
    brand_id: UUID | None = None
    category_id: UUID | None = None
    condition: Literal["new", "used", "refurbished"] | None = None
    storage: str | None = Field(default=None, max_length=30)
    ram: str | None = Field(default=None, max_length=30)
    color: str | None = Field(default=None, max_length=50)
    operating_system: str | None = Field(default=None, max_length=50)
    screen_size: str | None = Field(default=None, max_length=30)
    battery_capacity: str | None = Field(default=None, max_length=30)
    connectivity: str | None = Field(default=None, max_length=50)
    cost_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    selling_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    discount_price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    stock_quantity: int | None = Field(default=None, ge=0)
    min_stock: int | None = Field(default=None, ge=0)
    warranty_months: int | None = Field(default=None, ge=0)
    image_url: str | None = Field(default=None, max_length=500)
    barcode: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None

    @model_validator(mode="before")
    @classmethod
    def unwrap_data_envelope(cls, values):
        if isinstance(values, dict) and set(values) == {"data"}:
            values = values["data"]
        if isinstance(values, dict):
            nullable_fields = {
                "model", "description", "brand_id", "category_id", "storage", "ram",
                "color", "operating_system", "screen_size", "battery_capacity",
                "connectivity", "discount_price", "image_url", "barcode", "manufacturer",
            }
            invalid_nulls = [
                field for field, value in values.items()
                if value is None and field not in nullable_fields
            ]
            if invalid_nulls:
                raise ValueError(
                    f"These fields cannot be null: {', '.join(invalid_nulls)}"
                )
        return values


class ProductAuditUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str


class ProductResponse(BaseModel):
    """Public product representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    sku: str
    model: str | None = None
    description: str | None = None
    brand_id: UUID | None = None
    category_id: UUID | None = None
    condition: str
    storage: str | None = None
    ram: str | None = None
    color: str | None = None
    operating_system: str | None = None
    screen_size: str | None = None
    battery_capacity: str | None = None
    connectivity: str | None = None
    cost_price: Decimal
    selling_price: Decimal
    discount_price: Decimal | None = None
    stock_quantity: int
    min_stock: int
    warranty_months: int
    image_url: str | None = None
    barcode: str | None = None
    manufacturer: str | None = None
    is_active: bool
    created_by_id: UUID | None = None
    updated_by_id: UUID | None = None
    created_by: ProductAuditUser | None = Field(
        default=None,
        validation_alias=AliasChoices("created_by", "creator"),
    )
    updated_by: ProductAuditUser | None = Field(
        default=None,
        validation_alias=AliasChoices("updated_by", "updater"),
    )
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    """Envelope for paginated product lists."""

    message: str
    data: list[ProductResponse]
    total: int
    offset: int
    limit: int


class ProductDetailResponse(BaseModel):
    """Envelope for a single product."""

    message: str
    data: ProductResponse
