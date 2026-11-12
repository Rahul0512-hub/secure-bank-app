from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from bson.decimal128 import Decimal128
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.app.mongodb import (
    get_audit_collection,
    get_fraud_alerts_collection,
    get_login_events_collection,
    get_mongo_client,
)
from backend.app.postgres import get_postgres_connection

router = APIRouter(prefix="/api/person-b", tags=["Person B - Analytics, Fraud & Vector Search"])


class SimulateEventRequest(BaseModel):
    user_id: int = 1
    amount: float
    category: str
    description: str


class LoginEventRequest(BaseModel):
    user_id: Optional[int] = None
    email: str
    ip_address: str = "127.0.0.1"
    status: str = "SUCCESS"


def text_to_embedding(query: str) -> str:
    """Converts natural language search query into a 4D semantic vector [Food, Travel, Bills, Security]."""
    q = query.lower()
    if any(w in q for w in ["coffee", "food", "dinner", "swiggy", "starbucks", "eat", "snack", "lunch"]):
        return "[0.95, 0.05, 0.05, 0.02]"
    if any(w in q for w in ["uber", "cab", "flight", "airport", "travel", "trip", "indigo", "taxi"]):
        return "[0.05, 0.96, 0.04, 0.02]"
    if any(w in q for w in ["bill", "electricity", "utility", "bescom", "rent", "recharge", "limit"]):
        return "[0.02, 0.03, 0.95, 0.10]"
    return "[0.02, 0.02, 0.08, 0.97]"


@router.get("/analytics/spending")
def get_spending_analytics():
    """MongoDB Aggregation Pipeline for spending analytics across audit logs and fraud alerts."""
    client = None
    try:
        client = get_mongo_client()
        audit_col = get_audit_collection(client)
        fraud_col = get_fraud_alerts_collection(client)
        login_col = get_login_events_collection(client)

        # 1. Aggregation Pipeline: Group transaction_audit_logs by event_type / status
        audit_pipeline = [
            {
                "$group": {
                    "_id": "$event_type",
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1},
                }
            },
            {"$sort": {"total_amount": -1}},
        ]
        audit_summary = []
        for doc in audit_col.aggregate(audit_pipeline):
            amt = doc.get("total_amount", 0)
            if isinstance(amt, Decimal128):
                amt = float(amt.to_decimal())
            audit_summary.append({
                "category": doc["_id"] or "OTHER",
                "totalSpent": round(float(amt), 2),
                "count": doc["transaction_count"],
            })

        # 2. Fetch active fraud alerts
        alerts = []
        for alert in fraud_col.find().sort("created_at", -1).limit(15):
            amt = alert.get("amount", 0)
            if isinstance(amt, Decimal128):
                amt = float(amt.to_decimal())
            alerts.append({
                "id": str(alert["_id"]),
                "user_id": alert.get("user_id"),
                "amount": float(amt),
                "category": alert.get("category", "Transfer"),
                "reason": alert.get("reason"),
                "severity": alert.get("severity"),
                "status": alert.get("status"),
                "created_at": alert.get("created_at").isoformat() if alert.get("created_at") else None,
            })

        # 3. Fetch recent login events
        logins = []
        for ev in login_col.find().sort("occurred_at", -1).limit(10):
            logins.append({
                "email": ev.get("email"),
                "ip_address": ev.get("ip_address"),
                "status": ev.get("status"),
                "occurred_at": ev.get("occurred_at").isoformat() if ev.get("occurred_at") else None,
            })

        return {
            "spendingByCategory": audit_summary,
            "fraudAlerts": alerts,
            "loginEvents": logins,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if client:
            client.close()


@router.post("/fraud/evaluate")
def evaluate_transaction_fraud(payload: SimulateEventRequest):
    """Real-time Fraud Detection Engine + Audit Log writer."""
    client = None
    try:
        client = get_mongo_client()
        audit_col = get_audit_collection(client)
        fraud_col = get_fraud_alerts_collection(client)
        now = datetime.now(timezone.utc)

        # 1. Insert into Rahul's transaction_audit_logs following his strict schema
        tx_id = int(now.timestamp())
        audit_col.insert_one({
            "transaction_id": tx_id,
            "event_type": "TRANSFER_COMPLETED",
            "status": "SUCCESS",
            "source_account_id": 1,
            "destination_account_id": 2,
            "amount": Decimal128(Decimal(str(payload.amount))),
            "currency": "INR",
            "occurred_at": now,
            "actor_user_id": payload.user_id,
            "description": f"[{payload.category}] {payload.description}",
        })

        # 2. Run Fraud Detection Rules
        fraud_triggered = False
        severity = "LOW"
        reason = None

        if payload.amount >= 50000:
            fraud_triggered = True
            severity = "HIGH" if payload.amount < 100000 else "CRITICAL"
            reason = f"High-value {payload.category} transfer of ₹{payload.amount:,.2f} exceeds ₹50,000 threshold"
        elif "international" in payload.category.lower() or "crypto" in payload.description.lower():
            fraud_triggered = True
            severity = "MEDIUM"
            reason = f"Suspicious merchant/category pattern detected: {payload.description}"

        if fraud_triggered:
            fraud_col.insert_one({
                "transaction_id": tx_id,
                "user_id": payload.user_id,
                "amount": float(payload.amount),
                "category": payload.category,
                "reason": reason,
                "severity": severity,
                "status": "OPEN",
                "created_at": now,
            })

        return {
            "status": "processed",
            "transaction_id": tx_id,
            "fraud_triggered": fraud_triggered,
            "severity": severity if fraud_triggered else "NONE",
            "reason": reason,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if client:
            client.close()


@router.post("/login-events")
def record_login_event(payload: LoginEventRequest):
    """Logs user authentication attempts into MongoDB login_events collection."""
    client = None
    try:
        client = get_mongo_client()
        login_col = get_login_events_collection(client)
        now = datetime.now(timezone.utc)

        login_col.insert_one({
            "user_id": payload.user_id,
            "email": payload.email,
            "ip_address": payload.ip_address,
            "user_agent": "SecureBank-Web-Dashboard",
            "status": payload.status,
            "occurred_at": now,
        })

        # If 3+ failed logins recently, trigger a fraud alert!
        if payload.status == "FAILED":
            recent_fails = login_col.count_documents({"email": payload.email, "status": "FAILED"})
            if recent_fails >= 3:
                get_fraud_alerts_collection(client).insert_one({
                    "transaction_id": None,
                    "user_id": payload.user_id or 0,
                    "amount": 0.0,
                    "category": "Account Takeover",
                    "reason": f"Brute-force alert: {recent_fails} failed login attempts for {payload.email}",
                    "severity": "CRITICAL",
                    "status": "OPEN",
                    "created_at": now,
                })

        return {"status": "logged"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if client:
            client.close()


@router.get("/semantic-search")
def semantic_vector_search(q: str = Query(..., description="Natural language search query")):
    """Performs pgvector cosine distance (<=>) semantic search over transactions and FAQs."""
    query_vector = text_to_embedding(q)
    try:
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, item_type, category, title, description, amount,
                           ROUND((1 - (embedding <=> %s::vector))::numeric, 4) AS similarity_score
                    FROM semantic_search_items
                    ORDER BY embedding <=> %s::vector ASC
                    LIMIT 5;
                    """,
                    (query_vector, query_vector),
                )
                rows = cur.fetchall()
                results = []
                for r in rows:
                    results.append({
                        "id": r[0],
                        "item_type": r[1],
                        "category": r[2],
                        "title": r[3],
                        "description": r[4],
                        "amount": float(r[5]) if r[5] is not None else None,
                        "similarity": float(r[6]),
                    })
                return {"query": q, "results": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"pgvector search error: {exc}")