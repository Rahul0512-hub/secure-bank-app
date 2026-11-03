import psycopg
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from backend.app.config import settings
from backend.app.postgres import get_postgres_connection
from backend.app.security import hash_password, verify_password
from backend.app.tokens import create_access_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1)


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

    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Customer registration failed",
        )

    user_id, username, email, phone, role, created_at = customer

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
def login(request: LoginRequest):
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id, username, password_hash, role = user

    access_token = create_access_token(
        user_id=user_id,
        username=username,
        role=role,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
