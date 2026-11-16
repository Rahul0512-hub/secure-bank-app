from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.accounts import router as accounts_router
from backend.app.analytics import router as analytics_router
from backend.app.auth import router as auth_router
from backend.app.dashboard_ui import router as dashboard_ui_router
from backend.app.loans import router as loans_router
from backend.app.mongodb import get_mongo_client
from backend.app.postgres import get_postgres_connection
from backend.app.transactions import router as transactions_router

app = FastAPI(
    title="SecureBank Enterprise API",
    description="Full-featured, robust, secure digital banking core with dual-engine transactional outbox, pgvector semantic search, and fraud intelligence",
    version="2.0.0",
)

# Enable CORS for rich browser interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(loans_router)
app.include_router(analytics_router)
app.include_router(dashboard_ui_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to SecureBank Enterprise Banking System",
        "version": "2.0.0",
        "status": "operational",
        "documentation": "/docs",
        "web_app": "/dashboard",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SecureBank API",
        "architecture": "PostgreSQL ACID Core + MongoDB Audit Replication",
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

    except Exception as exc:
        return {
            "status": "unhealthy",
            "database": "PostgreSQL",
            "error": str(exc),
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

    except Exception as exc:
        return {
            "status": "unhealthy",
            "database": "MongoDB",
            "error": str(exc),
        }

    finally:
        if client is not None:
            client.close()
