from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.dependencies import get_current_user, require_admin
from backend.app.postgres import get_postgres_connection


router = APIRouter(prefix="/accounts", tags=["Accounts"])


def mask_account_number(account_number: str) -> str:
    """Show only the last four digits of an account number."""
    return "*" * max(0, len(account_number) - 4) + account_number[-4:]


def format_account(row: tuple) -> dict:
    """Convert a database account row into a safe API response."""
    (
        account_id,
        account_number,
        account_type,
        balance,
        currency,
        account_status,
    ) = row

    return {
        "account_id": account_id,
        "account_number": mask_account_number(account_number),
        "account_type": account_type,
        "balance": str(Decimal(balance)),
        "currency": currency,
        "status": account_status,
    }


def require_customer(current_user: dict) -> None:
    if current_user["role"] != "Customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required",
        )


@router.get("/me")
def get_my_accounts(
    current_user: dict = Depends(get_current_user),
):
    require_customer(current_user)

    with get_postgres_connection() as connection:
        rows = connection.execute(
            """
            SELECT account_id, account_number, account_type,
                   balance, currency, status
            FROM public.accounts
            WHERE user_id = %s
            ORDER BY account_id
            """,
            (current_user["user_id"],),
        ).fetchall()

    return {
        "accounts": [format_account(row) for row in rows],
        "count": len(rows),
    }


@router.get("/{account_id}")
def get_account(
    account_id: int,
    current_user: dict = Depends(get_current_user),
):
    require_customer(current_user)

    if account_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    with get_postgres_connection() as connection:
        row = connection.execute(
            """
            SELECT account_id, account_number, account_type,
                   balance, currency, status
            FROM public.accounts
            WHERE account_id = %s AND user_id = %s
            """,
            (account_id, current_user["user_id"]),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    return {"account": format_account(row)}


@router.get("/admin/all")
def get_all_accounts(
    current_user: dict = Depends(require_admin),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    with get_postgres_connection() as connection:
        rows = connection.execute(
            """
            SELECT account_id, account_number, account_type,
                   balance, currency, status
            FROM public.accounts
            ORDER BY account_id
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        ).fetchall()

        total = connection.execute(
            "SELECT COUNT(*) FROM public.accounts"
        ).fetchone()[0]

    return {
        "accounts": [format_account(row) for row in rows],
        "count": len(rows),
        "total": total,
        "limit": limit,
        "offset": offset,
    }
