"""Track the users who create and update products."""

from alembic import op
import sqlalchemy as sa


revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("products", sa.Column("created_by_id", sa.Uuid(), nullable=True))
    op.add_column("products", sa.Column("updated_by_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_products_created_by_id_auths",
        "products",
        "auths",
        ["created_by_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_products_updated_by_id_auths",
        "products",
        "auths",
        ["updated_by_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_products_created_by_id", "products", ["created_by_id"])
    op.create_index("ix_products_updated_by_id", "products", ["updated_by_id"])


def downgrade() -> None:
    op.drop_index("ix_products_updated_by_id", table_name="products")
    op.drop_index("ix_products_created_by_id", table_name="products")
    op.drop_constraint("fk_products_updated_by_id_auths", "products", type_="foreignkey")
    op.drop_constraint("fk_products_created_by_id_auths", "products", type_="foreignkey")
    op.drop_column("products", "updated_by_id")
    op.drop_column("products", "created_by_id")
