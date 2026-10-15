
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.engine import make_url

load_dotenv()

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL must be configured")

parsed_database_url = make_url(database_url)
# Render and other PaaS providers may use "postgres://" or "postgresql://".
# Both need to be rewritten to "postgresql+asyncpg://" for async support.
if parsed_database_url.drivername in {"postgres", "postgresql"}:
    parsed_database_url = parsed_database_url.set(drivername="postgresql+asyncpg")
DATABASE_URL = parsed_database_url

# Render PostgreSQL requires SSL for external connections.
connect_args: dict = {}
if "render.com" in (parsed_database_url.host or "") or os.getenv("RENDER"):
    connect_args["ssl"] = True

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
