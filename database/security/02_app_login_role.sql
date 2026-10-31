-- Create the application login role if it does not exist.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'securebank_app_login'
    ) THEN
        EXECUTE 'CREATE ROLE securebank_app_login LOGIN INHERIT';
    END IF;
END
$$;

-- Ensure the role can log in and inherit application permissions.
ALTER ROLE securebank_app_login LOGIN INHERIT;

-- Grant the application permission group to the login role.
GRANT securebank_app TO securebank_app_login;
