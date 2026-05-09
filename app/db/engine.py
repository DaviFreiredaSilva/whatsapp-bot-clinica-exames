from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


def _build_url(url: str) -> str:
    if url.startswith("postgresql") or url.startswith("postgres"):
        # Ensure async psycopg driver is used
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
        return url
    # Treat bare filenames as SQLite
    return f"sqlite+aiosqlite:///{url}"


engine = create_async_engine(_build_url(settings.database_url), echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
