-- SecureBank: Restricted user authentication function

CREATE OR REPLACE FUNCTION public.get_auth_user(
    p_username VARCHAR(50)
)
RETURNS TABLE (
    user_id BIGINT,
    username VARCHAR(50),
    password_hash TEXT,
    role VARCHAR(20)
)
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
    SELECT
        u.user_id,
        u.username,
        u.password_hash,
        u.role
    FROM public.users AS u
    WHERE u.username = p_username
    LIMIT 1;
$$;
