-- ============================================================
-- SecureBank: Initial Seed Users and Accounts
-- File: database/init/07_seed_users_and_accounts.sql
-- Purpose: Seeds default administrator and customer accounts
--          for out-of-the-box development and testing.
-- ============================================================

BEGIN;

-- 1. Default Administrator (password: AdminPass@123)
INSERT INTO public.users (username, password_hash, email, phone, role)
VALUES (
    'admin',
    '$argon2id$v=19$m=65536,t=3,p=4$LV5TmdHV57W+V8uPhOd9+A$sj0j52gj+P2fttZxlr/UwbMTrZPjHA972FrIOjc7StE',
    'admin@securebank.com',
    '9876543200',
    'Admin'
)
ON CONFLICT (username) DO NOTHING;

-- 2. Demo Customer (password: CustomerPass@123)
INSERT INTO public.users (username, password_hash, email, phone, role)
VALUES (
    'customer',
    '$argon2id$v=19$m=65536,t=3,p=4$L6rRmyLLPMNBZCJKCePiuw$xjrlF9bpgAbpFVnyY2r7n7PLo0MjvkRwkiOyGC+tN8A',
    'customer@securebank.com',
    '9876543210',
    'Customer'
)
ON CONFLICT (username) DO NOTHING;

-- 3. Second Customer (password: CustomerPass@123)
INSERT INTO public.users (username, password_hash, email, phone, role)
VALUES (
    'john_doe',
    '$argon2id$v=19$m=65536,t=3,p=4$L6rRmyLLPMNBZCJKCePiuw$xjrlF9bpgAbpFVnyY2r7n7PLo0MjvkRwkiOyGC+tN8A',
    'john.doe@securebank.com',
    '9876543220',
    'Customer'
)
ON CONFLICT (username) DO NOTHING;

-- 4. Demo Accounts
INSERT INTO public.accounts (user_id, account_number, account_type, balance, currency, status)
SELECT u.user_id, 'SB1000000001', 'Savings', 50000.0000, 'INR', 'Active'
FROM public.users u
WHERE u.username = 'customer'
ON CONFLICT (account_number) DO NOTHING;

INSERT INTO public.accounts (user_id, account_number, account_type, balance, currency, status)
SELECT u.user_id, 'SB1000000002', 'Current', 25000.0000, 'INR', 'Active'
FROM public.users u
WHERE u.username = 'customer'
ON CONFLICT (account_number) DO NOTHING;

INSERT INTO public.accounts (user_id, account_number, account_type, balance, currency, status)
SELECT u.user_id, 'SB1000000003', 'Savings', 15000.0000, 'INR', 'Active'
FROM public.users u
WHERE u.username = 'john_doe'
ON CONFLICT (account_number) DO NOTHING;

COMMIT;
