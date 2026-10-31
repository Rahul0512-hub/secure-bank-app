
-- ============================================================
-- SecureBank: Database Roles and Permissions
-- File: database/security/01_roles_and_permissions.sql
-- ============================================================

BEGIN;

-- 1. Create dedicated roles if they do not exist.

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'securebank_app'
    ) THEN
        CREATE ROLE securebank_app NOLOGIN NOINHERIT;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'securebank_transfer'
    ) THEN
        CREATE ROLE securebank_transfer NOLOGIN NOINHERIT;
    END IF;
END;
$$;

-- 2. Grant schema access.

GRANT USAGE ON SCHEMA public
TO securebank_app, securebank_transfer;

-- 3. Application role: read-only access to banking data.

GRANT SELECT ON
    public.accounts,
    public.loans,
    public.transactions
TO securebank_app;

-- 4. Transfer role: minimum permissions required
--    by the transfer_funds function.

GRANT SELECT, UPDATE ON public.accounts
TO securebank_transfer;

GRANT INSERT ON public.transactions
TO securebank_transfer;
GRANT SELECT (transaction_id) ON public.transactions
TO securebank_transfer;

GRANT USAGE, SELECT
ON SEQUENCE public.transactions_transaction_id_seq
TO securebank_transfer;

-- 5. Temporarily allow the transfer role to own
--    the function in the public schema.

GRANT CREATE ON SCHEMA public
TO securebank_transfer;

ALTER FUNCTION public.transfer_funds(
    BIGINT,
    BIGINT,
    NUMERIC,
    VARCHAR,
    TEXT
) OWNER TO securebank_transfer;

-- 6. Configure secure function execution.
--    The function executes with the restricted owner's
--    permissions, not the application's permissions.

ALTER FUNCTION public.transfer_funds(
    BIGINT,
    BIGINT,
    NUMERIC,
    VARCHAR,
    TEXT
) SECURITY DEFINER;

-- Use a fixed search path to prevent object shadowing.

ALTER FUNCTION public.transfer_funds(
    BIGINT,
    BIGINT,
    NUMERIC,
    VARCHAR,
    TEXT
) SET search_path = pg_catalog, public;

-- The transfer role no longer needs schema CREATE access.

REVOKE CREATE ON SCHEMA public
FROM securebank_transfer;

-- 7. Remove public access to the transfer function.

REVOKE ALL ON FUNCTION public.transfer_funds(
    BIGINT,
    BIGINT,
    NUMERIC,
    VARCHAR,
    TEXT
) FROM PUBLIC;

-- 8. Only the application role can execute transfers.

GRANT EXECUTE ON FUNCTION public.transfer_funds(
    BIGINT,
    BIGINT,
    NUMERIC,
    VARCHAR,
    TEXT
) TO securebank_app;

COMMIT;

-- ============================================================
-- End of security configuration
-- ============================================================
