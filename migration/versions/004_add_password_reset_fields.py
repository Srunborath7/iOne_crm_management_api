"""Add password reset token fields to auths."""

from alembic import op
import sqlalchemy as sa


revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "auths", sa.Column("password_reset_token_hash", sa.String(length=64))
    )
    op.add_column(
        "auths", sa.Column("password_reset_expires_at", sa.DateTime(timezone=True))
    )


def downgrade() -> None:
    op.drop_column("auths", "password_reset_expires_at")
    op.drop_column("auths", "password_reset_token_hash")
