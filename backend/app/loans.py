import math
from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.app.dependencies import get_current_user, require_admin
from backend.app.postgres import get_postgres_connection


router = APIRouter(prefix="/loans", tags=["Loans"])


class ApplyLoanRequest(BaseModel):
    loan_amount: Decimal = Field(gt=0, max_digits=19, decimal_places=4)
    interest_rate: Decimal = Field(default=Decimal("8.5000"), ge=0, max_digits=7, decimal_places=4)
    tenure_months: int = Field(default=24, ge=1, le=360)


class CalculateEMIRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    tenure_months: int = Field(ge=1, le=360)


class UpdateLoanStatusRequest(BaseModel):
    status: str = Field(..., description="Pending, Approved, Rejected, Active, Paid, Defaulted")


def require_customer(current_user: dict) -> None:
    if current_user["role"] != "Customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer access required",
        )


def calculate_emi_values(principal: float, annual_rate: float, tenure_months: int) -> dict:
    if annual_rate == 0:
        monthly_emi = principal / tenure_months
        total_payment = principal
        total_interest = 0.0
    else:
        monthly_r = (annual_rate / 100) / 12
        factor = math.pow(1 + monthly_r, tenure_months)
        monthly_emi = principal * monthly_r * factor / (factor - 1)
        total_payment = monthly_emi * tenure_months
        total_interest = total_payment - principal

    return {
        "monthly_emi": round(monthly_emi, 2),
        "total_principal": round(principal, 2),
        "total_interest": round(total_interest, 2),
        "total_payable": round(total_payment, 2),
    }


def format_loan(row: tuple) -> dict:
    (
        loan_id,
        user_id,
        loan_amount,
        interest_rate,
        loan_status,
        start_date,
        end_date,
    ) = row

    # Calculate estimated EMI
    months = 24
    if start_date and end_date:
        delta_days = (end_date - start_date).days
        months = max(1, round(delta_days / 30.4))

    emi_info = calculate_emi_values(float(loan_amount), float(interest_rate), months)

    return {
        "loan_id": loan_id,
        "user_id": user_id,
        "loan_amount": str(Decimal(loan_amount)),
        "interest_rate": f"{float(interest_rate):.2f}%",
        "status": loan_status,
        "start_date": str(start_date) if start_date else None,
        "end_date": str(end_date) if end_date else None,
        "tenure_months": months,
        "monthly_emi": emi_info["monthly_emi"],
        "total_payable": emi_info["total_payable"],
    }


@router.post("/calculator")
def calculate_loan_emi(request: CalculateEMIRequest):
    """Utility endpoint to calculate monthly EMI and loan amortization projections."""
    return calculate_emi_values(request.principal, request.annual_rate, request.tenure_months)


@router.get("/me")
def get_my_loans(current_user: dict = Depends(get_current_user)):
    """Retrieve all loans associated with the logged-in customer."""
    require_customer(current_user)

    with get_postgres_connection() as connection:
        rows = connection.execute(
            """
            SELECT loan_id, user_id, loan_amount, interest_rate, status, start_date, end_date
            FROM public.loans
            WHERE user_id = %s
            ORDER BY loan_id DESC
            """,
            (current_user["user_id"],),
        ).fetchall()

    return {
        "loans": [format_loan(row) for row in rows],
        "count": len(rows),
    }


@router.post("/apply", status_code=status.HTTP_201_CREATED)
def apply_for_loan(
    request: ApplyLoanRequest,
    current_user: dict = Depends(get_current_user),
):
    """Apply for a new bank loan."""
    require_customer(current_user)

    start_date = date.today()
    end_date = start_date + timedelta(days=request.tenure_months * 30)

    with get_postgres_connection() as connection:
        try:
            row = connection.execute(
                """
                SELECT loan_id, user_id, loan_amount, interest_rate, status, start_date, end_date
                FROM public.apply_loan(%s, %s, %s, %s, %s)
                """,
                (
                    current_user["user_id"],
                    request.loan_amount,
                    request.interest_rate,
                    start_date,
                    end_date,
                ),
            ).fetchone()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Loan application could not be processed: {str(exc)}",
            )

    return {
        "message": "Loan application submitted successfully and pending approval",
        "loan": format_loan(row),
    }


@router.get("/admin/all")
def get_all_loans(
    current_user: dict = Depends(require_admin),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Bank Admin view of all customer loan applications."""
    with get_postgres_connection() as connection:
        rows = connection.execute(
            """
            SELECT loan_id, user_id, loan_amount, interest_rate, status, start_date, end_date
            FROM public.loans
            ORDER BY loan_id DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        ).fetchall()

        total = connection.execute("SELECT COUNT(*) FROM public.loans").fetchone()[0]

    return {
        "loans": [format_loan(row) for row in rows],
        "count": len(rows),
        "total": total,
    }


@router.patch("/{loan_id}/status")
def update_loan_status(
    loan_id: int,
    request: UpdateLoanStatusRequest,
    current_user: dict = Depends(require_admin),
):
    """Bank Admin approve, reject, or update status of a loan."""
    with get_postgres_connection() as connection:
        try:
            connection.execute(
                "SELECT public.update_loan_status(%s, %s)",
                (loan_id, request.status)
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to update loan: {str(exc)}"
            )

    return {
        "message": f"Loan {loan_id} status updated to {request.status}",
        "loan_id": loan_id,
        "status": request.status,
    }
