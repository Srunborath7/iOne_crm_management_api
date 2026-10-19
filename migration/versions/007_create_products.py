"""Create products."""

from alembic import op
import sqlalchemy as sa


revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if sa.inspect(bind).has_table("products"):
        return

    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("sku", sa.String(length=50), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("brand_id", sa.Uuid(), nullable=True),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column(
            "condition",
            sa.String(length=20),
            nullable=False,
            server_default="new",
        ),
        sa.Column("storage", sa.String(length=30), nullable=True),
        sa.Column("ram", sa.String(length=30), nullable=True),
        sa.Column("color", sa.String(length=50), nullable=True),
        sa.Column("operating_system", sa.String(length=50), nullable=True),
        sa.Column("screen_size", sa.String(length=30), nullable=True),
        sa.Column("battery_capacity", sa.String(length=30), nullable=True),
        sa.Column("connectivity", sa.String(length=50), nullable=True),
        sa.Column(
            "cost_price",
            sa.Numeric(12, 2),
            nullable=False,
            server_default="0.00",
        ),
        sa.Column("selling_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_price", sa.Numeric(12, 2), nullable=True),
        sa.Column(
            "stock_quantity",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "min_stock",
            sa.Integer(),
            nullable=False,
            server_default="5",
        ),
        sa.Column(
            "warranty_months",
            sa.Integer(),
            nullable=False,
            server_default="12",
        ),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("barcode", sa.String(length=100), nullable=True),
        sa.Column("manufacturer", sa.String(length=100), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku"),
        sa.UniqueConstraint("barcode"),
    )
    op.create_index("ix_products_brand_id", "products", ["brand_id"])
    op.create_index("ix_products_category_id", "products", ["category_id"])


def downgrade() -> None:
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_index("ix_products_brand_id", table_name="products")
    op.drop_table("products")
