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

from src.features.accounts.routers import auth_router, accounts_router
from src.features.products.routers import products_router, categories_router
from src.features.permissions.routers import permissions_router, permission_groups_router, assignments_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=config.APP_NAME, 
    debug=config.APP_DEBUG,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=config.API_V1_STR)
app.include_router(accounts_router, prefix=config.API_V1_STR)
app.include_router(products_router, prefix=config.API_V1_STR)
app.include_router(categories_router, prefix=config.API_V1_STR)
app.include_router(permissions_router, prefix=config.API_V1_STR)
app.include_router(permission_groups_router, prefix=config.API_V1_STR)
app.include_router(assignments_router, prefix=config.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "Welcome to PetGarage API",
        "app_name": config.APP_NAME,
        "database": config.DB_NAME,
    }
