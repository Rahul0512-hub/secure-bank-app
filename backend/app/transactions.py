from datetime import datetime, timezone
from decimal import Decimal

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.app.dependencies import get_current_user
from backend.app.mongodb import get_fraud_alerts_collection, get_mongo_client
from backend.app.postgres import get_postgres_connection


router = APIRouter(prefix="/transactions", tags=["Transactions"])


class TransferRequest(BaseModel):
    source_account_id: int = Field(gt=0)
    destination_account_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=19, decimal_places=4)
    description: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default="Transfer", max_length=50)


def require_customer(current_user: dict) -> None:
    if current_user["role"] != "Customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required",
        )


def format_transaction(row: tuple) -> dict:
    (
        transaction_id,
        source_account_id,
        destination_account_id,
        amount,
        transaction_type,
        description,
        transaction_status,
        created_at,
    ) = row

    return {
        "transaction_id": transaction_id,
        "source_account_id": source_account_id,
        "destination_account_id": destination_account_id,
        "amount": str(Decimal(amount)),
        "transaction_type": transaction_type,
        "description": description,
        "status": transaction_status,
        "created_at": created_at,
    }


def evaluate_transfer_fraud_and_alert(user_id: int, transaction_id: int, amount: float, category: str, description: str | None):
    """Real-time fraud detection engine hooks."""
    desc_clean = (description or "").lower()
    cat_clean = (category or "").lower()

    fraud_triggered = False
    severity = "LOW"
    reason = None

    if amount >= 50000:
        fraud_triggered = True
        severity = "HIGH" if amount < 100000 else "CRITICAL"
        reason = f"High-velocity transfer of ₹{amount:,.2f} exceeds ₹50,000 threshold"
    elif any(k in desc_clean or k in cat_clean for k in ["crypto", "offshore", "gambling", "hawala"]):
        fraud_triggered = True
        severity = "HIGH"
        reason = f"High-risk keyword pattern detected in payment memo: '{description}'"

    if fraud_triggered:
        try:
            client = get_mongo_client()
            fraud_col = get_fraud_alerts_collection(client)
            fraud_col.insert_one({
                "transaction_id": transaction_id,
                "user_id": user_id,
                "amount": float(amount),
                "category": category,
                "reason": reason,
                "severity": severity,
                "status": "OPEN",
                "created_at": datetime.now(timezone.utc),
            })
            client.close()
        except Exception:
            pass

    return fraud_triggered, severity, reason


@router.get("/me")
def get_my_transactions(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    require_customer(current_user)

    user_id = current_user["user_id"]

    try:
        with get_postgres_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    t.transaction_id,
                    t.source_account_id,
                    t.destination_account_id,
                    t.amount,
                    t.transaction_type,
                    t.description,
                    t.status,
                    t.created_at
                FROM public.transactions AS t
                JOIN public.accounts AS source
                    ON source.account_id = t.source_account_id
                JOIN public.accounts AS destination
                    ON destination.account_id = t.destination_account_id
                WHERE source.user_id = %s
                   OR destination.user_id = %s
                ORDER BY t.created_at DESC, t.transaction_id DESC
                LIMIT %s OFFSET %s
                """,
                (user_id, user_id, limit, offset),
            ).fetchall()

            total = connection.execute(
                """
                SELECT COUNT(*)
                FROM public.transactions AS t
                JOIN public.accounts AS source
                    ON source.account_id = t.source_account_id
                JOIN public.accounts AS destination
                    ON destination.account_id = t.destination_account_id
                WHERE source.user_id = %s
                   OR destination.user_id = %s
                """,
                (user_id, user_id),
            ).fetchone()[0]
    except psycopg.OperationalError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banking service is temporarily unavailable. Please try again later.",
        )

    return {
        "transactions": [format_transaction(row) for row in rows],
        "count": len(rows),
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/stats")
def get_transaction_stats(current_user: dict = Depends(get_current_user)):
    """Summary of debits, credits, and transaction volume for customer."""
    require_customer(current_user)
    user_id = current_user["user_id"]

    with get_postgres_connection() as connection:
        sent_row = connection.execute(
            """
            SELECT COALESCE(SUM(t.amount), 0), COUNT(t.transaction_id)
            FROM public.transactions t
            JOIN public.accounts s ON s.account_id = t.source_account_id
            WHERE s.user_id = %s;
            """,
            (user_id,)
        ).fetchone()

        received_row = connection.execute(
            """
            SELECT COALESCE(SUM(t.amount), 0), COUNT(t.transaction_id)
            FROM public.transactions t
            JOIN public.accounts d ON d.account_id = t.destination_account_id
            WHERE d.user_id = %s;
            """,
            (user_id,)
        ).fetchone()

    return {
        "total_sent": str(Decimal(sent_row[0])),
        "sent_count": sent_row[1],
        "total_received": str(Decimal(received_row[0])),
        "received_count": received_row[1],
    }


@router.get("/{transaction_id}")
def get_transaction(
    transaction_id: int,
    current_user: dict = Depends(get_current_user),
):
    require_customer(current_user)

    if transaction_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    user_id = current_user["user_id"]

    try:
        with get_postgres_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    t.transaction_id,
                    t.source_account_id,
                    t.destination_account_id,
                    t.amount,
                    t.transaction_type,
                    t.description,
                    t.status,
                    t.created_at
                FROM public.transactions AS t
                JOIN public.accounts AS source
                    ON source.account_id = t.source_account_id
                JOIN public.accounts AS destination
                    ON destination.account_id = t.destination_account_id
                WHERE t.transaction_id = %s
                  AND (source.user_id = %s OR destination.user_id = %s)
                """,
                (transaction_id, user_id, user_id),
            ).fetchone()
    except psycopg.OperationalError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banking service is temporarily unavailable. Please try again later.",
        )

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return {"transaction": format_transaction(row)}


@router.post("/transfer", status_code=status.HTTP_201_CREATED)
def transfer_funds(
    request: TransferRequest,
    current_user: dict = Depends(get_current_user),
):
    require_customer(current_user)

    if request.source_account_id == request.destination_account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source and destination accounts must be different",
        )

    user_id = current_user["user_id"]

    try:
        with get_postgres_connection() as connection:
            source = connection.execute(
                """
                SELECT account_id
                FROM public.accounts
                WHERE account_id = %s AND user_id = %s
                """,
                (request.source_account_id, user_id),
            ).fetchone()

            if source is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Source account not found",
                )

            transaction_id = connection.execute(
                """
                SELECT public.transfer_funds(%s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    request.source_account_id,
                    request.destination_account_id,
                    request.amount,
                    "Transfer",
                    request.description,
                ),
            ).fetchone()[0]

    except HTTPException:
        raise

    except psycopg.OperationalError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banking service is temporarily unavailable. Please try again later.",
        )

    except psycopg.errors.RaiseException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Transfer could not be completed. Verify the destination "
                "account, account status, currency, and available balance."
            ),
        )

    except psycopg.Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred.",
        )

    # Evaluate real-time fraud checks
    fraud_flag, severity, reason = evaluate_transfer_fraud_and_alert(
        user_id=user_id,
        transaction_id=transaction_id,
        amount=float(request.amount),
        category=request.category or "Transfer",
        description=request.description,
    )

    return {
        "message": "Transfer completed successfully",
        "transaction_id": transaction_id,
        "status": "Completed",
        "fraud_alert": {
            "triggered": fraud_flag,
            "severity": severity if fraud_flag else "NONE",
            "reason": reason,
        } if fraud_flag else None,
    }
