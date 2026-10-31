-- ============================================================
-- SecureBank: Automated Database Integrity Tests
-- File: database/tests/test_database_integrity.sql
-- ============================================================

BEGIN;

DO $$
DECLARE
    v_user_id BIGINT;
    v_account_id BIGINT;
    v_destination_id BIGINT;
    v_denied BOOLEAN;
BEGIN
    -- --------------------------------------------------------
    -- TEST SETUP
    -- --------------------------------------------------------

    INSERT INTO users (
        username, password_hash, email, phone, role
    )
    VALUES (
        'integrity_test_user',
        'test_hash',
        'integrity_test@example.com',
        '9999999997',
        'Customer'
    )
    RETURNING user_id INTO v_user_id;

    INSERT INTO accounts (
        user_id, account_number, account_type,
        balance, currency, status
    )
    VALUES (
        v_user_id, 'INTEGRITY1001', 'Savings',
        10000, 'INR', 'Active'
    )
    RETURNING account_id INTO v_account_id;

    INSERT INTO accounts (
        user_id, account_number, account_type,
        balance, currency, status
    )
    VALUES (
        v_user_id, 'INTEGRITY1002', 'Savings',
        5000, 'INR', 'Active'
    )
    RETURNING account_id INTO v_destination_id;

    RAISE NOTICE 'Integrity test setup completed';

    -- --------------------------------------------------------
    -- TEST 1: Negative account balance rejected
    -- --------------------------------------------------------

    v_denied := FALSE;

    BEGIN
        INSERT INTO accounts (
            user_id, account_number, account_type,
            balance, currency, status
        )
        VALUES (
            v_user_id, 'INTEGRITY1003', 'Savings',
            -100, 'INR', 'Active'
        );
    EXCEPTION
        WHEN check_violation THEN
            v_denied := TRUE;
    END;

    IF NOT v_denied THEN
        RAISE EXCEPTION 'TEST 1 FAILED: Negative balance allowed';
    END IF;

    RAISE NOTICE 'TEST 1 PASSED: Negative balance rejected';

    -- --------------------------------------------------------
    -- TEST 2: Invalid user foreign key rejected
    -- --------------------------------------------------------

    v_denied := FALSE;

    BEGIN
        INSERT INTO accounts (
            user_id, account_number, account_type,
            balance, currency, status
        )
        VALUES (
            999999999, 'INTEGRITY1004', 'Savings',
            1000, 'INR', 'Active'
        );
    EXCEPTION
        WHEN foreign_key_violation THEN
            v_denied := TRUE;
    END;

    IF NOT v_denied THEN
        RAISE EXCEPTION 'TEST 2 FAILED: Invalid user reference allowed';
    END IF;

    RAISE NOTICE 'TEST 2 PASSED: Invalid user reference rejected';

    -- --------------------------------------------------------
    -- TEST 3: Zero loan amount rejected
    -- --------------------------------------------------------

    v_denied := FALSE;

    BEGIN
        INSERT INTO loans (
            user_id, loan_amount, interest_rate, status
        )
        VALUES (
            v_user_id, 0, 5.5, 'Pending'
        );
    EXCEPTION
        WHEN check_violation THEN
            v_denied := TRUE;
    END;

    IF NOT v_denied THEN
        RAISE EXCEPTION 'TEST 3 FAILED: Zero loan amount allowed';
    END IF;

    RAISE NOTICE 'TEST 3 PASSED: Zero loan amount rejected';

    -- --------------------------------------------------------
    -- TEST 4: Negative interest rate rejected
    -- --------------------------------------------------------

    v_denied := FALSE;

    BEGIN
        INSERT INTO loans (
            user_id, loan_amount, interest_rate, status
        )
        VALUES (
            v_user_id, 50000, -2, 'Pending'
        );
    EXCEPTION
        WHEN check_violation THEN
            v_denied := TRUE;
    END;

    IF NOT v_denied THEN
        RAISE EXCEPTION 'TEST 4 FAILED: Negative interest rate allowed';
    END IF;

    RAISE NOTICE 'TEST 4 PASSED: Negative interest rate rejected';

    -- --------------------------------------------------------
    -- TEST 5: Invalid loan date range rejected
    -- --------------------------------------------------------

    v_denied := FALSE;

    BEGIN
        INSERT INTO loans (
            user_id, loan_amount, interest_rate,
            status, start_date, end_date
        )
        VALUES (
            v_user_id, 50000, 5.5,
            'Pending', DATE '2026-12-31', DATE '2026-01-01'
        );
    EXCEPTION
        WHEN check_violation THEN
            v_denied := TRUE;
    END;

    IF NOT v_denied THEN
        RAISE EXCEPTION 'TEST 5 FAILED: Invalid loan date range allowed';
    END IF;

    RAISE NOTICE 'TEST 5 PASSED: Invalid loan date range rejected';

    -- --------------------------------------------------------
    -- TEST 6: Zero transaction amount rejected
    -- --------------------------------------------------------

    v_denied := FALSE;

    BEGIN
        INSERT INTO transactions (
            source_account_id, destination_account_id,
            amount, transaction_type, description, status
        )
        VALUES (
            v_account_id, v_destination_id,
            0, 'Transfer', 'Integrity test', 'Completed'
        );
    EXCEPTION
        WHEN check_violation THEN
            v_denied := TRUE;
    END;

    IF NOT v_denied THEN
        RAISE EXCEPTION 'TEST 6 FAILED: Zero transaction amount allowed';
    END IF;

    RAISE NOTICE 'TEST 6 PASSED: Zero transaction amount rejected';

    -- --------------------------------------------------------
    -- TEST 7: Invalid account foreign key rejected
    -- --------------------------------------------------------

    v_denied := FALSE;

    BEGIN
        INSERT INTO transactions (
            source_account_id, destination_account_id,
            amount, transaction_type, description, status
        )
        VALUES (
            999999999, v_destination_id,
            100, 'Transfer', 'Integrity test', 'Completed'
        );
    EXCEPTION
        WHEN foreign_key_violation THEN
            v_denied := TRUE;
    END;

    IF NOT v_denied THEN
        RAISE EXCEPTION 'TEST 7 FAILED: Invalid account reference allowed';
    END IF;

    RAISE NOTICE 'TEST 7 PASSED: Invalid account reference rejected';

    -- --------------------------------------------------------
    -- TEST 8: Same source and destination rejected
    -- --------------------------------------------------------

    v_denied := FALSE;

    BEGIN
        INSERT INTO transactions (
            source_account_id, destination_account_id,
            amount, transaction_type, description, status
        )
        VALUES (
            v_account_id, v_account_id,
            100, 'Transfer', 'Same account test', 'Completed'
        );
    EXCEPTION
        WHEN check_violation THEN
            v_denied := TRUE;
    END;

    IF NOT v_denied THEN
        RAISE EXCEPTION 'TEST 8 FAILED: Same account transaction allowed';
    END IF;

    RAISE NOTICE 'TEST 8 PASSED: Same account transaction rejected';

    RAISE NOTICE 'ALL 8 DATABASE INTEGRITY TESTS PASSED';

END;
$$;

-- Remove all test data.
ROLLBACK;