-- SecureBank: Restricted customer registration role

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = 'securebank_registration'
    ) THEN
        CREATE ROLE securebank_registration NOLOGIN NOINHERIT;
    END IF;
END;
$$;

GRANT USAGE ON SCHEMA public TO securebank_registration;

GRANT INSERT (
    username,
    password_hash,
    email,
    phone,
    role
)
ON public.users
TO securebank_registration;

GRANT SELECT (
    user_id,
    username,
    email,
    phone,
    role,
    created_at
)
ON public.users
TO securebank_registration;

GRANT USAGE, SELECT
ON SEQUENCE public.users_user_id_seq
TO securebank_registration;

COMMIT;
