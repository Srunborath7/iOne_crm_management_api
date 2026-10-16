"""Create auths and seed the initial administrator.

Revision ID: 002
Revises: 001
"""

from uuid import uuid4
import os

from alembic import op
import sqlalchemy as sa
from app.core.security import hash_password


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

ADMIN_EMAIL = "borath@gmail.com"
ADMIN_ROLE_NAME = "admin"


def upgrade() -> None:
    bind = op.get_bind()
    if not sa.inspect(bind).has_table("auths"):
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

    role_id = bind.execute(
        sa.select(roles.c.id).where(roles.c.name == ADMIN_ROLE_NAME)
    ).scalar_one_or_none()
    if role_id is None:
        role_id = uuid4()
        bind.execute(
            sa.insert(roles).values(
                id=role_id,
                name=ADMIN_ROLE_NAME,
                note="System administrator",
            )
        )

    admin_exists = bind.execute(
        sa.select(users.c.id).where(users.c.email == ADMIN_EMAIL)
    ).first()
    if admin_exists is None:
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD")
        if not admin_password:
            raise RuntimeError(
                "DEFAULT_ADMIN_PASSWORD must be set to seed the admin user"
            )
        bind.execute(
            sa.insert(users).values(
                id=uuid4(),
                username="Borath",
                email=ADMIN_EMAIL,
                password=hash_password(admin_password),
                user_role=role_id,
            )
        )


def downgrade() -> None:
    bind = op.get_bind()
    auths = sa.table("auths", sa.column("email", sa.String()))
    roles = sa.table("role_users", sa.column("name", sa.String()))
    bind.execute(sa.delete(auths).where(auths.c.email == ADMIN_EMAIL))
    bind.execute(sa.delete(roles).where(roles.c.name == ADMIN_ROLE_NAME))
    op.drop_table("auths")
