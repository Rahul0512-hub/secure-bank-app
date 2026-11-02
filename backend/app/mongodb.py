from pymongo import MongoClient

from backend.app.config import settings


def get_mongo_client() -> MongoClient:
    if not settings.MONGODB_AUDIT_URI:
        raise RuntimeError("MONGODB_AUDIT_URI is not configured")

    return MongoClient(
        settings.MONGODB_AUDIT_URI,
        authMechanism="SCRAM-SHA-256",
        serverSelectionTimeoutMS=5000,
    )


def get_audit_collection(client: MongoClient):
    return client["securebank_audit"]["transaction_audit_logs"]
