import psycopg

from backend.app.config import settings


def get_postgres_connection():
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg.connect(
        settings.DATABASE_URL,
        connect_timeout=5,
    )
