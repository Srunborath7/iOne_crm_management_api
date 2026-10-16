"""Create role_users.

Revision ID: 001
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if sa.inspect(bind).has_table("role_users"):
        return

    op.create_table(
        "role_users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=10), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )


def downgrade() -> None:
    op.drop_table("role_users")
