import unittest
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.app.config import settings
from backend.app.dependencies import get_current_user, require_admin
from backend.app.tokens import create_access_token


test_app = FastAPI()


@test_app.get("/protected")
def protected_route(user: dict = Depends(get_current_user)):
    return user


@test_app.get("/admin")
def admin_route(user: dict = Depends(require_admin)):
    return {"message": "Admin access granted", "user": user}


client = TestClient(test_app)


class TestAuthenticationDependencies(unittest.TestCase):

    def token_for(self, user_id=1010, username="test_customer", role="Customer"):
        return create_access_token(user_id, username, role)

    def test_missing_token_returns_401(self):
        response = client.get("/protected")
        self.assertEqual(response.status_code, 401)

    def test_invalid_token_returns_401(self):
        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid.token.value"},
        )
        self.assertEqual(response.status_code, 401)

    def test_valid_customer_token_returns_identity(self):
        token = self.token_for()

        response = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_id"], 1010)
        self.assertEqual(response.json()["username"], "test_customer")
        self.assertEqual(response.json()["role"], "Customer")

    def test_expired_token_returns_401(self):
        now = datetime.now(timezone.utc)

        payload = {
            "sub": "1010",
            "username": "test_customer",
            "role": "Customer",
            "iat": now - timedelta(minutes=10),
            "exp": now - timedelta(minutes=5),
        }

        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        response = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 401)

    def test_customer_cannot_access_admin_route(self):
        token = self.token_for(role="Customer")

        response = client.get(
            "/admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_admin_route(self):
        token = self.token_for(role="Admin")

        response = client.get(
            "/admin",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Admin access granted")


if __name__ == "__main__":
    unittest.main()
