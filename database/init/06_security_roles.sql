-- ============================================================
-- SecureBank: Automated Container Security Roles & Permissions
-- File: database/init/06_security_roles.sql
-- Purpose: Initialize application, transfer, auth, registration,
--          and audit worker roles with least-privilege security.
-- ============================================================

BEGIN;

-- 1. Create NOLOGIN service roles
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'securebank_app') THEN
        CREATE ROLE securebank_app NOLOGIN NOINHERIT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'securebank_transfer') THEN
        CREATE ROLE securebank_transfer NOLOGIN NOINHERIT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'securebank_auth') THEN
        CREATE ROLE securebank_auth NOLOGIN NOINHERIT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'securebank_registration') THEN
        CREATE ROLE securebank_registration NOLOGIN NOINHERIT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'securebank_audit_worker') THEN
        CREATE ROLE securebank_audit_worker NOLOGIN NOINHERIT;
    END IF;
END;
$$;

-- 2. Create LOGIN roles with development passwords
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'securebank_app_login') THEN
        CREATE ROLE securebank_app_login WITH LOGIN INHERIT PASSWORD 'SecureBankDev_AppPassword_123';
    ELSE
        ALTER ROLE securebank_app_login WITH LOGIN INHERIT PASSWORD 'SecureBankDev_AppPassword_123';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'securebank_audit_worker_login') THEN
        CREATE ROLE securebank_audit_worker_login WITH LOGIN INHERIT PASSWORD 'SecureBankDev_WorkerPassword_123';
    ELSE
        ALTER ROLE securebank_audit_worker_login WITH LOGIN INHERIT PASSWORD 'SecureBankDev_WorkerPassword_123';
    END IF;
END;
$$;

-- 3. Grant role memberships to login roles
GRANT securebank_app TO securebank_app_login;
GRANT securebank_audit_worker TO securebank_audit_worker_login;

-- 4. Schema usage
GRANT USAGE ON SCHEMA public TO
    securebank_app,
    securebank_transfer,
    securebank_auth,
    securebank_registration,
    securebank_audit_worker;

-- 5. Application role permissions (read-only for core tables)
GRANT SELECT ON public.accounts, public.loans, public.transactions TO securebank_app;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'semantic_search_items'
    ) THEN
        GRANT SELECT ON public.semantic_search_items TO securebank_app;
    END IF;
END $$;

-- 6. Transfer role permissions
GRANT SELECT, UPDATE ON public.accounts TO securebank_transfer;
GRANT INSERT ON public.transactions TO securebank_transfer;
GRANT SELECT (transaction_id) ON public.transactions TO securebank_transfer;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.sequences 
        WHERE sequence_schema = 'public' AND sequence_name = 'transactions_transaction_id_seq'
    ) THEN
        GRANT USAGE, SELECT ON SEQUENCE public.transactions_transaction_id_seq TO securebank_transfer;
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'transaction_audit_outbox'
    ) THEN
        GRANT INSERT ON public.transaction_audit_outbox TO securebank_transfer;
    END IF;
END $$;

-- 7. Configure transfer_funds function ownership and security
ALTER FUNCTION public.transfer_funds(
    BIGINT,
    BIGINT,
    BIGINT,
    NUMERIC,
    VARCHAR,
    TEXT
) OWNER TO securebank_transfer;

ALTER FUNCTION public.transfer_funds(
    BIGINT,
    BIGINT,
    BIGINT,
    NUMERIC,
    VARCHAR,
    TEXT
) SECURITY DEFINER;

ALTER FUNCTION public.transfer_funds(
    BIGINT,
    BIGINT,
    BIGINT,
    NUMERIC,
    VARCHAR,
    TEXT
) SET search_path = pg_catalog, public;

REVOKE ALL ON FUNCTION public.transfer_funds(
    BIGINT,
    BIGINT,
    BIGINT,
    NUMERIC,
    VARCHAR,
    TEXT
) FROM PUBLIC;

GRANT EXECUTE ON FUNCTION public.transfer_funds(
    BIGINT,
    BIGINT,
    BIGINT,
    NUMERIC,
    VARCHAR,
    TEXT
) TO securebank_app;

-- 8. Auth role permissions and get_auth_user function
GRANT SELECT (user_id, username, password_hash, role) ON public.users TO securebank_auth;

ALTER FUNCTION public.get_auth_user(VARCHAR) OWNER TO securebank_auth;
REVOKE ALL ON FUNCTION public.get_auth_user(VARCHAR) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.get_auth_user(VARCHAR) TO securebank_app;

-- 9. Registration role permissions and register_customer function
GRANT INSERT (username, password_hash, email, phone, role) ON public.users TO securebank_registration;
GRANT SELECT (user_id, username, email, phone, role, created_at) ON public.users TO securebank_registration;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.sequences 
        WHERE sequence_schema = 'public' AND sequence_name = 'users_user_id_seq'
    ) THEN
        GRANT USAGE, SELECT ON SEQUENCE public.users_user_id_seq TO securebank_registration;
    END IF;
END $$;

ALTER FUNCTION public.register_customer(VARCHAR, TEXT, VARCHAR, VARCHAR) OWNER TO securebank_registration;
REVOKE ALL ON FUNCTION public.register_customer(VARCHAR, TEXT, VARCHAR, VARCHAR) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.register_customer(VARCHAR, TEXT, VARCHAR, VARCHAR) TO securebank_app;

-- 10. Audit worker role permissions
GRANT SELECT (outbox_id, payload, created_at, delivered_at, attempts, last_error) ON public.transaction_audit_outbox TO securebank_audit_worker;
GRANT UPDATE (delivered_at, attempts, last_error) ON public.transaction_audit_outbox TO securebank_audit_worker;

REVOKE ALL ON public.transaction_audit_outbox FROM PUBLIC, securebank_app, securebank_app_login;

COMMIT;
