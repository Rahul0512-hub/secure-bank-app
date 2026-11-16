"""
SecureBank - Comprehensive Demo Data Seeding Script
Seeds PostgreSQL and MongoDB with realistic, professional banking data.
Can be safely rerun multiple times (idempotent).
"""

import sys
import os
from datetime import datetime, timezone, timedelta, date
from decimal import Decimal
import psycopg
from bson.decimal128 import Decimal128

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.config import settings
from backend.app.security import hash_password
from backend.app.mongodb import (
    get_mongo_client,
    get_audit_collection,
    get_fraud_alerts_collection,
    get_login_events_collection,
)

# Admin DB URL using postgres credentials if needed, or fallback to settings.DATABASE_URL
ADMIN_DB_URL = os.getenv("ADMIN_DATABASE_URL", "postgresql://securebank:SecureBankDev_Postgres_ChangeMe@localhost:5432/securebank")

def seed_postgres():
    print("[PostgreSQL] Connecting to seed database...")
    try:
        conn = psycopg.connect(ADMIN_DB_URL)
    except Exception:
        conn = psycopg.connect(settings.DATABASE_URL)

    with conn:
        with conn.cursor() as cur:
            # 1. Seed Users
            users_data = [
                ("admin", "AdminPassword@123", "admin@securebank.com", "+91 90000 00001", "Admin"),
                ("priya_sharma", "CustomerPass@123", "priya.sharma@securebank.com", "+91 98765 43210", "Customer"),
                ("arun_kumar", "CustomerPass@123", "arun.kumar@securebank.com", "+91 98123 45678", "Customer"),
                ("vikram_singh", "CustomerPass@123", "vikram.singh@securebank.com", "+91 99887 76655", "Customer"),
                ("ananya_patel", "CustomerPass@123", "ananya.patel@securebank.com", "+91 97654 32100", "Customer"),
            ]

            user_map = {} # username -> user_id
            for username, pwd, email, phone, role in users_data:
                cur.execute("SELECT user_id FROM public.users WHERE username = %s;", (username,))
                row = cur.fetchone()
                if row:
                    user_map[username] = row[0]
                    print(f"  Existing user: {username} (ID: {row[0]})")
                else:
                    pw_hash = hash_password(pwd)
                    cur.execute(
                        """
                        INSERT INTO public.users (username, password_hash, email, phone, role)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING user_id;
                        """,
                        (username, pw_hash, email, phone, role)
                    )
                    uid = cur.fetchone()[0]
                    user_map[username] = uid
                    print(f"  Created user: {username} (ID: {uid})")

            # 2. Seed Accounts
            accounts_data = [
                ("priya_sharma", "SBIN0010023451", "Savings", Decimal("185450.0000")),
                ("priya_sharma", "SBIN0010023452", "Investment", Decimal("450000.0000")),
                ("arun_kumar", "SBIN0020034561", "Checking", Decimal("62300.0000")),
                ("arun_kumar", "SBIN0020034562", "Savings", Decimal("15200.0000")),
                ("vikram_singh", "SBIN0030045671", "Business", Decimal("820000.0000")),
                ("ananya_patel", "SBIN0040056781", "Savings", Decimal("34800.0000")),
            ]

            account_map = {} # acc_num -> account_id
            for uname, acc_num, acc_type, bal in accounts_data:
                uid = user_map[uname]
                cur.execute("SELECT account_id FROM public.accounts WHERE account_number = %s;", (acc_num,))
                row = cur.fetchone()
                if row:
                    account_map[acc_num] = row[0]
                    print(f"  Existing account: {acc_num} (ID: {row[0]})")
                else:
                    cur.execute(
                        """
                        INSERT INTO public.accounts (user_id, account_number, account_type, balance, currency, status)
                        VALUES (%s, %s, %s, %s, 'INR', 'Active')
                        RETURNING account_id;
                        """,
                        (uid, acc_num, acc_type, bal)
                    )
                    aid = cur.fetchone()[0]
                    account_map[acc_num] = aid
                    print(f"  Created account: {acc_num} ({acc_type}, ID: {aid})")

            # 3. Seed Loans
            loans_data = [
                ("priya_sharma", Decimal("2500000.0000"), Decimal("8.4500"), "Active", date(2025, 1, 15), date(2045, 1, 15)),
                ("arun_kumar", Decimal("450000.0000"), Decimal("10.2500"), "Approved", date(2026, 2, 1), date(2029, 2, 1)),
                ("vikram_singh", Decimal("1500000.0000"), Decimal("9.0000"), "Pending", date(2026, 6, 1), date(2031, 6, 1)),
            ]

            for uname, l_amt, l_rate, l_status, s_date, e_date in loans_data:
                uid = user_map[uname]
                cur.execute("SELECT loan_id FROM public.loans WHERE user_id = %s AND loan_amount = %s;", (uid, l_amt))
                if not cur.fetchone():
                    cur.execute(
                        """
                        INSERT INTO public.loans (user_id, loan_amount, interest_rate, status, start_date, end_date)
                        VALUES (%s, %s, %s, %s, %s, %s);
                        """,
                        (uid, l_amt, l_rate, l_status, s_date, e_date)
                    )
                    print(f"  Created loan: {l_amt} INR for {uname} ({l_status})")

            # 4. Seed Historical Transactions
            tx_data = [
                ("SBIN0010023451", "SBIN0020034561", Decimal("4500.0000"), "Transfer", "Monthly maintenance share", -5),
                ("SBIN0020034561", "SBIN0010023451", Decimal("1200.0000"), "Transfer", "Weekend dinner bill split", -3),
                ("SBIN0030045671", "SBIN0010023451", Decimal("75000.0000"), "Transfer", "Consulting fee milestone 2", -2),
                ("SBIN0010023451", "SBIN0040056781", Decimal("2800.0000"), "Transfer", "Gift and book order reimb", -1),
                ("SBIN0040056781", "SBIN0020034561", Decimal("950.0000"), "Transfer", "Coffee and shared cab ride", 0),
            ]

            for src_num, dest_num, amt, txtype, desc, day_offset in tx_data:
                src_id = account_map[src_num]
                dest_id = account_map[dest_num]
                cur.execute(
                    "SELECT transaction_id FROM public.transactions WHERE source_account_id = %s AND destination_account_id = %s AND amount = %s;",
                    (src_id, dest_id, amt)
                )
                if not cur.fetchone():
                    t_time = datetime.now(timezone.utc) + timedelta(days=day_offset, hours=2)
                    cur.execute(
                        """
                        INSERT INTO public.transactions (source_account_id, destination_account_id, amount, transaction_type, description, status, created_at)
                        VALUES (%s, %s, %s, %s, %s, 'Completed', %s)
                        RETURNING transaction_id;
                        """,
                        (src_id, dest_id, amt, txtype, desc, t_time)
                    )
                    tid = cur.fetchone()[0]

                    # Also insert into outbox so worker / audit table is synced
                    cur.execute(
                        """
                        INSERT INTO public.transaction_audit_outbox (transaction_id, event_type, payload, delivered_at)
                        VALUES (%s, 'TRANSFER_COMPLETED', %s, CURRENT_TIMESTAMP)
                        ON CONFLICT DO NOTHING;
                        """,
                        (
                            tid,
                            psycopg.types.json.Jsonb({
                                "transaction_id": tid,
                                "event_type": "TRANSFER_COMPLETED",
                                "status": "SUCCESS",
                                "source_account_id": src_id,
                                "destination_account_id": dest_id,
                                "amount": str(amt),
                                "currency": "INR",
                                "occurred_at": t_time.isoformat(),
                                "actor_user_id": user_map["priya_sharma"],
                                "description": desc,
                            })
                        )
                    )
                    print(f"  Created transaction: ₹{amt} ({src_num} -> {dest_num})")

            # 5. Semantic Search Items
            semantic_items = [
                ('TRANSACTION', 101, 'Food & Dining', 'Starbucks Indiranagar', 'Morning latte and hazelnut pastry', 420.00, '[0.95, 0.05, 0.05, 0.02]'),
                ('TRANSACTION', 102, 'Food & Dining', 'Swiggy Dinner Order', 'Biryani and dessert delivery for dinner party', 850.00, '[0.92, 0.08, 0.04, 0.01]'),
                ('TRANSACTION', 103, 'Travel', 'Uber Airport Ride', 'Morning cab to Bangalore airport terminal 2', 1350.00, '[0.05, 0.96, 0.04, 0.02]'),
                ('TRANSACTION', 104, 'Travel', 'IndiGo Airlines Flight', 'Return flight BLR to BOM business travel', 6200.00, '[0.04, 0.98, 0.05, 0.01]'),
                ('TRANSACTION', 105, 'Bills & Utilities', 'BESCOM Power Bill', 'Monthly home electricity utility payment', 2450.00, '[0.02, 0.03, 0.96, 0.05]'),
                ('TRANSACTION', 106, 'Bills & Utilities', 'Airtel Broadband Fiber', 'High-speed fiber internet monthly recharge', 1199.00, '[0.02, 0.03, 0.95, 0.08]'),
                ('FAQ', 1, 'Security', 'How to freeze or block a lost debit card?', 'Navigate to Security Settings > Freeze Card or call our 24/7 fraud helpline immediately.', None, '[0.01, 0.02, 0.05, 0.98]'),
                ('FAQ', 2, 'Security', 'Why was my high-value transfer flagged for fraud review?', 'Transfers >= ₹50,000 or to high-risk recipients trigger anomaly detection checks.', None, '[0.01, 0.01, 0.10, 0.97]'),
                ('FAQ', 3, 'Payments', 'How do I raise my daily IMPS / NEFT transfer limit?', 'Go to Account Preferences and verify with 2FA/OTP to adjust daily limit up to ₹10 Lakhs.', None, '[0.02, 0.05, 0.65, 0.75]')
            ]

            for itype, ref, cat, title, desc, amt, emb in semantic_items:
                cur.execute("SELECT id FROM public.semantic_search_items WHERE title = %s;", (title,))
                if not cur.fetchone():
                    cur.execute(
                        """
                        INSERT INTO public.semantic_search_items (item_type, reference_id, category, title, description, amount, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s::vector);
                        """,
                        (itype, ref, cat, title, desc, amt, emb)
                    )
                    print(f"  Created semantic search item: {title}")

    conn.close()
    print("[PostgreSQL] Seeding completed successfully.")


def seed_mongodb():
    print("[MongoDB] Connecting to seed audit logs, fraud alerts and login events...")
    client = get_mongo_client()
    try:
        audit_col = get_audit_collection(client)
        fraud_col = get_fraud_alerts_collection(client)
        login_col = get_login_events_collection(client)

        now = datetime.now(timezone.utc)

        # 1. Seed Audit Logs
        audit_entries = [
            {
                "transaction_id": 2001,
                "event_type": "TRANSFER_COMPLETED",
                "status": "SUCCESS",
                "source_account_id": 1,
                "destination_account_id": 3,
                "amount": Decimal128(Decimal("4500.00")),
                "currency": "INR",
                "occurred_at": now - timedelta(days=5),
                "actor_user_id": 2,
                "description": "Monthly maintenance share",
            },
            {
                "transaction_id": 2002,
                "event_type": "TRANSFER_COMPLETED",
                "status": "SUCCESS",
                "source_account_id": 3,
                "destination_account_id": 1,
                "amount": Decimal128(Decimal("1200.00")),
                "currency": "INR",
                "occurred_at": now - timedelta(days=3),
                "actor_user_id": 3,
                "description": "Weekend dinner bill split",
            },
            {
                "transaction_id": 2003,
                "event_type": "TRANSFER_COMPLETED",
                "status": "SUCCESS",
                "source_account_id": 5,
                "destination_account_id": 1,
                "amount": Decimal128(Decimal("75000.00")),
                "currency": "INR",
                "occurred_at": now - timedelta(days=2),
                "actor_user_id": 4,
                "description": "Consulting fee milestone 2",
            },
            {
                "transaction_id": 2004,
                "event_type": "TRANSFER_COMPLETED",
                "status": "SUCCESS",
                "source_account_id": 1,
                "destination_account_id": 6,
                "amount": Decimal128(Decimal("2800.00")),
                "currency": "INR",
                "occurred_at": now - timedelta(days=1),
                "actor_user_id": 2,
                "description": "Gift and book order reimb",
            },
            {
                "transaction_id": 2005,
                "event_type": "TRANSFER_COMPLETED",
                "status": "SUCCESS",
                "source_account_id": 6,
                "destination_account_id": 3,
                "amount": Decimal128(Decimal("950.00")),
                "currency": "INR",
                "occurred_at": now - timedelta(hours=4),
                "actor_user_id": 5,
                "description": "Coffee and shared cab ride",
            },
        ]

        for entry in audit_entries:
            if not audit_col.find_one({"transaction_id": entry["transaction_id"]}):
                audit_col.insert_one(entry)
                print(f"  [Mongo] Inserted audit log for tx {entry['transaction_id']}")

        # 2. Seed Fraud Alerts
        fraud_alerts_data = [
            {
                "transaction_id": 9901,
                "user_id": 2,
                "amount": 85000.0,
                "category": "International Wire",
                "reason": "High-value transfer of ₹85,000 to offshore cryptocurrency exchange flagged by rule FX-09",
                "severity": "CRITICAL",
                "status": "OPEN",
                "created_at": now - timedelta(hours=6),
            },
            {
                "transaction_id": 9902,
                "user_id": 3,
                "amount": 55000.0,
                "category": "High-Value Transfer",
                "reason": "Transfer amount ₹55,000 exceeded customer normal velocity baseline by 320%",
                "severity": "HIGH",
                "status": "INVESTIGATING",
                "created_at": now - timedelta(days=1, hours=3),
            },
            {
                "transaction_id": None,
                "user_id": 0,
                "amount": 0.0,
                "category": "Account Takeover",
                "reason": "Brute-force credential stuffing alert: 5 failed attempts from foreign TOR exit node 185.220.101.45",
                "severity": "CRITICAL",
                "status": "OPEN",
                "created_at": now - timedelta(hours=1),
            },
            {
                "transaction_id": 9903,
                "user_id": 4,
                "amount": 18000.0,
                "category": "Peer-to-Peer",
                "reason": "Unusual night-time transaction window (03:14 AM IST) with unverified beneficiary",
                "severity": "MEDIUM",
                "status": "RESOLVED",
                "created_at": now - timedelta(days=2),
            },
        ]

        for alert in fraud_alerts_data:
            if not fraud_col.find_one({"reason": alert["reason"]}):
                fraud_col.insert_one(alert)
                print(f"  [Mongo] Inserted fraud alert: {alert['category']} ({alert['severity']})")

        # 3. Seed Login Events
        login_events_data = [
            {"user_id": 2, "email": "priya.sharma@securebank.com", "ip_address": "103.21.244.12", "user_agent": "Chrome 122 (Windows 11)", "status": "SUCCESS", "occurred_at": now - timedelta(minutes=15)},
            {"user_id": 3, "email": "arun.kumar@securebank.com", "ip_address": "49.37.192.88", "user_agent": "Safari 17 (macOS Sonoma)", "status": "SUCCESS", "occurred_at": now - timedelta(hours=2)},
            {"user_id": 1, "email": "admin@securebank.com", "ip_address": "127.0.0.1", "user_agent": "Firefox 123 (Workstation)", "status": "SUCCESS", "occurred_at": now - timedelta(hours=5)},
            {"user_id": 2, "email": "priya.sharma@securebank.com", "ip_address": "185.220.101.45", "user_agent": "Python-urllib/3.11", "status": "FAILED", "occurred_at": now - timedelta(hours=1, minutes=10)},
            {"user_id": 2, "email": "priya.sharma@securebank.com", "ip_address": "185.220.101.45", "user_agent": "Python-urllib/3.11", "status": "FAILED", "occurred_at": now - timedelta(hours=1, minutes=8)},
            {"user_id": 2, "email": "priya.sharma@securebank.com", "ip_address": "185.220.101.45", "user_agent": "Python-urllib/3.11", "status": "FAILED", "occurred_at": now - timedelta(hours=1, minutes=6)},
            {"user_id": 4, "email": "vikram.singh@securebank.com", "ip_address": "157.48.21.109", "user_agent": "Edge 121 (Windows 11)", "status": "SUCCESS", "occurred_at": now - timedelta(days=1)},
        ]

        for log in login_events_data:
            if not login_col.find_one({"email": log["email"], "occurred_at": log["occurred_at"]}):
                login_col.insert_one(log)
                print(f"  [Mongo] Inserted login event: {log['email']} ({log['status']})")

    finally:
        client.close()
    print("[MongoDB] Seeding completed successfully.")


if __name__ == "__main__":
    seed_postgres()
    seed_mongodb()
    print("\n All SecureBank pre-built database components seeded successfully!")
