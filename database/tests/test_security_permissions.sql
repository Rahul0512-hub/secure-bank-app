
-- ============================================================
-- SecureBank: Automated Database Security Permission Tests
-- File: database/tests/test_security_permissions.sql
-- ============================================================

BEGIN;

-- ------------------------------------------------------------
-- TEST SETUP: Create test user and accounts as administrator
-- ------------------------------------------------------------

CREATE TEMP TABLE security_test_ids (
    source_account_id BIGINT,
    destination_account_id BIGINT
);

INSERT INTO users (
    username, password_hash, email, phone, role
)
VALUES (
    'security_test_user',
    'test_hash',
    'security_test_user@example.com',
    '9999999998',
    'Customer'
)
RETURNING user_id
\gset

INSERT INTO accounts (
    user_id, account_number, account_type,
    balance, currency, status
)
VALUES (
    :user_id, 'SECURITY1001', 'Savings',
    10000, 'INR', 'Active'
)
RETURNING account_id
\gset source_

INSERT INTO accounts (
    user_id, account_number, account_type,
    balance, currency, status
)
VALUES (
    :user_id, 'SECURITY1002', 'Savings',
    5000, 'INR', 'Active'
)
RETURNING account_id
\gset destination_

INSERT INTO security_test_ids
VALUES (:source_account_id, :destination_account_id);

GRANT SELECT ON security_test_ids TO securebank_app_login;

-- ------------------------------------------------------------
-- TEST EXECUTION: Switch to actual application login
-- ------------------------------------------------------------

SET LOCAL ROLE securebank_app_login;

DO $$
DECLARE
    v_source_id BIGINT;
    v_destination_id BIGINT;
    v_balance NUMERIC(19,4);
    v_transaction_id BIGINT;
    v_denied BOOLEAN;
    v_count INTEGER;
BEGIN
    SELECT source_account_id, destination_account_id
    INTO v_source_id, v_destination_id
    FROM security_test_ids;

    -- TEST 1: Application can read accounts.

    PERFORM account_id
    FROM public.accounts
    WHERE account_id = v_source_id;

    RAISE NOTICE 'TEST 1 PASSED: Application can read accounts';

    -- TEST 2: Application can read loans.

    PERFORM loan_id FROM public.loans LIMIT 1;

    RAISE NOTICE 'TEST 2 PASSED: Application can read loans';

    -- TEST 3: Application can read transactions.

    PERFORM transaction_id FROM public.transactions LIMIT 1;

    RAISE NOTICE 'TEST 3 PASSED: Application can read transactions';

    -- TEST 4: Application cannot read users directly.

    v_denied := FALSE;

    BEGIN
        PERFORM user_id FROM public.users LIMIT 1;
    EXCEPTION
        WHEN insufficient_privilege THEN
            v_denied := TRUE;
    END;

    IF NOT v_denied THEN
        RAISE EXCEPTION
            'TEST 4 FAILED: Application unexpectedly read users';
    END IF;

    RAISE NOTICE 'TEST 4 PASSED: Direct users access denied';

    -- TEST 5: Application cannot directly update account balances.

    v_denied := FALSE;

    BEGIN
        UPDATE public.accounts
        SET balance = balance + 100
        WHERE account_id = v_source_id;
    EXCEPTION
        WHEN insufficient_privilege THEN
            v_denied := TRUE;
    END;

    IF NOT v_denied THEN
        RAISE EXCEPTION
            'TEST 5 FAILED: Direct account update was allowed';
    END IF;

    RAISE NOTICE 'TEST 5 PASSED: Direct account update denied';

    -- TEST 6: Application cannot directly insert transactions.

    v_denied := FALSE;

    BEGIN
        INSERT INTO public.transactions (
            source_account_id,
            destination_account_id,
            amount,
            transaction_type,
            description,
            status
        )
        VALUES (
            v_source_id,
            v_destination_id,
            100,
            'Transfer',
            'Unauthorized security test',
            'Completed'
        );
    EXCEPTION
        WHEN insufficient_privilege THEN
            v_denied := TRUE;
    END;

    IF NOT v_denied THEN
        RAISE EXCEPTION
            'TEST 6 FAILED: Direct transaction insertion was allowed';
    END IF;

    RAISE NOTICE 'TEST 6 PASSED: Direct transaction insertion denied';

    -- TEST 7: Application can execute the secure transfer function.

    v_transaction_id := public.transfer_funds(
        v_source_id,
        v_destination_id,
        1000,
        'Transfer',
        'Security permission test'
    );

    IF v_transaction_id IS NULL THEN
        RAISE EXCEPTION
            'TEST 7 FAILED: Transfer function returned NULL';
    END IF;

    RAISE NOTICE 'TEST 7 PASSED: Secure transfer function executed';

    -- TEST 8: Verify source balance after transfer.

    SELECT balance INTO v_balance
    FROM public.accounts
    WHERE account_id = v_source_id;

    IF v_balance <> 9000 THEN
        RAISE EXCEPTION
            'TEST 8 FAILED: Incorrect source balance: %', v_balance;
    END IF;

    RAISE NOTICE 'TEST 8 PASSED: Source balance verified';

    -- TEST 9: Verify destination balance after transfer.

    SELECT balance INTO v_balance
    FROM public.accounts
    WHERE account_id = v_destination_id;

    IF v_balance <> 6000 THEN
        RAISE EXCEPTION
            'TEST 9 FAILED: Incorrect destination balance: %', v_balance;
    END IF;

    RAISE NOTICE 'TEST 9 PASSED: Destination balance verified';

    -- TEST 10: Verify completed transaction record.

    SELECT COUNT(*) INTO v_count
    FROM public.transactions
    WHERE transaction_id = v_transaction_id
      AND status = 'Completed';

    IF v_count <> 1 THEN
        RAISE EXCEPTION
            'TEST 10 FAILED: Transaction record not found';
    END IF;

    RAISE NOTICE 'TEST 10 PASSED: Transaction record verified';

    RAISE NOTICE 'ALL 10 DATABASE SECURITY TESTS PASSED';
END;
$$;

-- ------------------------------------------------------------
-- ROLLBACK: Remove all test data
-- ------------------------------------------------------------

ROLLBACK;
