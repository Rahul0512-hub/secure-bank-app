import psycopg
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from backend.app.config import settings
from backend.app.dependencies import get_current_user, require_admin
from backend.app.mongodb import get_fraud_alerts_collection, get_login_events_collection, get_mongo_client
from backend.app.postgres import get_postgres_connection
from backend.app.security import hash_password, verify_password
from backend.app.tokens import create_access_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    initial_deposit: float = Field(default=5000.0, ge=0)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1)


def log_login_event_safe(email: str, status_str: str, client_ip: str = "127.0.0.1", user_id: int | None = None):
    """Safely records authentication events to MongoDB without disrupting authentication flow."""
    try:
        from datetime import datetime, timezone
        client = get_mongo_client()
        login_col = get_login_events_collection(client)
        now = datetime.now(timezone.utc)

        login_col.insert_one({
            "user_id": user_id,
            "email": email,
            "ip_address": client_ip,
            "user_agent": "SecureBank-Web-Client",
            "status": status_str,
            "occurred_at": now,
        })

        if status_str == "FAILED":
            recent_fails = login_col.count_documents({"email": email, "status": "FAILED"})
            if recent_fails >= 3:
                fraud_col = get_fraud_alerts_collection(client)
                fraud_col.insert_one({
                    "transaction_id": None,
                    "user_id": user_id or 0,
                    "amount": 0.0,
                    "category": "Account Takeover",
                    "reason": f"Brute-force alert: {recent_fails} failed login attempts for {email}",
                    "severity": "CRITICAL",
                    "status": "OPEN",
                    "created_at": now,
                })
        client.close()
    except Exception:
        # Logging to MongoDB should never break authentication if Mongo is unavailable
        pass


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest):
    password_hash = hash_password(request.password)

    try:
        with get_postgres_connection() as connection:
            customer = connection.execute(
                """
                SELECT *
                FROM public.register_customer(%s, %s, %s, %s)
                """,
                (
                    request.username,
                    password_hash,
                    str(request.email),
                    request.phone,
                ),
            ).fetchone()

            if customer is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Customer registration failed",
                )

            user_id, username, email, phone, role, created_at = customer

    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )

    return {
        "message": "Customer registered successfully",
        "user": {
            "user_id": user_id,
            "username": username,
            "email": email,
            "phone": phone,
            "role": role,
            "created_at": created_at,
        },
    }


@router.post("/login")
def login(request: LoginRequest, req: Request = None):
    client_ip = "127.0.0.1"
    if req and req.client:
        client_ip = req.client.host

    # Retrieve only the matching user's authentication details.
    with get_postgres_connection() as connection:
        user = connection.execute(
            """
            SELECT user_id, username, password_hash, role
            FROM public.get_auth_user(%s)
            """,
            (request.username,),
        ).fetchone()

    # Use the same response for unknown users and incorrect passwords.
    if user is None or not verify_password(request.password, user[2]):
        log_login_event_safe(request.username, "FAILED", client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id, username, password_hash, role = user

    log_login_event_safe(username, "SUCCESS", client_ip, user_id=user_id)

    access_token = create_access_token(
        user_id=user_id,
        username=username,
        role=role,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "user_id": user_id,
            "username": username,
            "role": role,
        }
    }


@router.get("/me")
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Returns profile information for the authenticated user."""
    try:
        with get_postgres_connection() as connection:
            row = connection.execute(
                """
                SELECT user_id, username, email, phone, role, created_at
                FROM public.get_user_profile(%s)
                """,
                (current_user["user_id"],)
            ).fetchone()

            if row:
                return {
                    "user_id": row[0],
                    "username": row[1],
                    "email": row[2],
                    "phone": row[3],
                    "role": row[4],
                    "created_at": row[5],
                }
    except Exception:
        pass

    return {
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "role": current_user["role"],
        "email": f"{current_user['username']}@securebank.com",
    }


@router.get("/admin/users")
def list_all_users(current_user: dict = Depends(require_admin)):
    """Admin-only view of all registered banking users."""
    with get_postgres_connection() as connection:
        rows = connection.execute(
            """
            SELECT user_id, username, email, phone, role, created_at
            FROM public.get_all_users()
            """
        ).fetchall()

    users = []
    for r in rows:
        users.append({
            "user_id": r[0],
            "username": r[1],
            "email": r[2],
            "phone": r[3],
            "role": r[4],
            "created_at": r[5],
        })

    return {"users": users, "count": len(users)}
