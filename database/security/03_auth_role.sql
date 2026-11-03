-- SecureBank: Restricted authentication role

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'securebank_auth'
    ) THEN
        CREATE ROLE securebank_auth NOLOGIN NOINHERIT;
    END IF;
END;
$$;

GRANT USAGE ON SCHEMA public TO securebank_auth;

GRANT SELECT (
    user_id,
    username,
    password_hash,
    role
)
ON public.users
TO securebank_auth;

COMMIT;
