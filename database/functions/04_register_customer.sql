-- SecureBank: Customer registration function

CREATE OR REPLACE FUNCTION public.register_customer(
    p_username VARCHAR(50),
    p_password_hash TEXT,
    p_email VARCHAR(255),
    p_phone VARCHAR(20) DEFAULT NULL
)
RETURNS TABLE (
    user_id BIGINT,
    username VARCHAR(50),
    email VARCHAR(255),
    phone VARCHAR(20),
    role VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE SQL
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
    INSERT INTO public.users (
        username,
        password_hash,
        email,
        phone,
        role
    )
    VALUES (
        p_username,
        p_password_hash,
        p_email,
        p_phone,
        'Customer'
    )
    RETURNING
        users.user_id,
        users.username,
        users.email,
        users.phone,
        users.role,
        users.created_at;
$$;
