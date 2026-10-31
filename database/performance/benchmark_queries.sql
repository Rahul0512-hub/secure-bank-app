
-- SecureBank Database Performance Benchmark
-- Temporary benchmark data is rolled back after testing.

BEGIN;

-- 1. Generate 1,000 temporary users.
INSERT INTO users (username, password_hash, email, phone, role)
SELECT
    'perf_user_' || i,
    'benchmark_hash',
    'perf_user_' || i || '@example.com',
    '900000' || LPAD(i::TEXT, 4, '0'),
    'Customer'
FROM generate_series(1, 1000) AS i;

-- 2. Generate 1,000 accounts.
INSERT INTO accounts (
    user_id, account_number, account_type,
    balance, currency, status
)
SELECT
    u.user_id,
    'PERF' || LPAD(i::TEXT, 8, '0'),
    'Savings',
    10000.00,
    'INR',
    'Active'
FROM generate_series(1, 1000) AS i
JOIN users u ON u.username = 'perf_user_' || i;

-- 3. Generate 500 loans.
INSERT INTO loans (
    user_id, loan_amount, interest_rate,
    status, start_date, end_date
)
SELECT
    u.user_id,
    50000.00,
    8.5,
    'Active',
    CURRENT_DATE,
    CURRENT_DATE + INTERVAL '1 year'
FROM generate_series(1, 500) AS i
JOIN users u ON u.username = 'perf_user_' || i;

-- 4. Generate 10,000 transactions.
INSERT INTO transactions (
    source_account_id,
    destination_account_id,
    amount,
    transaction_type,
    description,
    status,
    created_at
)
SELECT
    source.account_id,
    destination.account_id,
    100.00 + (i % 1000),
    'Transfer',
    'Performance benchmark transaction',
    'Completed',
    NOW() - (i || ' seconds')::INTERVAL
FROM generate_series(1, 10000) AS i
JOIN accounts source
    ON source.account_number =
       'PERF' || LPAD((((i - 1) % 1000) + 1)::TEXT, 8, '0')
JOIN accounts destination
    ON destination.account_number =
       'PERF' || LPAD(((i % 1000) + 1)::TEXT, 8, '0');

-- 5. Update planner statistics.
ANALYZE users;
ANALYZE accounts;
ANALYZE loans;
ANALYZE transactions;

-- 6. Benchmark account lookup by user.
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM accounts
WHERE user_id = (
    SELECT user_id
    FROM users
    WHERE username = 'perf_user_1'
);

-- 7. Benchmark loan lookup by user.
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM loans
WHERE user_id = (
    SELECT user_id
    FROM users
    WHERE username = 'perf_user_1'
);

-- 8. Benchmark transactions by source account.
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM transactions
WHERE source_account_id = (
    SELECT account_id
    FROM accounts
    WHERE account_number = 'PERF00000001'
);

-- 9. Benchmark transactions by destination account.
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM transactions
WHERE destination_account_id = (
    SELECT account_id
    FROM accounts
    WHERE account_number = 'PERF00000001'
);

-- 10. Benchmark recent transaction retrieval.
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM transactions
ORDER BY created_at DESC
LIMIT 20;

-- 11. Confirm temporary benchmark row counts.
SELECT 'users' AS table_name, COUNT(*) AS total_rows
FROM users WHERE username LIKE 'perf_user_%'
UNION ALL
SELECT 'accounts', COUNT(*)
FROM accounts WHERE account_number LIKE 'PERF%'
UNION ALL
SELECT 'loans', COUNT(*)
FROM loans
WHERE user_id IN (
    SELECT user_id FROM users WHERE username LIKE 'perf_user_%'
)
UNION ALL
SELECT 'transactions', COUNT(*)
FROM transactions
WHERE description = 'Performance benchmark transaction';

-- 12. Remove all benchmark data.
ROLLBACK;
