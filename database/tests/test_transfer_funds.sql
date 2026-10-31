
-- ============================================================
-- SecureBank: Automated Fund Transfer Tests
-- File: database/tests/test_transfer_funds.sql
-- ============================================================

BEGIN;

DO $$
DECLARE
    v_user_id BIGINT;
    v_source_id BIGINT;
    v_destination_id BIGINT;
    v_inactive_id BIGINT;
    v_transaction_id BIGINT;
    v_balance NUMERIC(19,4);
    v_count INTEGER;
BEGIN
    -- --------------------------------------------------------
    -- TEST SETUP: Create temporary test user and accounts
    -- --------------------------------------------------------

    INSERT INTO users (
        username, password_hash, email, phone, role
    )
    VALUES (
        'sql_test_user',
        'test_hash',
        'sql_test_user@example.com',
        '9999999999',
        'Customer'
    )
    RETURNING user_id INTO v_user_id;

    INSERT INTO accounts (
        user_id, account_number, account_type,
        balance, currency, status
    )
    VALUES (
        v_user_id, 'SQLTEST1001', 'Savings',
        10000, 'INR', 'Active'
    )
    RETURNING account_id INTO v_source_id;

    INSERT INTO accounts (
        user_id, account_number, account_type,
        balance, currency, status
    )
    VALUES (
        v_user_id, 'SQLTEST1002', 'Savings',
        5000, 'INR', 'Active'
    )
    RETURNING account_id INTO v_destination_id;

    INSERT INTO accounts (
        user_id, account_number, account_type,
        balance, currency, status
    )
    VALUES (
        v_user_id, 'SQLTEST1003', 'Savings',
        2000, 'INR', 'Frozen'
    )
    RETURNING account_id INTO v_inactive_id;

    RAISE NOTICE 'Test setup completed';

    -- --------------------------------------------------------
    -- TEST 1: Successful transfer
    -- --------------------------------------------------------

    v_transaction_id := transfer_funds(
        v_source_id,
        v_destination_id,
        1000,
        'Transfer',
        'Automated test transfer'
    );

    SELECT balance INTO v_balance
    FROM accounts WHERE account_id = v_source_id;

    IF v_balance <> 9000 THEN
        RAISE EXCEPTION 'TEST 1 FAILED: Incorrect source balance';
    END IF;

    SELECT balance INTO v_balance
    FROM accounts WHERE account_id = v_destination_id;

    IF v_balance <> 6000 THEN
        RAISE EXCEPTION 'TEST 1 FAILED: Incorrect destination balance';
    END IF;

    SELECT COUNT(*) INTO v_count
    FROM transactions
    WHERE transaction_id = v_transaction_id
      AND status = 'Completed';

    IF v_count <> 1 THEN
        RAISE EXCEPTION 'TEST 1 FAILED: Transaction not recorded';
    END IF;

    RAISE NOTICE 'TEST 1 PASSED: Successful transfer';

    -- --------------------------------------------------------
    -- TEST 2: Insufficient balance
    -- --------------------------------------------------------

    BEGIN
        PERFORM transfer_funds(
            v_source_id, v_destination_id,
            50000, 'Transfer', 'Insufficient balance test'
        );

        RAISE EXCEPTION 'TEST 2 FAILED: Expected insufficient balance error';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM = 'Insufficient balance in source account' THEN
                RAISE NOTICE 'TEST 2 PASSED: Insufficient balance rejected';
            ELSE
                RAISE;
            END IF;
    END;

    -- --------------------------------------------------------
    -- TEST 3: Zero amount
    -- --------------------------------------------------------

    BEGIN
        PERFORM transfer_funds(
            v_source_id, v_destination_id,
            0, 'Transfer', 'Zero amount test'
        );

        RAISE EXCEPTION 'TEST 3 FAILED: Expected zero amount error';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM = 'Transfer amount must be greater than zero' THEN
                RAISE NOTICE 'TEST 3 PASSED: Zero amount rejected';
            ELSE
                RAISE;
            END IF;
    END;

    -- --------------------------------------------------------
    -- TEST 4: Negative amount
    -- --------------------------------------------------------

    BEGIN
        PERFORM transfer_funds(
            v_source_id, v_destination_id,
            -100, 'Transfer', 'Negative amount test'
        );

        RAISE EXCEPTION 'TEST 4 FAILED: Expected negative amount error';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM = 'Transfer amount must be greater than zero' THEN
                RAISE NOTICE 'TEST 4 PASSED: Negative amount rejected';
            ELSE
                RAISE;
            END IF;
    END;

    -- --------------------------------------------------------
    -- TEST 5: Same source and destination
    -- --------------------------------------------------------

    BEGIN
        PERFORM transfer_funds(
            v_source_id, v_source_id,
            100, 'Transfer', 'Same account test'
        );

        RAISE EXCEPTION 'TEST 5 FAILED: Expected same account error';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM = 'Source and destination accounts must be different' THEN
                RAISE NOTICE 'TEST 5 PASSED: Same account rejected';
            ELSE
                RAISE;
            END IF;
    END;

    -- --------------------------------------------------------
    -- TEST 6: Non-existent source account
    -- --------------------------------------------------------

    BEGIN
        PERFORM transfer_funds(
            999999999, v_destination_id,
            100, 'Transfer', 'Invalid account test'
        );

        RAISE EXCEPTION 'TEST 6 FAILED: Expected missing account error';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM LIKE 'Source account % does not exist' THEN
                RAISE NOTICE 'TEST 6 PASSED: Missing account rejected';
            ELSE
                RAISE;
            END IF;
    END;

    -- --------------------------------------------------------
    -- TEST 7: Inactive source account
    -- --------------------------------------------------------

    BEGIN
        PERFORM transfer_funds(
            v_inactive_id, v_destination_id,
            100, 'Transfer', 'Inactive account test'
        );

        RAISE EXCEPTION 'TEST 7 FAILED: Expected inactive account error';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM = 'Source account is not active' THEN
                RAISE NOTICE 'TEST 7 PASSED: Inactive account rejected';
            ELSE
                RAISE;
            END IF;
    END;

    -- --------------------------------------------------------
    -- TEST 8: Empty transaction type
    -- --------------------------------------------------------

    BEGIN
        PERFORM transfer_funds(
            v_source_id, v_destination_id,
            100, '   ', 'Empty transaction type test'
        );

        RAISE EXCEPTION 'TEST 8 FAILED: Expected empty type error';
    EXCEPTION
        WHEN OTHERS THEN
            IF SQLERRM = 'Transaction type cannot be empty' THEN
                RAISE NOTICE 'TEST 8 PASSED: Empty transaction type rejected';
            ELSE
                RAISE;
            END IF;
    END;

    RAISE NOTICE 'ALL 8 FUND TRANSFER TESTS PASSED';

END;
$$;

-- Remove all test users, accounts and transactions.
ROLLBACK;
