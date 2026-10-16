import asyncio

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.database import Base, DATABASE_URL
from app.domain.auth import model as auth_models  # noqa: F401 - registers mapped models
from app.domain.customers import model as customer_models  # noqa: F401 - registers mapped models

config = context.config


def get_url() -> str:
    # str() on a SQLAlchemy URL object renders the password as "***",
    # so render it explicitly when DATABASE_URL is a URL object.
    if isinstance(DATABASE_URL, URL):
        url = DATABASE_URL.render_as_string(hide_password=False)
    else:
        url = str(DATABASE_URL)

    # asyncpg needs the +asyncpg driver in the scheme
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


url = get_url()

config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        # Only needed if you use Supabase's transaction pooler (port 6543).
        # Harmless on the session pooler / direct connection.
        connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0},
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
