"""Create auths and seed the initial administrator.

Revision ID: 002
Revises: 001
"""

from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

ADMIN_EMAIL = "borath@gmail.com"
ADMIN_ROLE_NAME = "admin"


def upgrade() -> None:
    op.create_table(
        "auths",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=50), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("user_role", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_role"], ["role_users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    role_id = uuid4()
    roles = sa.table(
        "role_users",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("note", sa.String()),
    )
    users = sa.table(
        "auths",
        sa.column("id", sa.Uuid()),
        sa.column("username", sa.String()),
        sa.column("email", sa.String()),
        sa.column("password", sa.String()),
        sa.column("user_role", sa.Uuid()),
    )

    op.bulk_insert(
        roles,
        [{"id": role_id, "name": ADMIN_ROLE_NAME, "note": "System administrator"}],
    )
    op.bulk_insert(
        users,
        [{
            "id": uuid4(),
            "username": "Borath",
            "email": ADMIN_EMAIL,
            # Replace the example value with a real password hash before deployment.
            "password": "12345",
            "user_role": role_id,
        }],
    )


def downgrade() -> None:
    bind = op.get_bind()
    auths = sa.table("auths", sa.column("email", sa.String()))
    roles = sa.table("role_users", sa.column("name", sa.String()))
    bind.execute(sa.delete(auths).where(auths.c.email == ADMIN_EMAIL))
    bind.execute(sa.delete(roles).where(roles.c.name == ADMIN_ROLE_NAME))
    op.drop_table("auths")
