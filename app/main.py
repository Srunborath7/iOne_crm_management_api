
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.database import Base, engine
from app.core.upload import get_upload_dir
from app.api.v1 import router as v1_router
from app.domain.auth import model as auth_models  # noqa: F401
from app.domain.brands import model as brand_models  # noqa: F401
from app.domain.customers import model as customer_models  # noqa: F401
from app.domain.categories import model as category_models
from app.domain.products import model as product_models
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified successfully.")
    except Exception as exc:
        logger.error("Could not connect to the database on startup: %s", exc)
        raise
    yield


app = FastAPI(title="CRM Management API", lifespan=lifespan)
app.mount(
    "/uploads",
    StaticFiles(directory=str(get_upload_dir()), check_dir=False),
    name="uploads",
)
app.include_router(v1_router, prefix="/api/v1")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://i-one-crm-management-website.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CRM Management API is running"}


@app.get("/db-check")
async def db_check():
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT current_database()"))
        database_name = result.scalar_one()

    return {
        "status": "connected",
        "database": database_name,
    }
