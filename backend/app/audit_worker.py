import argparse
import logging
import time
from datetime import datetime
from decimal import Decimal

import psycopg
from bson.decimal128 import Decimal128
from pymongo.errors import PyMongoError

from backend.app.config import settings
from backend.app.mongodb import get_audit_collection, get_mongo_client


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("securebank.audit_worker")


def build_audit_document(outbox_id, payload):
    """Convert an outbox payload into the MongoDB audit schema."""
    if not isinstance(payload, dict):
        raise ValueError("Outbox payload must be a JSON object")

    required = (
        "transaction_id",
        "event_type",
        "status",
        "amount",
        "occurred_at",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise ValueError(f"Missing payload fields: {', '.join(missing)}")

    occurred_at = payload["occurred_at"]
    if isinstance(occurred_at, str):
        occurred_at = datetime.fromisoformat(
            occurred_at.replace("Z", "+00:00")
        )

    if occurred_at.tzinfo is None:
        raise ValueError("occurred_at must include a timezone")

    document = {
        "_id": str(outbox_id),
        "transaction_id": int(payload["transaction_id"]),
        "event_type": str(payload["event_type"]),
        "status": str(payload["status"]),
        "amount": Decimal128(Decimal(str(payload["amount"]))),
        "occurred_at": occurred_at,
    }

    optional_fields = (
        "source_account_id",
        "destination_account_id",
        "currency",
        "actor_user_id",
        "description",
    )

    for field in optional_fields:
        value = payload.get(field)
        if value is not None:
            if field in (
                "source_account_id",
                "destination_account_id",
                "actor_user_id",
            ):
                value = int(value)
            else:
                value = str(value)
            document[field] = value

    return document


def process_batch(connection, collection, batch_size=20):
    """Process one batch while safely locking pending outbox rows."""
    delivered = 0
    failed = 0

    with connection.transaction():
        events = connection.execute(
            """
            SELECT outbox_id, payload
            FROM public.transaction_audit_outbox
            WHERE delivered_at IS NULL
            ORDER BY created_at, outbox_id
            LIMIT %s
            FOR UPDATE SKIP LOCKED
            """,
            (batch_size,),
        ).fetchall()

        for outbox_id, payload in events:
            try:
                document = build_audit_document(outbox_id, payload)

                collection.replace_one(
                    {"_id": str(outbox_id)},
                    document,
                    upsert=True,
                )

                connection.execute(
                    """
                    UPDATE public.transaction_audit_outbox
                    SET delivered_at = CURRENT_TIMESTAMP,
                        attempts = attempts + 1,
                        last_error = NULL
                    WHERE outbox_id = %s
                    """,
                    (outbox_id,),
                )

                delivered += 1
                logger.info("Delivered audit event %s", outbox_id)

            except (PyMongoError, ValueError, TypeError, ArithmeticError) as exc:
                connection.execute(
                    """
                    UPDATE public.transaction_audit_outbox
                    SET attempts = attempts + 1,
                        last_error = %s
                    WHERE outbox_id = %s
                    """,
                    (str(exc)[:2000], outbox_id),
                )

                failed += 1
                logger.exception("Could not deliver audit event %s", outbox_id)

    return len(events), delivered, failed


def main():
    parser = argparse.ArgumentParser(
        description="SecureBank PostgreSQL-to-MongoDB audit worker"
    )
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--poll-seconds", type=float, default=5)
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process one batch and exit",
    )
    args = parser.parse_args()

    if args.batch_size < 1:
        parser.error("--batch-size must be at least 1")
    if args.poll_seconds <= 0:
        parser.error("--poll-seconds must be greater than 0")

    if not settings.AUDIT_WORKER_DATABASE_URL:
        raise RuntimeError("AUDIT_WORKER_DATABASE_URL is not configured")

    if not settings.MONGODB_AUDIT_URI:
        raise RuntimeError("MONGODB_AUDIT_URI is not configured")

    mongo_client = get_mongo_client()

    try:
        mongo_client.admin.command("ping")
        collection = get_audit_collection(mongo_client)
        logger.info("Connected to MongoDB audit collection")

        with psycopg.connect(
            settings.AUDIT_WORKER_DATABASE_URL,
            connect_timeout=5,
        ) as connection:
            logger.info("Connected to PostgreSQL as the audit worker")

            while True:
                total, delivered, failed = process_batch(
                    connection,
                    collection,
                    args.batch_size,
                )

                if total:
                    logger.info(
                        "Batch complete: total=%s delivered=%s failed=%s",
                        total,
                        delivered,
                        failed,
                    )

                if args.once:
                    break

                time.sleep(args.poll_seconds)

    finally:
        mongo_client.close()


if __name__ == "__main__":
    main()
