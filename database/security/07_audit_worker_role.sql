-- ============================================================
-- SecureBank: Audit Worker Role
-- File: database/security/07_audit_worker_role.sql
-- ============================================================

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'securebank_audit_worker'
    ) THEN
        CREATE ROLE securebank_audit_worker NOLOGIN NOINHERIT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'securebank_audit_worker_login'
    ) THEN
        CREATE ROLE securebank_audit_worker_login LOGIN INHERIT;
    END IF;
END;
$$;

ALTER ROLE securebank_audit_worker NOLOGIN NOINHERIT;
ALTER ROLE securebank_audit_worker_login LOGIN INHERIT;

GRANT USAGE ON SCHEMA public TO securebank_audit_worker;

GRANT SELECT (outbox_id, payload, created_at, delivered_at)
ON public.transaction_audit_outbox
TO securebank_audit_worker;

GRANT UPDATE (delivered_at, attempts, last_error)
ON public.transaction_audit_outbox
TO securebank_audit_worker;

GRANT securebank_audit_worker
TO securebank_audit_worker_login;

COMMIT;

-- ============================================================
-- End of security configuration
-- ============================================================
