from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.config import config
from src.core.db_connection import init_db
from src.core.models import *  # Ensure all models are registered
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    await init_db()
    yield

app = FastAPI(
    title=config.APP_NAME, 
    debug=config.APP_DEBUG,
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to PetGarage API",
        "app_name": config.APP_NAME,
        "database": config.DB_NAME,
    }
