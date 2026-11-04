# secure-bank-app

Digital Banking System with Fraud Detection and Semantic Search

## Transaction Audit Integration

SecureBank uses a PostgreSQL transactional outbox and a Python worker to deliver completed transfer audit events to MongoDB.

### Requirements
- Python 3.x
- PostgreSQL
- MongoDB
- Docker Desktop (if using the provided containers)

### Installation
1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies using: pip install -r requirements.txt
4. Create a local .env file using .env.example as a template.
5. Configure database connection variables locally. Never commit .env or real credentials.

### Audit database setup
Apply these SQL files using the appropriate database administrator:
- database/migrations/001_transaction_audit_outbox.sql
- database/security/07_audit_worker_role.sql

Configure AUDIT_WORKER_DATABASE_URL and MONGODB_AUDIT_URI in .env.
The worker requires access to the PostgreSQL outbox and the MongoDB transaction_audit_logs collection.

### Running the audit worker
Process one batch and exit: python -m backend.app.audit_worker --once
Run continuously: python -m backend.app.audit_worker
Optional arguments: python -m backend.app.audit_worker --batch-size 20 --poll-seconds 5

### Audit delivery design
1. transfer_funds inserts an audit event into the PostgreSQL outbox within the transfer transaction.
2. The worker reads pending events using SKIP LOCKED.
3. The worker writes each event to MongoDB using the outbox UUID as the document ID.
4. After a successful MongoDB write, the worker marks the PostgreSQL event as delivered.
5. Failed deliveries retain error details and can be retried.

MongoDB writes are idempotent because each event uses its PostgreSQL outbox UUID as its MongoDB document ID.

### Relevant files
- backend/app/audit_worker.py - PostgreSQL-to-MongoDB worker.
- backend/app/config.py - environment configuration.
- database/functions/02_transfer_funds.sql - transfer function.
- database/init/02_transfer_funds.sql - initialization copy.
- database/migrations/001_transaction_audit_outbox.sql - audit outbox migration.
- database/security/07_audit_worker_role.sql - restricted worker permissions.
- database/tests/test_transfer_funds.sql - transfer and audit outbox tests.

### Security notes
- Never commit .env, database passwords, MongoDB URIs, or JWT signing secrets.
- Use separate PostgreSQL application, transfer, and audit-worker roles.
- Keep MongoDB audit credentials separate from administrator credentials.
- URL-encode credentials in MongoDB connection URIs when required.
