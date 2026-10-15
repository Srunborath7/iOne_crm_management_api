
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from app.core.database import Base, engine
from app.api.v1 import router as v1_router
from app.domain.auth import model as auth_models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="CRM Management API", lifespan=lifespan)
app.include_router(v1_router, prefix="/api/v1")

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
