from fastapi import FastAPI

from backend.app.mongodb import get_mongo_client
from backend.app.postgres import get_postgres_connection

app = FastAPI(
    title="SecureBank API",
    description="Backend API for the SecureBank application",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to SecureBank API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SecureBank API",
    }


@app.get("/health/postgres")
def postgres_health_check():
    try:
        with get_postgres_connection() as connection:
            connection.execute("SELECT 1")

        return {
            "status": "healthy",
            "database": "PostgreSQL",
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "PostgreSQL",
        }


@app.get("/health/mongodb")
def mongodb_health_check():
    client = None

    try:
        client = get_mongo_client()
        client.admin.command("ping")

        collection = client["securebank_audit"]["transaction_audit_logs"]
        collection.list_indexes()

        return {
            "status": "healthy",
            "database": "MongoDB",
            "collection": "transaction_audit_logs",
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "MongoDB",
        }

    finally:
        if client is not None:
            client.close()
