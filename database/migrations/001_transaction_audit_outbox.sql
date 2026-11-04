-- ============================================================
-- SecureBank: Transaction Audit Outbox
-- File: database/migrations/001_transaction_audit_outbox.sql
-- Purpose: Persist successful transfer audit events reliably.
-- ============================================================

BEGIN;

CREATE TABLE IF NOT EXISTS public.transaction_audit_outbox (
    outbox_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id BIGINT NOT NULL
        REFERENCES public.transactions(transaction_id)
        ON DELETE RESTRICT,
    event_type VARCHAR(40) NOT NULL
        CHECK (event_type = 'TRANSFER_COMPLETED'),
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMPTZ,
    attempts INTEGER NOT NULL DEFAULT 0
        CHECK (attempts >= 0),
    last_error TEXT,
    CONSTRAINT uq_transaction_audit_outbox_event
        UNIQUE (transaction_id, event_type)
);

CREATE INDEX IF NOT EXISTS idx_transaction_audit_outbox_pending
    ON public.transaction_audit_outbox (created_at, outbox_id)
    WHERE delivered_at IS NULL;

-- The transfer function owner may insert events, but cannot
-- read or modify the outbox.
GRANT INSERT ON public.transaction_audit_outbox
    TO securebank_transfer;

-- No direct access for the application role.
REVOKE ALL ON public.transaction_audit_outbox
    FROM PUBLIC, securebank_app, securebank_app_login;

COMMIT;

-- ============================================================
-- End of migration
-- ============================================================
