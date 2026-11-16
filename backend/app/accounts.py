import random
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.app.dependencies import get_current_user, require_admin
from backend.app.postgres import get_postgres_connection


router = APIRouter(prefix="/accounts", tags=["Accounts"])


class OpenAccountRequest(BaseModel):
    account_type: str = Field(default="Savings", description="Savings, Checking, Investment, Business")
    initial_balance: Decimal = Field(default=Decimal("1000.00"), ge=0, max_digits=19, decimal_places=4)
    currency: str = Field(default="INR", max_length=3)


class AccountStatusRequest(BaseModel):
    status: str = Field(..., description="Active, Frozen, Closed")


def mask_account_number(account_number: str) -> str:
    """Show only the last four digits of an account number."""
    return "*" * max(0, len(account_number) - 4) + account_number[-4:]


def format_account(row: tuple, mask: bool = True) -> dict:
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
        "account_number": mask_account_number(account_number) if mask else account_number,
        "raw_account_number": account_number,
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


@router.post("/open", status_code=status.HTTP_201_CREATED)
def open_new_account(
    request: OpenAccountRequest,
    current_user: dict = Depends(get_current_user),
):
    require_customer(current_user)

    acc_num = f"SBIN{random.randint(1000000000, 9999999999)}"

    with get_postgres_connection() as connection:
        try:
            row = connection.execute(
                """
                SELECT account_id, user_id, account_number, account_type, balance, currency, status
                FROM public.open_account(%s, %s, %s, %s, %s)
                """,
                (
                    current_user["user_id"],
                    acc_num,
                    request.account_type,
                    request.initial_balance,
                    request.currency,
                ),
            ).fetchone()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to open account: {str(exc)}",
            )

    return {
        "message": f"Successfully opened new {request.account_type} account",
        "account": {
            "account_id": row[0],
            "user_id": row[1],
            "account_number": row[2],
            "account_type": row[3],
            "balance": str(Decimal(row[4])),
            "currency": row[5],
            "status": row[6],
        },
    }


@router.get("/recipients")
def get_transfer_recipients(current_user: dict = Depends(get_current_user)):
    """Returns all active customer accounts across the bank for transfers."""
    require_customer(current_user)

    with get_postgres_connection() as connection:
        rows = connection.execute(
            """
            SELECT account_id, account_number, account_type, owner_username
            FROM public.get_transfer_recipients();
            """
        ).fetchall()

    recipients = []
    for r in rows:
        recipients.append({
            "account_id": r[0],
            "account_number": r[1],
            "account_type": r[2],
            "owner_username": r[3],
        })

    return {"recipients": recipients}


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


@router.patch("/{account_id}/status")
def update_account_status(
    account_id: int,
    request: AccountStatusRequest,
    current_user: dict = Depends(require_admin),
):
    """Admin function to Freeze, Unfreeze, or Close an account."""
    with get_postgres_connection() as connection:
        try:
            connection.execute(
                "SELECT public.set_account_status(%s, %s)",
                (account_id, request.status)
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to update account status: {str(exc)}"
            )

    return {
        "message": f"Account {account_id} status updated to {request.status}",
        "account_id": account_id,
        "status": request.status,
    }


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
        "accounts": [format_account(row, mask=False) for row in rows],
        "count": len(rows),
        "total": total,
        "limit": limit,
        "offset": offset,
    }
