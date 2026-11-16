-- ============================================================
-- SecureBank: User Profile, Account Management & Loan Functions
-- File: database/functions/05_account_and_loan_functions.sql
-- Purpose: Provide principle-of-least-privilege operations for
--          user profile retrieval, account opening/status, and loan lifecycle.
-- ============================================================

BEGIN;

-- 1. User Profile Retrieval
CREATE OR REPLACE FUNCTION public.get_user_profile(
    p_user_id BIGINT
)
RETURNS TABLE (
    user_id BIGINT,
    username VARCHAR(50),
    email VARCHAR(255),
    phone VARCHAR(20),
    role VARCHAR(20),
    created_at TIMESTAMPTZ
)
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
    SELECT
        u.user_id,
        u.username,
        u.email,
        u.phone,
        u.role,
        u.created_at
    FROM public.users AS u
    WHERE u.user_id = p_user_id
    LIMIT 1;
$$;

-- 2. Admin: Get All Users
CREATE OR REPLACE FUNCTION public.get_all_users()
RETURNS TABLE (
    user_id BIGINT,
    username VARCHAR(50),
    email VARCHAR(255),
    phone VARCHAR(20),
    role VARCHAR(20),
    created_at TIMESTAMPTZ
)
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
    SELECT
        u.user_id,
        u.username,
        u.email,
        u.phone,
        u.role,
        u.created_at
    FROM public.users AS u
    ORDER BY u.user_id ASC;
$$;

-- 2b. Safe Transfer Recipient Accounts (Customer visibility)
CREATE OR REPLACE FUNCTION public.get_transfer_recipients()
RETURNS TABLE (
    account_id BIGINT,
    account_number VARCHAR(34),
    account_type VARCHAR(30),
    owner_username VARCHAR(50)
)
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
    SELECT
        a.account_id,
        a.account_number,
        a.account_type,
        u.username AS owner_username
    FROM public.accounts AS a
    JOIN public.users AS u ON u.user_id = a.user_id
    WHERE a.status = 'Active'
    ORDER BY a.account_id ASC;
$$;

-- 3. Open Account Function
CREATE OR REPLACE FUNCTION public.open_account(
    p_user_id BIGINT,
    p_account_number VARCHAR(34),
    p_account_type VARCHAR(30),
    p_initial_balance NUMERIC(19, 4) DEFAULT 0,
    p_currency CHAR(3) DEFAULT 'INR'
)
RETURNS TABLE (
    account_id BIGINT,
    user_id BIGINT,
    account_number VARCHAR(34),
    account_type VARCHAR(30),
    balance NUMERIC(19, 4),
    currency CHAR(3),
    status VARCHAR(20)
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
DECLARE
    v_account_id BIGINT;
BEGIN
    IF p_initial_balance < 0 THEN
        RAISE EXCEPTION 'Initial balance cannot be negative';
    END IF;

    IF p_account_type NOT IN ('Savings', 'Checking', 'Investment', 'Business', 'Fixed Deposit') THEN
        RAISE EXCEPTION 'Invalid account type: %', p_account_type;
    END IF;

    -- Ensure user exists
    IF NOT EXISTS (SELECT 1 FROM public.users WHERE users.user_id = p_user_id) THEN
        RAISE EXCEPTION 'User % does not exist', p_user_id;
    END IF;

    INSERT INTO public.accounts (
        user_id,
        account_number,
        account_type,
        balance,
        currency,
        status
    )
    VALUES (
        p_user_id,
        p_account_number,
        p_account_type,
        p_initial_balance,
        p_currency,
        'Active'
    )
    RETURNING accounts.account_id INTO v_account_id;

    RETURN QUERY
    SELECT
        a.account_id,
        a.user_id,
        a.account_number,
        a.account_type,
        a.balance,
        a.currency,
        a.status
    FROM public.accounts AS a
    WHERE a.account_id = v_account_id;
END;
$$;

-- 4. Set Account Status (Active, Frozen, Closed)
CREATE OR REPLACE FUNCTION public.set_account_status(
    p_account_id BIGINT,
    p_status VARCHAR(20)
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
BEGIN
    IF p_status NOT IN ('Active', 'Frozen', 'Closed') THEN
        RAISE EXCEPTION 'Invalid account status: %', p_status;
    END IF;

    UPDATE public.accounts
    SET status = p_status
    WHERE account_id = p_account_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account % not found', p_account_id;
    END IF;

    RETURN TRUE;
END;
$$;

-- 5. Loan Application Function
CREATE OR REPLACE FUNCTION public.apply_loan(
    p_user_id BIGINT,
    p_loan_amount NUMERIC(19, 4),
    p_interest_rate NUMERIC(7, 4),
    p_start_date DATE DEFAULT CURRENT_DATE,
    p_end_date DATE DEFAULT (CURRENT_DATE + INTERVAL '12 months')::date
)
RETURNS TABLE (
    loan_id BIGINT,
    user_id BIGINT,
    loan_amount NUMERIC(19, 4),
    interest_rate NUMERIC(7, 4),
    status VARCHAR(20),
    start_date DATE,
    end_date DATE
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
DECLARE
    v_loan_id BIGINT;
BEGIN
    IF p_loan_amount <= 0 THEN
        RAISE EXCEPTION 'Loan amount must be greater than zero';
    END IF;

    IF p_interest_rate < 0 THEN
        RAISE EXCEPTION 'Interest rate cannot be negative';
    END IF;

    IF p_end_date IS NOT NULL AND p_start_date IS NOT NULL AND p_end_date < p_start_date THEN
        RAISE EXCEPTION 'Loan end date must be after start date';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM public.users WHERE users.user_id = p_user_id) THEN
        RAISE EXCEPTION 'User % does not exist', p_user_id;
    END IF;

    INSERT INTO public.loans (
        user_id,
        loan_amount,
        interest_rate,
        status,
        start_date,
        end_date
    )
    VALUES (
        p_user_id,
        p_loan_amount,
        p_interest_rate,
        'Pending',
        p_start_date,
        p_end_date
    )
    RETURNING loans.loan_id INTO v_loan_id;

    RETURN QUERY
    SELECT
        l.loan_id,
        l.user_id,
        l.loan_amount,
        l.interest_rate,
        l.status,
        l.start_date,
        l.end_date
    FROM public.loans AS l
    WHERE l.loan_id = v_loan_id;
END;
$$;

-- 6. Update Loan Status
CREATE OR REPLACE FUNCTION public.update_loan_status(
    p_loan_id BIGINT,
    p_status VARCHAR(20)
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
BEGIN
    IF p_status NOT IN ('Pending', 'Approved', 'Rejected', 'Active', 'Paid', 'Defaulted') THEN
        RAISE EXCEPTION 'Invalid loan status: %', p_status;
    END IF;

    UPDATE public.loans
    SET status = p_status
    WHERE loan_id = p_loan_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Loan % not found', p_loan_id;
    END IF;

    RETURN TRUE;
END;
$$;

-- 7. Get Outbox Stats
CREATE OR REPLACE FUNCTION public.get_outbox_stats()
RETURNS TABLE (
    total_events BIGINT,
    pending_events BIGINT,
    delivered_events BIGINT,
    failed_events BIGINT
)
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
    SELECT
        COUNT(*)::BIGINT AS total_events,
        COUNT(*) FILTER (WHERE delivered_at IS NULL)::BIGINT AS pending_events,
        COUNT(*) FILTER (WHERE delivered_at IS NOT NULL)::BIGINT AS delivered_events,
        COUNT(*) FILTER (WHERE attempts > 0 AND delivered_at IS NULL)::BIGINT AS failed_events
    FROM public.transaction_audit_outbox;
$$;

-- Grant permissions to securebank_app
REVOKE ALL ON FUNCTION public.get_user_profile(BIGINT) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.get_user_profile(BIGINT) TO securebank_app;

REVOKE ALL ON FUNCTION public.get_all_users() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.get_all_users() TO securebank_app;

REVOKE ALL ON FUNCTION public.get_transfer_recipients() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.get_transfer_recipients() TO securebank_app;

REVOKE ALL ON FUNCTION public.open_account(BIGINT, VARCHAR, VARCHAR, NUMERIC, CHAR) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.open_account(BIGINT, VARCHAR, VARCHAR, NUMERIC, CHAR) TO securebank_app;

REVOKE ALL ON FUNCTION public.set_account_status(BIGINT, VARCHAR) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.set_account_status(BIGINT, VARCHAR) TO securebank_app;

REVOKE ALL ON FUNCTION public.apply_loan(BIGINT, NUMERIC, NUMERIC, DATE, DATE) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.apply_loan(BIGINT, NUMERIC, NUMERIC, DATE, DATE) TO securebank_app;

REVOKE ALL ON FUNCTION public.update_loan_status(BIGINT, VARCHAR) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.update_loan_status(BIGINT, VARCHAR) TO securebank_app;

REVOKE ALL ON FUNCTION public.get_outbox_stats() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.get_outbox_stats() TO securebank_app;

COMMIT;
