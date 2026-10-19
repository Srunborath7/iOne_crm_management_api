import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, UUID, Text, ForeignKey, Numeric, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Products(Base):
    __tablename__ = "products"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    model: Mapped[str | None] = mapped_column(String(100),nullable=True,)
    description: Mapped[str | None] = mapped_column(Text,nullable=True,)
    brand_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True),ForeignKey("brands.id", ondelete="RESTRICT"),nullable=True,index=True,)
    category_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True),ForeignKey("categories.id", ondelete="SET NULL"),nullable=True,index=True,)
    condition: Mapped[str] = mapped_column(String(20),nullable=False,default="new",)
    storage: Mapped[str | None] = mapped_column(String(30),nullable=True)
    ram: Mapped[str | None] = mapped_column(String(30),nullable=True)
    color: Mapped[str | None] = mapped_column(String(50),nullable=True)
    operating_system: Mapped[str | None] = mapped_column(String(50),nullable=True)
    screen_size: Mapped[str | None] = mapped_column(String(30),nullable=True)
    battery_capacity: Mapped[str | None] = mapped_column(String(30),nullable=True)
    connectivity: Mapped[str | None] = mapped_column(String(50),nullable=True)
    cost_price: Mapped[Decimal] = mapped_column( Numeric(12, 2), nullable=False,default=Decimal("0.00"),)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2),nullable=False,)
    discount_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2),nullable=True,)
    stock_quantity: Mapped[int] = mapped_column(Integer,nullable=False,default=0)
    min_stock: Mapped[int] = mapped_column(Integer,nullable=False,default=5,)
    warranty_months: Mapped[int] = mapped_column(Integer,nullable=False,default=12)
    image_url: Mapped[str | None] = mapped_column(String(500),nullable=True)
    barcode: Mapped[str | None] = mapped_column(String(100),nullable=True,unique=True)
    manufacturer: Mapped[str | None] = mapped_column(String(100),nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean,nullable=False,default=True)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auths.id", ondelete="SET NULL"), nullable=True, index=True
    )
    updated_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auths.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,default=lambda: datetime.now(timezone.utc),)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc),)
    # ORM relationships
    brand = relationship("Brands",back_populates="products")
    category = relationship("Categories",back_populates="products")
    creator = relationship("Auths", foreign_keys=[created_by_id])
    updater = relationship("Auths", foreign_keys=[updated_by_id])
