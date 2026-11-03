from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

from backend.app.tokens import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    """Verify the JWT and return the authenticated user's identity."""

    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    try:
        payload = decode_access_token(credentials.credentials)

        user_id = int(payload["sub"])
        username = payload["username"]
        role = payload["role"]

        if user_id <= 0:
            raise unauthorized

        if not isinstance(username, str) or not username.strip():
            raise unauthorized

        if role not in ("Admin", "Customer"):
            raise unauthorized

        return {
            "user_id": user_id,
            "username": username,
            "role": role,
        }

    except (InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorized


def require_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Allow access only to authenticated administrators."""

    if current_user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    return current_user
