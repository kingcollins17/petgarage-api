from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from src.core.config import config

# ──────────────────────────────────────────────────────────────────────────────
# Build the async database URL from environment variables.
#
#   DB_TYPE=mysql    → uses asyncmy driver  (mysql+asyncmy://...)
#   DB_TYPE=postgres → uses asyncpg driver  (postgresql+asyncpg://...)
#
# Set DB_TYPE (and the other DB_* variables) in your .env file.
# ──────────────────────────────────────────────────────────────────────────────

_db_type = config.DB_TYPE.lower().strip()

if _db_type == "postgres":
    DATABASE_URL = (
        f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASSWORD}"
        f"@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    )
elif _db_type == "mysql":
    DATABASE_URL = (
        f"mysql+asyncmy://{config.DB_USER}:{config.DB_PASSWORD}"
        f"@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    )
else:
    raise ValueError(
        f"Unsupported DB_TYPE '{config.DB_TYPE}'. "
        "Valid values are: 'mysql', 'postgres'."
    )

engine = create_async_engine(DATABASE_URL, echo=config.APP_DEBUG)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
