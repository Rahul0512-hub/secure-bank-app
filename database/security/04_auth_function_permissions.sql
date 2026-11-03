-- SecureBank: Authentication function permissions

BEGIN;

-- Temporarily allow the restricted role to own the function.
GRANT CREATE ON SCHEMA public TO securebank_auth;

-- Make the function execute with restricted authentication privileges.
ALTER FUNCTION public.get_auth_user(VARCHAR)
OWNER TO securebank_auth;

-- Remove temporary schema creation permission.
REVOKE CREATE ON SCHEMA public FROM securebank_auth;

-- Remove default public execution access.
REVOKE ALL ON FUNCTION public.get_auth_user(VARCHAR)
FROM PUBLIC;

-- Allow the application permission group to call the function.
GRANT EXECUTE ON FUNCTION public.get_auth_user(VARCHAR)
TO securebank_app;

COMMIT;
