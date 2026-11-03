-- SecureBank: Customer registration function permissions

BEGIN;

-- Temporarily allow the restricted role to own the function.
GRANT CREATE ON SCHEMA public TO securebank_registration;

-- Run the function with restricted registration privileges.
ALTER FUNCTION public.register_customer(
    VARCHAR,
    TEXT,
    VARCHAR,
    VARCHAR
)
OWNER TO securebank_registration;

-- Remove temporary schema creation permission.
REVOKE CREATE ON SCHEMA public FROM securebank_registration;

-- Remove default public execution access.
REVOKE ALL ON FUNCTION public.register_customer(
    VARCHAR,
    TEXT,
    VARCHAR,
    VARCHAR
)
FROM PUBLIC;

-- Allow the application permission group to register customers.
GRANT EXECUTE ON FUNCTION public.register_customer(
    VARCHAR,
    TEXT,
    VARCHAR,
    VARCHAR
)
TO securebank_app;

COMMIT;
