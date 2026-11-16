# SecureBank Enterprise Banking System
**Digital Banking Core with Dual-Engine Architecture, Transactional Outbox, pgvector Semantic Search & Real-Time Fraud Intelligence**

[![FastAPI](https://img.shields.io/badge/FastAPI-2.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16_with_pgvector-336791?style=flat&logo=postgresql)](https://github.com/pgvector/pgvector)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0_SCRAM--SHA--256-47A248?style=flat&logo=mongodb)](https://www.mongodb.com)
[![Security](https://img.shields.io/badge/Security-Argon2id_%2B_JWT_RBAC-purple?style=flat)](https://cheatsheetseries.owasp.org/)
[![Tests](https://img.shields.io/badge/Tests-49_Passed_%28100%25%29-brightgreen?style=flat)]()

---

## Executive Architecture Overview

SecureBank is an enterprise-grade digital banking platform combining a **strictly isolated PostgreSQL ACID relational core** with a **high-throughput MongoDB audit and analytical lake**, connected via a **resilient transactional outbox pipeline**.

```
                           ┌──────────────────────────────────────────────┐
                           │          Modern Banking Web Portal           │
                           │   (Customer Banking + Admin Fraud Center)    │
                           └──────────────────────┬───────────────────────┘
                                                  │ REST / JSON (JWT RBAC)
                                                  ▼
                           ┌──────────────────────────────────────────────┐
                           │            FastAPI Banking Core              │
                           │      (Argon2id, Least-Privilege Roles)       │
                           └──────────────┬────────────────┬──────────────┘
                                          │                │
            ┌─────────────────────────────┴────┐     ┌─────┴────────────────────────────┐
            ▼                                  ▼     ▼                                  ▼
┌───────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐
│  PostgreSQL 16 (ACID)     │      │   PostgreSQL pgvector     │      │     MongoDB 7 Cluster     │
│ ───────────────────────── │      │ ───────────────────────── │      │ ───────────────────────── │
│ • accounts & users        │      │ • HNSW Vector Index       │      │ • transaction_audit_logs  │
│ • loans & transactions    │      │ • 4D Cosine (<=>) Search  │      │ • fraud_alerts (AML)      │
│ • row-level locks         │      │ • Semantic FAQ & TX query │      │ • login_events (Audit)    │
│ • transactional outbox    │      └───────────────────────────┘      │ • Aggregation Pipelines   │
└─────────────┬─────────────┘                                         └─────────────▲─────────────┘
              │                                                                     │
              └─────────────────────► [ Python Outbox Worker ] ─────────────────────┘
                                       (SKIP LOCKED Delivery)
```

---

## Key Enterprise Capabilities

### 1. Dual-Role Least-Privilege Database Security
- The primary application connection role (`securebank_app_login`) has **zero direct INSERT, UPDATE, or DELETE permissions** on financial tables (`accounts`, `transactions`, `loans`).
- All balance transfers and account mutations execute exclusively via PostgreSQL `SECURITY DEFINER` stored procedures (`transfer_funds`, `open_account`, `apply_loan`).
- Concurrent race conditions are prevented with strictly ordered row-level locks (`SELECT FOR UPDATE`).

### 2. Transactional Outbox Pattern with Guaranteed Delivery
- Every completed fund transfer inserts an audit document into `public.transaction_audit_outbox` within the exact same database transaction.
- An independent Python daemon (`backend.app.audit_worker`) polls pending outbox entries using `FOR UPDATE SKIP LOCKED`.
- Writes to MongoDB use the PostgreSQL outbox UUID as the MongoDB `_id`, making delivery **100% idempotent** with automatic retry backoff.

### 3. AI Semantic Vector Search (pgvector HNSW)
- Powered by PostgreSQL 16 `pgvector` with HNSW cosine similarity indexing (`vector_cosine_ops`).
- Allows users to search banking statements and support documentation in natural language (e.g. *"morning coffee"*, *"airport cab ride"*, *"lost card FAQ"*).

### 4. Real-Time Fraud & AML Intelligence Engine
- High-velocity checks immediately flag transactions exceeding ₹50,000 threshold.
- Suspicious keyword detection (crypto, offshore, gambling) triggers severity ratings (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) logged directly to MongoDB `fraud_alerts`.
- Real-time login event surveillance detects credential stuffing and brute-force attacks after 3 consecutive failures.

### 5. Interactive Customer Banking & Executive Admin Dashboard
- Unified Web UI at `/dashboard`:
  - **Customer Portal**: Account cards, instant secure transfers, transaction statements, loan EMI simulator with interactive sliders, and 1-click account opening.
  - **Admin Command Center**: System AUM metrics, live MongoDB Chart.js spending analytics, real-time fraud alert resolution queue, login security audit trail, and outbox synchronization console.

---

## Pre-Seeded Demo Personas

The system comes pre-loaded with realistic banking data. You can switch personas with 1 click directly in the dashboard header:

| Persona | Role | Username | Password | Key Assets |
| :--- | :--- | :--- | :--- | :--- |
| **Priya Sharma** | Customer | `priya_sharma` | `CustomerPass@123` | ₹7,50,000.00 Liquidity (Savings & Investment) + Active Home Loan |
| **Arun Kumar** | Customer | `arun_kumar` | `CustomerPass@123` | ₹85,000.00 Liquidity (Salary Checking) + Approved Auto Loan |
| **Bank Admin** | Admin | `admin` | `AdminPassword@123` | Full compliance surveillance, loan approvals, account freeze/unfreeze & fraud resolution |

---

## Quick Start Guide

### 1. Start Database Containers
```powershell
docker compose up -d
```
Verify containers are healthy (`docker compose ps`):
- `securebank-postgres` on port `5432`
- `securebank-mongodb` on port `27018`

### 2. Reset & Seed Fresh Demo Database
Cleans previous customer data and seeds fresh, official Admin and Customer accounts across both PostgreSQL and MongoDB:
```powershell
.\.venv\Scripts\python backend\scripts\reset_and_seed.py
```

### 3. Launch the Banking Application
```powershell
.\.venv\Scripts\uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Open in Browser
- **Banking Web App & Dashboard**: [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **OpenAPI JSON**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## Running the Transactional Outbox Worker

Sync pending PostgreSQL outbox events to MongoDB:

```powershell
# Single-batch execution
.\.venv\Scripts\python -m backend.app.audit_worker --once

# Continuous daemon mode
.\.venv\Scripts\python -m backend.app.audit_worker --batch-size 20 --poll-seconds 5
```
*(You can also trigger batch synchronization on-demand with 1 click from the Admin Dashboard!)*

---

## Automated Verification & Test Suite

The project includes an exhaustive testing suite across Python and SQL:

```powershell
# 1. Run all Python Unit and Live E2E Integration Tests (49 tests)
.\.venv\Scripts\python -m unittest discover -s tests

# 2. Run PostgreSQL Security Permission Isolation Tests (10 tests)
Get-Content database\tests\test_security_permissions.sql | docker exec -i securebank-postgres psql -U securebank -d securebank

# 3. Run PostgreSQL Fund Transfer ACID Tests (10 tests)
Get-Content database\tests\test_transfer_funds.sql | docker exec -i securebank-postgres psql -U securebank -d securebank

# 4. Run PostgreSQL Schema Integrity Constraint Tests (8 tests)
Get-Content database\tests\test_database_integrity.sql | docker exec -i securebank-postgres psql -U securebank -d securebank

# 5. Run MongoDB Audit Schema Validation Tests (3 tests)
Get-Content database\mongodb\02_audit_tests.js | docker exec -i securebank-mongodb mongosh -u securebank_admin -p dbms@123 --authenticationDatabase admin
```

**Total Test Coverage:** 80 tests passing across SQL constraints, role privileges, MongoDB JSON schemas, and FastAPI business logic.

---

## Directory Structure

```text
secure-bank-app/
├── backend/
│   ├── app/
│   │   ├── accounts.py           # Account balance, listing, opening, freeze controls
│   │   ├── analytics.py          # MongoDB aggregation, fraud alerts & pgvector search
│   │   ├── audit_worker.py       # PostgreSQL outbox to MongoDB audit daemon
│   │   ├── auth.py               # Argon2id registration, login, profile & user listing
│   │   ├── config.py             # Environment configurations
│   │   ├── dashboard_ui.py       # Full-fidelity Fintech Web Portal
│   │   ├── dependencies.py       # JWT authentication & RBAC guards
│   │   ├── loans.py              # Loan applications, EMI calculator & admin lifecycle
│   │   ├── main.py               # FastAPI application entrypoint & middleware
│   │   ├── mongodb.py            # MongoDB client & collection helpers
│   │   ├── postgres.py           # PostgreSQL connection pool
│   │   ├── security.py           # Argon2 password hasher & verifier
│   │   ├── tokens.py             # JWT token issuance & signature decoding
│   │   └── transactions.py       # ACID fund transfers, history & real-time AML hooks
│   └── scripts/
│       └── seed_demo_data.py     # Comprehensive database seeder (Postgres + Mongo)
├── database/
│   ├── functions/                # Stored procedures (transfer, registration, accounts, loans)
│   ├── init/                     # Docker entrypoint initialization scripts
│   ├── migrations/               # pgvector & transactional outbox DDL
│   ├── mongodb/                  # Collections, indexes & schema validators
│   ├── security/                 # Least-privilege roles & permissions DDL
│   └── tests/                    # Database integrity, security & ACID tests
├── tests/                        # Python unit & live E2E test suite (49 tests)
├── docker-compose.yml            # PostgreSQL (pgvector:pg16) + MongoDB 7
└── requirements.txt              # Production Python dependencies
```
