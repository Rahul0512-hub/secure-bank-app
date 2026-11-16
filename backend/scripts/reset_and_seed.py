"""
SecureBank - Clean Database Reset & Demo Seeder Script
Wipes all previous test data and seeds fresh, professional Customer and Admin accounts.
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

ADMIN_DB_URL = os.getenv(
    "ADMIN_DATABASE_URL",
    "postgresql://securebank:SecureBankDev_Postgres_ChangeMe@localhost:5432/securebank"
)


def reset_and_seed_postgres():
    print("\n[1/2] Connecting to PostgreSQL to reset & reseed...")
    conn = psycopg.connect(ADMIN_DB_URL)

    with conn:
        with conn.cursor() as cur:
            # Step A: Delete all existing customer and transaction data
            print("  -> Deleting previous records from public schema...")
            cur.execute("DELETE FROM public.transaction_audit_outbox;")
            cur.execute("DELETE FROM public.transactions;")
            cur.execute("DELETE FROM public.loans;")
            cur.execute("DELETE FROM public.accounts;")
            cur.execute("DELETE FROM public.users;")
            cur.execute("DELETE FROM public.semantic_search_items;")

            # Step B: Seed Demo Users
            print("  -> Creating fresh Admin and Demo Customers...")
            users = [
                ("admin", "AdminPassword@123", "admin@securebank.com", "+91 90000 00001", "Admin"),
                ("priya_sharma", "CustomerPass@123", "priya.sharma@securebank.com", "+91 98765 43210", "Customer"),
                ("arun_kumar", "CustomerPass@123", "arun.kumar@securebank.com", "+91 98123 45678", "Customer"),
            ]

            user_ids = {}
            for username, password, email, phone, role in users:
                pw_hash = hash_password(password)
                cur.execute(
                    """
                    INSERT INTO public.users (username, password_hash, email, phone, role)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING user_id;
                    """,
                    (username, pw_hash, email, phone, role)
                )
                uid = cur.fetchone()[0]
                user_ids[username] = uid
                print(f"     ✓ Created User: {username} (Role: {role}, ID: {uid})")

            # Step C: Seed Accounts
            print("  -> Creating Bank Accounts with initial balances...")
            accounts = [
                ("priya_sharma", "SBIN1002003001", "Savings", Decimal("250000.0000")),
                ("priya_sharma", "SBIN1002003002", "Investment", Decimal("500000.0000")),
                ("arun_kumar", "SBIN2003004001", "Salary Checking", Decimal("85000.0000")),
            ]

            account_ids = {}
            for username, acc_num, acc_type, balance in accounts:
                uid = user_ids[username]
                cur.execute(
                    """
                    INSERT INTO public.accounts (user_id, account_number, account_type, balance, currency, status)
                    VALUES (%s, %s, %s, %s, 'INR', 'Active')
                    RETURNING account_id;
                    """,
                    (uid, acc_num, acc_type, balance)
                )
                aid = cur.fetchone()[0]
                account_ids[acc_num] = aid
                print(f"     ✓ Created Account: {acc_num} ({acc_type}, Balance: ₹{balance:,.2f}, ID: {aid})")

            # Step D: Seed Loans
            print("  -> Creating Loan Portfolios...")
            loans = [
                (user_ids["priya_sharma"], Decimal("2500000.0000"), Decimal("8.4500"), "Active", date(2025, 1, 15), date(2045, 1, 15)),
                (user_ids["arun_kumar"], Decimal("450000.0000"), Decimal("10.2500"), "Approved", date(2026, 2, 1), date(2029, 2, 1)),
            ]

            for uid, amount, rate, status, s_date, e_date in loans:
                cur.execute(
                    """
                    INSERT INTO public.loans (user_id, loan_amount, interest_rate, status, start_date, end_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING loan_id;
                    """,
                    (uid, amount, rate, status, s_date, e_date)
                )
                lid = cur.fetchone()[0]
                print(f"     ✓ Created Loan: ₹{amount:,.2f} at {rate}% ({status}, ID: {lid})")

            # Step E: Seed Initial Historical Transactions & Outbox
            print("  -> Creating Seed Transactions & Outbox Records...")
            priya_savings = account_ids["SBIN1002003001"]
            arun_checking = account_ids["SBIN2003004001"]

            tx_history = [
                (priya_savings, arun_checking, Decimal("15000.0000"), "Transfer", "Office shared rent settlement", -4),
                (arun_checking, priya_savings, Decimal("2450.0000"), "Transfer", "Team dinner expense reimbursement", -2),
                (priya_savings, arun_checking, Decimal("8500.0000"), "Transfer", "Co-working space monthly share", -1),
            ]

            for src_id, dest_id, amt, tx_type, desc, offset in tx_history:
                tx_time = datetime.now(timezone.utc) + timedelta(days=offset, hours=2)
                cur.execute(
                    """
                    INSERT INTO public.transactions (source_account_id, destination_account_id, amount, transaction_type, description, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, 'Completed', %s)
                    RETURNING transaction_id;
                    """,
                    (src_id, dest_id, amt, tx_type, desc, tx_time)
                )
                tid = cur.fetchone()[0]

                # Populate outbox (already marked delivered for seed items)
                cur.execute(
                    """
                    INSERT INTO public.transaction_audit_outbox (transaction_id, event_type, payload, delivered_at)
                    VALUES (%s, 'TRANSFER_COMPLETED', %s, CURRENT_TIMESTAMP);
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
                            "occurred_at": tx_time.isoformat(),
                            "actor_user_id": user_ids["priya_sharma"],
                            "description": desc,
                        })
                    )
                )
                print(f"     ✓ Transaction #{tid}: ₹{amt:,.2f} ('{desc}')")

            # Step F: Seed pgvector Semantic Search Items
            print("  -> Seeding pgvector 4D semantic search embeddings...")
            semantic_items = [
                ('TRANSACTION', 101, 'Food & Dining', 'Starbucks Coffee Indiranagar', 'Morning latte and croissant purchase via UPI', 450.00, '[0.95, 0.05, 0.05, 0.02]'),
                ('TRANSACTION', 102, 'Food & Dining', 'Swiggy Dinner Order', 'Late night biryani and soft drinks delivery', 680.00, '[0.92, 0.08, 0.04, 0.01]'),
                ('TRANSACTION', 103, 'Travel', 'Uber Airport Ride', 'Cab trip to Kempegowda International Airport terminal', 1250.00, '[0.05, 0.96, 0.04, 0.02]'),
                ('TRANSACTION', 104, 'Travel', 'IndiGo Airlines Flight', 'Domestic flight ticket booking Bengaluru to Mumbai', 5400.00, '[0.04, 0.98, 0.05, 0.01]'),
                ('TRANSACTION', 105, 'Bills & Utilities', 'BESCOM Electricity Bill', 'Monthly home electricity utility bill payment', 2100.00, '[0.02, 0.03, 0.96, 0.05]'),
                ('TRANSACTION', 106, 'Bills & Utilities', 'Airtel Broadband Fiber', 'High-speed fiber internet monthly recharge', 1199.00, '[0.02, 0.03, 0.95, 0.08]'),
                ('FAQ', 1, 'Security', 'How to block a stolen or lost debit card?', 'Go to Security Settings > Freeze Card immediately or call our 24/7 fraud helpline.', None, '[0.01, 0.02, 0.05, 0.98]'),
                ('FAQ', 2, 'Security', 'Why was my high-value transfer flagged for fraud?', 'Transfers above 50,000 INR trigger real-time velocity and anomaly checks in our Fraud Engine.', None, '[0.01, 0.01, 0.10, 0.97]'),
                ('FAQ', 3, 'Payments', 'How do I increase my daily NEFT/IMPS transfer limit?', 'Navigate to Account Limits and verify with OTP to raise your daily transfer cap up to 5 Lakhs.', None, '[0.02, 0.05, 0.65, 0.75]')
            ]

            for itype, ref, cat, title, desc, amt, emb in semantic_items:
                cur.execute(
                    """
                    INSERT INTO public.semantic_search_items (item_type, reference_id, category, title, description, amount, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::vector);
                    """,
                    (itype, ref, cat, title, desc, amt, emb)
                )

    conn.close()
    print("  ✓ PostgreSQL reset and reseed complete.")
    return user_ids, account_ids


def reset_and_seed_mongodb(user_ids, account_ids):
    print("\n[2/2] Connecting to MongoDB to reset & reseed audit logs...")
    client = get_mongo_client()

    try:
        audit_col = get_audit_collection(client)
        fraud_col = get_fraud_alerts_collection(client)
        login_col = get_login_events_collection(client)

        # Clear existing collections
        print("  -> Deleting previous records from MongoDB...")
        audit_col.delete_many({})
        fraud_col.delete_many({})
        login_col.delete_many({})

        now = datetime.now(timezone.utc)

        # Seed Audit Logs
        print("  -> Inserting initial audit trail events...")
        priya_savings = account_ids["SBIN1002003001"]
        arun_checking = account_ids["SBIN2003004001"]

        audit_col.insert_many([
            {
                "transaction_id": 1001,
                "event_type": "TRANSFER_COMPLETED",
                "status": "SUCCESS",
                "source_account_id": priya_savings,
                "destination_account_id": arun_checking,
                "amount": Decimal128(Decimal("15000.00")),
                "currency": "INR",
                "occurred_at": now - timedelta(days=4),
                "actor_user_id": user_ids["priya_sharma"],
                "description": "Office shared rent settlement",
            },
            {
                "transaction_id": 1002,
                "event_type": "TRANSFER_COMPLETED",
                "status": "SUCCESS",
                "source_account_id": arun_checking,
                "destination_account_id": priya_savings,
                "amount": Decimal128(Decimal("2450.00")),
                "currency": "INR",
                "occurred_at": now - timedelta(days=2),
                "actor_user_id": user_ids["arun_kumar"],
                "description": "Team dinner expense reimbursement",
            },
            {
                "transaction_id": 1003,
                "event_type": "TRANSFER_COMPLETED",
                "status": "SUCCESS",
                "source_account_id": priya_savings,
                "destination_account_id": arun_checking,
                "amount": Decimal128(Decimal("8500.00")),
                "currency": "INR",
                "occurred_at": now - timedelta(days=1),
                "actor_user_id": user_ids["priya_sharma"],
                "description": "Co-working space monthly share",
            },
        ])

        # Seed Fraud Alerts
        print("  -> Inserting sample AML fraud alerts for surveillance...")
        fraud_col.insert_many([
            {
                "transaction_id": 8801,
                "user_id": user_ids["priya_sharma"],
                "amount": 85000.0,
                "category": "International Wire",
                "reason": "High-value transfer of ₹85,000 to offshore cryptocurrency exchange flagged by rule FX-09",
                "severity": "CRITICAL",
                "status": "OPEN",
                "created_at": now - timedelta(hours=3),
            },
            {
                "transaction_id": 8802,
                "user_id": user_ids["arun_kumar"],
                "amount": 55000.0,
                "category": "High-Value Transfer",
                "reason": "Transfer amount ₹55,000 exceeded customer normal velocity baseline by 320%",
                "severity": "HIGH",
                "status": "INVESTIGATING",
                "created_at": now - timedelta(hours=7),
            },
            {
                "transaction_id": None,
                "user_id": 0,
                "amount": 0.0,
                "category": "Account Takeover",
                "reason": "Brute-force credential stuffing alert: 4 failed attempts from TOR exit node 185.220.101.45",
                "severity": "CRITICAL",
                "status": "OPEN",
                "created_at": now - timedelta(minutes=45),
            },
        ])

        # Seed Login Events
        print("  -> Inserting security authentication audit events...")
        login_col.insert_many([
            {"user_id": user_ids["admin"], "email": "admin@securebank.com", "ip_address": "127.0.0.1", "user_agent": "Workstation (Windows 11)", "status": "SUCCESS", "occurred_at": now - timedelta(hours=2)},
            {"user_id": user_ids["priya_sharma"], "email": "priya.sharma@securebank.com", "ip_address": "103.21.244.12", "user_agent": "Chrome 122 (Windows 11)", "status": "SUCCESS", "occurred_at": now - timedelta(minutes=20)},
            {"user_id": user_ids["arun_kumar"], "email": "arun.kumar@securebank.com", "ip_address": "49.37.192.88", "user_agent": "Safari 17 (macOS)", "status": "SUCCESS", "occurred_at": now - timedelta(minutes=10)},
            {"user_id": None, "email": "priya.sharma@securebank.com", "ip_address": "185.220.101.45", "user_agent": "Python-urllib/3.11", "status": "FAILED", "occurred_at": now - timedelta(minutes=50)},
            {"user_id": None, "email": "priya.sharma@securebank.com", "ip_address": "185.220.101.45", "user_agent": "Python-urllib/3.11", "status": "FAILED", "occurred_at": now - timedelta(minutes=48)},
            {"user_id": None, "email": "priya.sharma@securebank.com", "ip_address": "185.220.101.45", "user_agent": "Python-urllib/3.11", "status": "FAILED", "occurred_at": now - timedelta(minutes=46)},
        ])

    finally:
        client.close()
    print("  ✓ MongoDB audit reset and reseed complete.")


def print_summary(user_ids, account_ids):
    print("\n" + "="*65)
    print(" SECUREBANK FRESH DEMO CREDENTIALS")
    print("="*65)
    print("\n1. BANK ADMINISTRATOR (Full Management Authority):")
    print("   • Username: admin")
    print("   • Password: AdminPassword@123")
    print("   • Role:     Admin")
    print("   • Email:    admin@securebank.com")
    print("\n2. CUSTOMER 1 (High Net Worth Retail Customer):")
    print("   • Username: priya_sharma")
    print("   • Password: CustomerPass@123")
    print("   • Role:     Customer")
    print("   • Accounts: SBIN1002003001 (Savings: ₹2,50,000.00)")
    print("               SBIN1002003002 (Investment: ₹5,00,000.00)")
    print("   • Loans:    Active Home Loan: ₹25,00,000.00 at 8.45%")
    print("\n3. CUSTOMER 2 (Salaried Professional):")
    print("   • Username: arun_kumar")
    print("   • Password: CustomerPass@123")
    print("   • Role:     Customer")
    print("   • Accounts: SBIN2003004001 (Checking: ₹85,000.00)")
    print("   • Loans:    Approved Vehicle Loan: ₹4,50,000.00 at 10.25%")
    print("="*65 + "\n")


if __name__ == "__main__":
    u_ids, a_ids = reset_and_seed_postgres()
    reset_and_seed_mongodb(u_ids, a_ids)
    print_summary(u_ids, a_ids)
