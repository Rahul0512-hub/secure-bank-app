
CREATE OR REPLACE FUNCTION transfer_funds(
    p_source_account_id BIGINT,
    p_destination_account_id BIGINT,
    p_amount NUMERIC(19, 4),
    p_transaction_type VARCHAR(30),
    p_description TEXT DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
DECLARE
    v_source accounts%ROWTYPE;
    v_destination accounts%ROWTYPE;
    v_transaction_id BIGINT;
BEGIN
    -- Validate account IDs
    IF p_source_account_id = p_destination_account_id THEN
        RAISE EXCEPTION 'Source and destination accounts must be different';
    END IF;

    -- Validate transfer amount
    IF p_amount IS NULL OR p_amount <= 0 THEN
        RAISE EXCEPTION 'Transfer amount must be greater than zero';
    END IF;

    -- Validate transaction type
    IF p_transaction_type IS NULL OR TRIM(p_transaction_type) = '' THEN
        RAISE EXCEPTION 'Transaction type cannot be empty';
    END IF;

    -- Lock both accounts in a consistent order
    -- This helps prevent conflicting concurrent transfers.
    PERFORM account_id
    FROM accounts
    WHERE account_id IN (
        p_source_account_id,
        p_destination_account_id
    )
    ORDER BY account_id
    FOR UPDATE;

    -- Fetch source account
    SELECT *
    INTO v_source
    FROM accounts
    WHERE account_id = p_source_account_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Source account % does not exist',
            p_source_account_id;
    END IF;

    -- Fetch destination account
    SELECT *
    INTO v_destination
    FROM accounts
    WHERE account_id = p_destination_account_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Destination account % does not exist',
            p_destination_account_id;
    END IF;

    -- Check account status
    IF v_source.status <> 'Active' THEN
        RAISE EXCEPTION 'Source account is not active';
    END IF;

    IF v_destination.status <> 'Active' THEN
        RAISE EXCEPTION 'Destination account is not active';
    END IF;

    -- Check currency compatibility
    IF v_source.currency <> v_destination.currency THEN
        RAISE EXCEPTION 'Both accounts must use the same currency';
    END IF;

    -- Check available balance
    IF v_source.balance < p_amount THEN
        RAISE EXCEPTION 'Insufficient balance in source account';
    END IF;

    -- Debit source account
    UPDATE accounts
    SET balance = balance - p_amount
    WHERE account_id = p_source_account_id;

    -- Credit destination account
    UPDATE accounts
    SET balance = balance + p_amount
    WHERE account_id = p_destination_account_id;

    -- Record completed transaction
    INSERT INTO transactions (
        source_account_id,
        destination_account_id,
        amount,
        transaction_type,
        description,
        status
    )
    VALUES (
        p_source_account_id,
        p_destination_account_id,
        p_amount,
        p_transaction_type,
        p_description,
        'Completed'
    )
    RETURNING transaction_id INTO v_transaction_id;

    -- Record a completed transfer in the transactional audit outbox.
    INSERT INTO public.transaction_audit_outbox (
        transaction_id,
        event_type,
        payload
    )
    VALUES (
        v_transaction_id,
        'TRANSFER_COMPLETED',
        jsonb_build_object(
            'transaction_id', v_transaction_id,
            'event_type', 'TRANSFER_COMPLETED',
            'status', 'SUCCESS',
            'source_account_id', p_source_account_id,
            'destination_account_id', p_destination_account_id,
            'amount', p_amount,
            'currency', v_source.currency,
            'occurred_at', CURRENT_TIMESTAMP,
            'actor_user_id', v_source.user_id,
            'description', p_description
        )
    );

    RETURN v_transaction_id;
END;
$$;
